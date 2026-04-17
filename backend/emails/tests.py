from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from unittest.mock import patch
from kombu.exceptions import OperationalError
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from .models import EmailJob, EmailRecord, DailyEmailLimit
from .pdf_utils import PDFGenerator
from .views import StartEmailSendingView
import pandas as pd
import io
import os


class EmailJobModelTests(TestCase):
    def setUp(self):
        self.job = EmailJob.objects.create(
            total_count=10,
            sent_count=5,
            failed_count=2,
            pending_count=3
        )
    
    def test_progress_percentage(self):
        expected_percentage = (self.job.sent_count / self.job.total_count) * 100
        self.assertEqual(self.job.progress_percentage, expected_percentage)
    
    def test_progress_percentage_zero_total(self):
        job = EmailJob.objects.create(total_count=0)
        self.assertEqual(job.progress_percentage, 0)


class DailyEmailLimitTests(TestCase):
    def test_get_today_count(self):
        count = DailyEmailLimit.get_today_count()
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)
    
    def test_increment_today_count(self):
        initial_count = DailyEmailLimit.get_today_count()
        new_count = DailyEmailLimit.increment_today_count(5)
        self.assertEqual(new_count, initial_count + 5)


class EmailUploadTests(APITestCase):
    def setUp(self):
        # Create test Excel data
        data = {
            'ref_no': ['REF001', 'REF002'],
            'name': ['John Doe', 'Jane Smith'],
            'email': ['john@example.com', 'jane@example.com'],
            'company_name': ['John Corp', 'Jane Retail'],
            'address_line1': ['123 Main St', '456 Oak Ave'],
            'address_line2': ['Mumbai', 'Pune'],
        }
        df = pd.DataFrame(data)
        
        # Convert to Excel file
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        self.excel_file = SimpleUploadedFile(
            "test.xlsx",
            excel_buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    def test_upload_valid_excel(self):
        url = reverse('upload-excel')
        response = self.client.post(url, {'excel_file': self.excel_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('job_id', response.data)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(response.data['total_count'], 2)
        self.assertEqual(response.data['pending_count'], 2)
        self.assertEqual(response.data['total_emails'], 2)

        record = EmailRecord.objects.order_by('created_at').first()
        self.assertEqual(record.ref_no, 'REF001')
        self.assertEqual(record.company_name, 'John Corp')
        self.assertEqual(record.address_line1, '123 Main St')
        self.assertEqual(record.address_line2, 'Mumbai')
        self.assertEqual(record.email, 'john@example.com')
    
    def test_upload_invalid_file_type(self):
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"file content",
            content_type="text/plain"
        )
        
        url = reverse('upload-excel')
        response = self.client.post(url, {'excel_file': invalid_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('excel_file', response.data)
    
    def test_upload_missing_columns(self):
        # Create Excel with missing columns
        data = {'name': ['John Doe']}
        df = pd.DataFrame(data)
        
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        incomplete_file = SimpleUploadedFile(
            "incomplete.xlsx",
            excel_buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        url = reverse('upload-excel')
        response = self.client.post(url, {'excel_file': incomplete_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Missing required columns', response.data['error'])


class EmailJobStatusTests(APITestCase):
    def setUp(self):
        self.job = EmailJob.objects.create(
            total_count=5,
            sent_count=3,
            failed_count=1,
            pending_count=1
        )
        
        # Create some email records
        EmailRecord.objects.create(
            email_job=self.job,
            name='Test User',
            email='test@example.com',
            status='sent'
        )
        
        EmailRecord.objects.create(
            email_job=self.job,
            name='Failed User',
            email='failed@example.com',
            status='failed',
            error_message='SMTP Error'
        )
    
    def test_get_job_status(self):
        url = reverse('email-job-status', kwargs={'job_id': self.job.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_count'], 5)
        self.assertEqual(response.data['sent_count'], 3)
        self.assertEqual(response.data['failed_count'], 1)
        self.assertEqual(len(response.data['failed_records']), 1)
    
    def test_get_nonexistent_job_status(self):
        fake_uuid = '12345678-1234-5678-1234-567812345678'
        url = reverse('email-job-status', kwargs={'job_id': fake_uuid})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class EmailJobListTests(APITestCase):
    def test_get_jobs_is_paginated(self):
        for _ in range(12):
            EmailJob.objects.create(
                total_count=1,
                pending_count=1,
                excel_file='excel_files/test.xlsx',
            )

        url = reverse('email-job-list')
        response = self.client.get(url, {'page': 1, 'page_size': 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('total_pages', response.data)
        self.assertEqual(response.data['page'], 1)
        self.assertEqual(response.data['page_size'], 5)
        self.assertEqual(len(response.data['results']), 5)


class StartEmailSendingTests(APITestCase):
    @patch('emails.views.process_email_job.delay')
    def test_start_email_sending_returns_503_when_queue_is_down(self, mocked_delay):
        mocked_delay.side_effect = OperationalError('redis down')

        job = EmailJob.objects.create(
            total_count=1,
            pending_count=1,
            excel_file='excel_files/test.xlsx',
        )

        factory = APIRequestFactory()
        request = factory.post(f'/api/start/{job.id}/')
        response = StartEmailSendingView.as_view()(request, job_id=job.id)

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('Email queue is unavailable', response.data['error'])


class DailyLimitTests(APITestCase):
    def test_get_daily_limit(self):
        url = reverse('daily-limit')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('emails_sent', response.data)
        self.assertIn('remaining_emails', response.data)
        self.assertIn('daily_limit', response.data)

    def test_get_daily_limit_includes_warning_when_limit_is_hit(self):
        DailyEmailLimit.increment_today_count(100)

        url = reverse('daily-limit')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['remaining_emails'], 0)
        self.assertIn('warning_message', response.data)
        self.assertTrue(response.data['warning_message'])


class PDFGeneratorTests(TestCase):
    def test_generate_pdf_with_all_template_pages(self):
        record = EmailRecord(
            name='John Doe',
            email='john@example.com',
            ref_no='REF/2026/001',
            company_name='Doe Enterprises',
            address='123 Main St, Mumbai',
            address_line1='123 Main St',
            address_line2='Mumbai',
        )

        pdf_path = PDFGenerator().generate_pdf(record)

        self.assertIsNotNone(pdf_path)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 0)
