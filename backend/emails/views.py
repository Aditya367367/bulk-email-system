import pandas as pd
from kombu.exceptions import OperationalError
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.core.paginator import EmptyPage, Paginator
from django.utils import timezone
from .models import EmailJob, EmailRecord, DailyEmailLimit
from .serializers import (
    EmailJobSerializer, EmailJobStatusSerializer, 
    DailyEmailLimitSerializer, ExcelUploadSerializer
)
from .tasks import process_email_job


def _clean_excel_value(row, column_name, default=''):
    if column_name not in row or pd.isna(row[column_name]):
        return default
    return str(row[column_name]).strip()


LIMIT_HIT_WARNING = (
    'Daily email limit has been reached. Uploading more files today is blocked to protect sender reputation and help prevent email blacklisting.'
)


class UploadExcelView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = ExcelUploadSerializer(data=request.data)
        if serializer.is_valid():
            excel_file = serializer.validated_data['excel_file']
            
            try:
                # Read Excel file
                df = pd.read_excel(excel_file)
                
                # Validate required columns
                required_columns = [
                    'ref_no',
                    'name',
                    'email',
                    'company_name',
                    'address_line1',
                    'address_line2',
                ]
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    return Response({
                        'error': f'Missing required columns: {", ".join(missing_columns)}',
                        'required_columns': required_columns
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check row limit
                if len(df) > settings.DAILY_EMAIL_LIMIT:
                    return Response({
                        'error': f'Excel file contains {len(df)} rows. Maximum allowed is {settings.DAILY_EMAIL_LIMIT} rows.',
                        'warning_message': LIMIT_HIT_WARNING,
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check daily limit
                today_sent = DailyEmailLimit.get_today_count()
                if today_sent + len(df) > settings.DAILY_EMAIL_LIMIT:
                    remaining = settings.DAILY_EMAIL_LIMIT - today_sent
                    return Response({
                        'error': f'Daily email limit exceeded. You can send only {remaining} more emails today.',
                        'today_sent': today_sent,
                        'daily_limit': settings.DAILY_EMAIL_LIMIT,
                        'remaining': remaining,
                        'warning_message': LIMIT_HIT_WARNING,
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create EmailJob
                email_job = EmailJob.objects.create(
                    total_count=len(df),
                    pending_count=len(df),
                    excel_file=excel_file
                )
                
                # Create EmailRecords
                email_records = []
                for index, row in df.iterrows():
                    record = EmailRecord(
                        email_job=email_job,
                        ref_no=_clean_excel_value(row, 'ref_no'),
                        name=_clean_excel_value(row, 'name'),
                        email=_clean_excel_value(row, 'email'),
                        company_name=_clean_excel_value(row, 'company_name'),
                        address_line1=_clean_excel_value(row, 'address_line1'),
                        address_line2=_clean_excel_value(row, 'address_line2'),
                        license_number=_clean_excel_value(row, 'license_number'),
                        validity_from=(
                            pd.to_datetime(row['validity_from']).date()
                            if 'validity_from' in row and pd.notna(row['validity_from'])
                            else None
                        ),
                        premises_type=_clean_excel_value(row, 'premises_type'),
                        category=_clean_excel_value(row, 'category'),
                        address=_clean_excel_value(
                            row,
                            'address',
                            ', '.join(filter(None, [
                                _clean_excel_value(row, 'address_line1'),
                                _clean_excel_value(row, 'address_line2'),
                            ])),
                        ),
                    )
                    email_records.append(record)
                
                EmailRecord.objects.bulk_create(email_records)
                job_data = EmailJobStatusSerializer(email_job).data
                
                return Response({
                    **job_data,
                    'message': 'Excel file uploaded successfully',
                    'id': str(email_job.id),
                    'job_id': str(email_job.id),
                    'total_emails': len(df),
                    'daily_limit': settings.DAILY_EMAIL_LIMIT,
                    'today_sent': today_sent,
                    'remaining_today': settings.DAILY_EMAIL_LIMIT - today_sent,
                    'failed_records': [],
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Error processing Excel file: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StartEmailSendingView(APIView):
    def post(self, request, job_id):
        try:
            email_job = EmailJob.objects.get(id=job_id)
            
            if email_job.status != 'pending':
                return Response({
                    'error': f'Cannot start job. Current status: {email_job.status}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check daily limit again
            today_sent = DailyEmailLimit.get_today_count()
            if today_sent + email_job.pending_count > settings.DAILY_EMAIL_LIMIT:
                remaining = settings.DAILY_EMAIL_LIMIT - today_sent
                return Response({
                    'error': f'Daily email limit exceeded. You can send only {remaining} more emails today.',
                    'today_sent': today_sent,
                    'daily_limit': settings.DAILY_EMAIL_LIMIT,
                    'remaining': remaining,
                    'warning_message': LIMIT_HIT_WARNING,
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Start Celery task
            task = process_email_job.delay(str(email_job.id))
            email_job.celery_task_id = task.id
            email_job.status = 'processing'
            email_job.save()
            job_data = EmailJobStatusSerializer(email_job).data
            
            return Response({
                **job_data,
                'message': 'Email sending started',
                'id': str(email_job.id),
                'job_id': str(email_job.id),
                'task_id': task.id,
                'total_emails': email_job.total_count,
                'failed_records': [],
            }, status=status.HTTP_200_OK)

        except OperationalError:
            return Response({
                'error': 'Email queue is unavailable. Start Redis and the Celery worker, then try again.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except EmailJob.DoesNotExist:
            return Response({
                'error': 'Email job not found'
            }, status=status.HTTP_404_NOT_FOUND)


class EmailJobStatusView(APIView):
    def get(self, request, job_id):
        try:
            email_job = EmailJob.objects.get(id=job_id)
            serializer = EmailJobStatusSerializer(email_job)
            
            # Get email records with errors
            failed_records = EmailRecord.objects.filter(
                email_job=email_job, 
                status='failed'
            ).values('name', 'email', 'error_message')
            
            return Response({
                **serializer.data,
                'failed_records': list(failed_records)
            }, status=status.HTTP_200_OK)
            
        except EmailJob.DoesNotExist:
            return Response({
                'error': 'Email job not found'
            }, status=status.HTTP_404_NOT_FOUND)


class DailyLimitView(APIView):
    def get(self, request):
        today = timezone.now().date()
        daily_limit_obj, created = DailyEmailLimit.objects.get_or_create(
            date=today,
            defaults={'emails_sent': 0}
        )
        
        serializer = DailyEmailLimitSerializer(daily_limit_obj)
        return Response({
            **serializer.data,
            'daily_limit': settings.DAILY_EMAIL_LIMIT,
            'warning_message': LIMIT_HIT_WARNING if serializer.data['remaining_emails'] == 0 else '',
        }, status=status.HTTP_200_OK)


class DeveloperInfoView(APIView):
    def get(self, request):
        return Response(settings.DEVELOPER_INFO, status=status.HTTP_200_OK)


class PauseEmailSendingView(APIView):
    def post(self, request, job_id):
        try:
            email_job = EmailJob.objects.get(id=job_id)
            
            if email_job.status not in ['processing', 'paused']:
                return Response({
                    'error': f'Cannot pause job. Current status: {email_job.status}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            email_job.status = 'paused'
            email_job.save()
            
            return Response({
                'message': 'Email sending paused',
                'job_id': str(email_job.id),
                'status': email_job.status
            }, status=status.HTTP_200_OK)
            
        except EmailJob.DoesNotExist:
            return Response({
                'error': 'Email job not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ResumeEmailSendingView(APIView):
    def post(self, request, job_id):
        try:
            email_job = EmailJob.objects.get(id=job_id)
            
            if email_job.status != 'paused':
                return Response({
                    'error': f'Cannot resume job. Current status: {email_job.status}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            email_job.status = 'processing'
            email_job.save()
            
            return Response({
                'message': 'Email sending resumed',
                'job_id': str(email_job.id),
                'status': email_job.status
            }, status=status.HTTP_200_OK)
            
        except EmailJob.DoesNotExist:
            return Response({
                'error': 'Email job not found'
            }, status=status.HTTP_404_NOT_FOUND)


class TerminateEmailSendingView(APIView):
    def post(self, request, job_id):
        try:
            email_job = EmailJob.objects.get(id=job_id)
            
            if email_job.status not in ['processing', 'paused', 'pending']:
                return Response({
                    'error': f'Cannot terminate job. Current status: {email_job.status}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            email_job.status = 'terminated'
            email_job.save()
            
            # Update all pending email records to terminated status
            EmailRecord.objects.filter(
                email_job=email_job, 
                status='pending'
            ).update(status='terminated')
            
            # Cancel Celery task if it's running
            if email_job.celery_task_id:
                try:
                    from celery import current_app
                    current_app.control.revoke(email_job.celery_task_id, terminate=True)
                except Exception as e:
                    print(f"Error revoking Celery task: {e}")
            
            return Response({
                'message': 'Email sending terminated',
                'job_id': str(email_job.id),
                'status': email_job.status,
                'sent_count': email_job.sent_count,
                'failed_count': email_job.failed_count
            }, status=status.HTTP_200_OK)
            
        except EmailJob.DoesNotExist:
            return Response({
                'error': 'Email job not found'
            }, status=status.HTTP_404_NOT_FOUND)


class EmailJobListView(APIView):
    def get(self, request):
        page_number = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)

        try:
            page_number = max(int(page_number), 1)
        except (TypeError, ValueError):
            page_number = 1

        try:
            page_size = max(min(int(page_size), 50), 1)
        except (TypeError, ValueError):
            page_size = 10

        jobs = EmailJob.objects.all().order_by('-created_at')
        paginator = Paginator(jobs, page_size)

        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages if paginator.num_pages else 1)

        serializer = EmailJobStatusSerializer(page_obj.object_list, many=True)
        current_page = page_obj.number

        return Response({
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'page': current_page,
            'page_size': page_size,
            'next': current_page + 1 if page_obj.has_next() else None,
            'previous': current_page - 1 if page_obj.has_previous() else None,
            'results': serializer.data,
        }, status=status.HTTP_200_OK)
