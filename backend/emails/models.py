from django.db import models
from django.utils import timezone
import uuid


class EmailJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('terminated', 'Terminated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_count = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    pending_count = models.IntegerField(default=0)
    excel_file = models.FileField(upload_to='excel_files/')
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"EmailJob {self.id} - {self.status}"
    
    @property
    def progress_percentage(self):
        if self.total_count == 0:
            return 0
        return (self.sent_count / self.total_count) * 100


class EmailRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('processing', 'Processing'),
    ]
    
    email_job = models.ForeignKey(EmailJob, on_delete=models.CASCADE, related_name='email_records')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    license_number = models.CharField(max_length=255, blank=True, null=True)
    validity_from = models.DateField(blank=True, null=True)
    premises_type = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # New fields for page1.html template
    ref_no = models.CharField(max_length=100, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    email_subject = models.CharField(max_length=255, blank=True, null=True)
    sender_email = models.EmailField(blank=True, null=True, help_text="Email address where this email came from")
    custom_message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.name} - {self.email} - {self.status}"


class DailyEmailLimit(models.Model):
    date = models.DateField(unique=True)
    emails_sent = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date} - {self.emails_sent} emails"
    
    @classmethod
    def get_today_count(cls):
        today = timezone.now().date()
        obj, created = cls.objects.get_or_create(
            date=today,
            defaults={'emails_sent': 0}
        )
        return obj.emails_sent
    
    @classmethod
    def increment_today_count(cls, count=1):
        today = timezone.now().date()
        obj, created = cls.objects.get_or_create(
            date=today,
            defaults={'emails_sent': count}
        )
        if not created:
            obj.emails_sent += count
            obj.save()
        return obj.emails_sent
