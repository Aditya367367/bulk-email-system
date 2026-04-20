from rest_framework import serializers
from .models import EmailJob, EmailRecord, DailyEmailLimit


class EmailRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailRecord
        fields = [
            'id', 'name', 'email', 'license_number', 'validity_from',
            'premises_type', 'category', 'address', 'ref_no', 'company_name',
            'address_line1', 'address_line2', 'custom_message', 'status', 
            'error_message', 'created_at', 'updated_at'
        ]


class EmailJobSerializer(serializers.ModelSerializer):
    email_records = EmailRecordSerializer(many=True, read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = EmailJob
        fields = [
            'id', 'status', 'total_count', 'sent_count', 'failed_count',
            'pending_count', 'progress_percentage', 'created_at', 'updated_at',
            'email_records', 'excel_file', 'celery_task_id'
        ]


class EmailJobStatusSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = EmailJob
        fields = [
            'id', 'status', 'total_count', 'sent_count', 'failed_count',
            'pending_count', 'progress_percentage', 'created_at', 'updated_at'
        ]


class DailyEmailLimitSerializer(serializers.ModelSerializer):
    remaining_emails = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyEmailLimit
        fields = ['date', 'emails_sent', 'remaining_emails', 'created_at', 'updated_at']
    
    def get_remaining_emails(self, obj):
        from django.conf import settings
        return max(0, settings.DAILY_EMAIL_LIMIT - obj.emails_sent)


class ExcelUploadSerializer(serializers.Serializer):
    excel_file = serializers.FileField()
    
    def validate_excel_file(self, value):
        if not value.name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError("Only Excel files (.xlsx, .xls) are allowed.")
        
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 10MB.")
        
        return value
