from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import EmailJob, EmailRecord, DailyEmailLimit
import pandas as pd
import io


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
            'name': ['John Doe', 'Jane Smith'],
            'email': ['john@example.com', 'jane@example.com'],
            'license_number': ['LIC001', 'LIC002'],
            'validity_from': ['2023-01-01', '2023-01-02'],
            'premises_type': ['Office', 'Shop'],
            'category': ['Commercial', 'Retail'],
            'address': ['123 Main St', '456 Oak Ave']
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
        self.assertEqual(response.data['total_emails'], 2)
    
    def test_upload_invalid_file_type(self):
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"file content",
            content_type="text/plain"
        )
        
        url = reverse('upload-excel')
        response = self.client.post(url, {'excel_file': invalid_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_upload_missing_columns(self):
        # Create Excel with missing columns
        data = {'name': ['John Doe'], 'email': ['john@example.com']}
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


class DailyLimitTests(APITestCase):
    def test_get_daily_limit(self):
        url = reverse('daily-limit')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('emails_sent', response.data)
        self.assertIn('remaining_emails', response.data)
        self.assertIn('daily_limit', response.data)
