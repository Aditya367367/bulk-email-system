from django.urls import path
from .views import (
    UploadExcelView, StartEmailSendingView, EmailJobStatusView,
    DailyLimitView, EmailJobListView, PauseEmailSendingView,
    ResumeEmailSendingView, TerminateEmailSendingView
)

urlpatterns = [
    path('upload/', UploadExcelView.as_view(), name='upload-excel'),
    path('start/<uuid:job_id>/', StartEmailSendingView.as_view(), name='start-email-sending'),
    path('status/<uuid:job_id>/', EmailJobStatusView.as_view(), name='email-job-status'),
    path('pause/<uuid:job_id>/', PauseEmailSendingView.as_view(), name='pause-email-sending'),
    path('resume/<uuid:job_id>/', ResumeEmailSendingView.as_view(), name='resume-email-sending'),
    path('terminate/<uuid:job_id>/', TerminateEmailSendingView.as_view(), name='terminate-email-sending'),
    path('daily-limit/', DailyLimitView.as_view(), name='daily-limit'),
    path('jobs/', EmailJobListView.as_view(), name='email-job-list'),
]
