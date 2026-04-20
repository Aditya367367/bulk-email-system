from django.urls import path
from .views import (
    UploadExcelView, StartEmailSendingView, EmailJobStatusView,
    DailyLimitView, EmailJobListView, PauseEmailSendingView,
    ResumeEmailSendingView, TerminateEmailSendingView, DeveloperInfoView
)
from .auth_views import login_view, refresh_token_view, logout_view, user_profile_view

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', login_view, name='login'),
    path('auth/refresh/', refresh_token_view, name='refresh-token'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/profile/', user_profile_view, name='user-profile'),
    
    # Email system endpoints
    path('upload/', UploadExcelView.as_view(), name='upload-excel'),
    path('start/<uuid:job_id>/', StartEmailSendingView.as_view(), name='start-email-sending'),
    path('status/<uuid:job_id>/', EmailJobStatusView.as_view(), name='email-job-status'),
    path('pause/<uuid:job_id>/', PauseEmailSendingView.as_view(), name='pause-email-sending'),
    path('resume/<uuid:job_id>/', ResumeEmailSendingView.as_view(), name='resume-email-sending'),
    path('terminate/<uuid:job_id>/', TerminateEmailSendingView.as_view(), name='terminate-email-sending'),
    path('daily-limit/', DailyLimitView.as_view(), name='daily-limit'),
    path('developer-info/', DeveloperInfoView.as_view(), name='developer-info'),
    path('jobs/', EmailJobListView.as_view(), name='email-job-list'),
]
