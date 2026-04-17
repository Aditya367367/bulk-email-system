import os
import time
import tempfile
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from weasyprint import HTML, CSS
from PIL import Image
import io
from .models import EmailJob, EmailRecord, DailyEmailLimit
from .pdf_utils import PDFGenerator


@shared_task(bind=True, max_retries=3)
def process_email_job(self, job_id):
    try:
        email_job = EmailJob.objects.get(id=job_id)
        email_job.status = 'processing'
        email_job.save()
        
        while True:
            # Refresh job status to check for pause/terminate
            email_job.refresh_from_db()
            
            if email_job.status == 'terminated':
                # Mark all remaining pending records as terminated
                EmailRecord.objects.filter(
                    email_job=email_job, 
                    status='pending'
                ).update(status='terminated')
                return f'Email job terminated by user. Sent: {email_job.sent_count}, Failed: {email_job.failed_count}'
            
            if email_job.status == 'paused':
                time.sleep(5)  # Wait 5 seconds and check again
                continue
            
            if email_job.status != 'processing':
                break
            
            # Get next pending record
            try:
                record = EmailRecord.objects.filter(
                    email_job=email_job, 
                    status='pending'
                ).order_by('created_at').first()
                
                if not record:
                    break  # No more records to process
                
                # Check daily limit before each email
                today_sent = DailyEmailLimit.get_today_count()
                if today_sent >= settings.DAILY_EMAIL_LIMIT:
                    email_job.status = 'failed'
                    email_job.save()
                    return f'Daily email limit reached. Stopped at {today_sent} emails.'
                
                # Update record status to processing
                record.status = 'processing'
                record.save()
                
                # Generate PDF
                pdf_generator = PDFGenerator()
                pdf_path = pdf_generator.generate_pdf(record)
                
                if pdf_path:
                    record.pdf_file = pdf_path
                    record.save()
                    
                    # Send email
                    success = send_email_with_pdf(record, pdf_path)
                    
                    if success:
                        record.status = 'sent'
                        record.error_message = None
                        email_job.sent_count += 1
                        DailyEmailLimit.increment_today_count(1)
                    else:
                        record.status = 'failed'
                        record.error_message = 'Failed to send email'
                        email_job.failed_count += 1
                else:
                    record.status = 'failed'
                    record.error_message = 'Failed to generate PDF'
                    email_job.failed_count += 1
                
                email_job.pending_count -= 1
                email_job.save()
                record.save()
                
                # Add delay between emails to avoid spam
                time.sleep(7)  # 7 seconds delay
                
            except Exception as e:
                record.status = 'failed'
                record.error_message = str(e)
                record.save()
                email_job.failed_count += 1
                email_job.pending_count -= 1
                email_job.save()
        
        # Update final job status
        email_job.refresh_from_db()
        if email_job.status not in ['terminated', 'paused']:
            if email_job.failed_count == 0:
                email_job.status = 'completed'
            else:
                email_job.status = 'completed_with_errors'
            email_job.save()
        
        return f'Email job completed. Sent: {email_job.sent_count}, Failed: {email_job.failed_count}'
        
    except EmailJob.DoesNotExist:
        return f'Email job {job_id} not found'
    except Exception as e:
        # Retry logic
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        # Mark job as failed if max retries exceeded
        try:
            email_job = EmailJob.objects.get(id=job_id)
            email_job.status = 'failed'
            email_job.save()
        except EmailJob.DoesNotExist:
            pass
        
        return f'Email job failed: {str(e)}'


def send_email_with_pdf(record, pdf_path):
    try:
        subject = 'License Certificate - Important Document'
        
        # Create email message
        email = EmailMessage(
            subject=subject,
            body=f'''
Dear {record.name},

Please find attached your license certificate document.

License Number: {record.license_number}
Validity From: {record.validity_from}
Premises Type: {record.premises_type}
Category: {record.category}

If you have any questions, please contact us.

Best regards,
License Department
            '''.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[record.email]
        )
        
        # Attach PDF
        email.attach_file(pdf_path)
        
        # Send email
        email.send()
        
        return True
        
    except Exception as e:
        print(f"Error sending email to {record.email}: {str(e)}")
        return False


@shared_task
def cleanup_old_files():
    """Clean up old PDF files and temporary files"""
    from django.core.files.storage import default_storage
    from datetime import timedelta
    
    # Delete PDF files older than 7 days
    cutoff_date = timezone.now() - timedelta(days=7)
    
    old_records = EmailRecord.objects.filter(
        created_at__lt=cutoff_date,
        pdf_file__isnull=False
    )
    
    for record in old_records:
        if record.pdf_file and default_storage.exists(record.pdf_file.name):
            default_storage.delete(record.pdf_file.name)
        record.pdf_file = None
        record.save()
    
    return f'Cleaned up {old_records.count()} old PDF files'
