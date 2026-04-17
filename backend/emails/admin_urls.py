from django.urls import path
from . import admin_views

urlpatterns = [
    path('', admin_views.admin_dashboard, name='admin_dashboard'),
    path('email-jobs/', admin_views.email_jobs_list, name='admin_email_jobs'),
    path('email-jobs/delete/<uuid:job_id>/', admin_views.delete_email_job, name='admin_delete_job'),
    path('email-jobs/download/<uuid:job_id>/', admin_views.download_excel_file, name='admin_download_file'),
    path('email-jobs/delete-file/<uuid:job_id>/', admin_views.delete_excel_file, name='admin_delete_file'),
    path('email-records/', admin_views.email_records_list, name='admin_email_records'),
    path('email-records/delete/<int:record_id>/', admin_views.delete_email_record, name='admin_delete_record'),
    path('daily-limits/', admin_views.daily_limits_list, name='admin_daily_limits'),
    path('logout/', admin_views.admin_logout, name='admin_logout'),
]
