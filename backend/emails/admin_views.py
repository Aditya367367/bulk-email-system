from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import EmailJob, EmailRecord, DailyEmailLimit
import os
import mimetypes

def is_staff_user(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff_user)
def admin_dashboard(request):
    """Custom admin dashboard"""
    context = {
        'total_jobs': EmailJob.objects.count(),
        'pending_jobs': EmailJob.objects.filter(status='pending').count(),
        'processing_jobs': EmailJob.objects.filter(status='processing').count(),
        'completed_jobs': EmailJob.objects.filter(status='completed').count(),
        'total_records': EmailRecord.objects.count(),
        'today_sent': DailyEmailLimit.objects.filter(date=timezone.now().date()).first(),
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
@user_passes_test(is_staff_user)
def email_jobs_list(request):
    """List and manage email jobs"""
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    jobs = EmailJob.objects.all()
    
    if search:
        jobs = jobs.filter(Q(id__icontains=search))
    
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    
    jobs = jobs.order_by('-created_at')
    
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'status_choices': EmailJob.STATUS_CHOICES,
    }
    return render(request, 'admin/email_jobs.html', context)

@login_required
@user_passes_test(is_staff_user)
def delete_email_job(request, job_id):
    """Delete email job and associated files"""
    if request.method == 'POST':
        job = get_object_or_404(EmailJob, id=job_id)
        
        # Delete associated file
        if job.excel_file and os.path.exists(job.excel_file.path):
            os.remove(job.excel_file.path)
        
        # Delete job (will also delete related records due to CASCADE)
        job.delete()
        messages.success(request, 'Email job deleted successfully')
    
    return redirect('admin_email_jobs')

@login_required
@user_passes_test(is_staff_user)
def email_records_list(request):
    """List and manage email records"""
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    records = EmailRecord.objects.all()
    
    if search:
        records = records.filter(
            Q(name__icontains=search) | 
            Q(email__icontains=search) | 
            Q(license_number__icontains=search)
        )
    
    if status_filter:
        records = records.filter(status=status_filter)
    
    records = records.select_related('email_job').order_by('-created_at')
    
    paginator = Paginator(records, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'status_choices': EmailRecord.STATUS_CHOICES,
    }
    return render(request, 'admin/email_records.html', context)

@login_required
@user_passes_test(is_staff_user)
def delete_email_record(request, record_id):
    """Delete email record"""
    if request.method == 'POST':
        record = get_object_or_404(EmailRecord, id=record_id)
        record.delete()
        messages.success(request, 'Email record deleted successfully')
    
    return redirect('admin_email_records')

@login_required
@user_passes_test(is_staff_user)
def daily_limits_list(request):
    """List and manage daily limits"""
    limits = DailyEmailLimit.objects.all().order_by('-date')
    
    paginator = Paginator(limits, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'admin/daily_limits.html', context)

@login_required
@user_passes_test(is_staff_user)
def reset_daily_limit(request, limit_id):
    """Reset daily limit to 0"""
    if request.method == 'POST':
        limit = get_object_or_404(DailyEmailLimit, id=limit_id)
        limit.emails_sent = 0
        limit.save()
        messages.success(request, 'Daily limit reset successfully')
    
    return redirect('admin_daily_limits')

@login_required
@user_passes_test(is_staff_user)
def delete_daily_limit(request, limit_id):
    """Delete daily limit"""
    if request.method == 'POST':
        limit = get_object_or_404(DailyEmailLimit, id=limit_id)
        limit.delete()
        messages.success(request, 'Daily limit deleted successfully')
    
    return redirect('admin_daily_limits')

@login_required
@user_passes_test(is_staff_user)
def download_excel_file(request, job_id):
    """Download Excel file for a job"""
    job = get_object_or_404(EmailJob, id=job_id)
    
    if job.excel_file and os.path.exists(job.excel_file.path):
        mime_type, _ = mimetypes.guess_type(job.excel_file.path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        with open(job.excel_file.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=mime_type)
        
        filename = os.path.basename(job.excel_file.path)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = os.path.getsize(job.excel_file.path)
        
        return response
    else:
        messages.error(request, 'File not found')
        return redirect('admin_email_jobs')

@login_required
@user_passes_test(is_staff_user)
def delete_excel_file(request, job_id):
    """Delete Excel file but keep the job"""
    if request.method == 'POST':
        job = get_object_or_404(EmailJob, id=job_id)
        
        if job.excel_file and os.path.exists(job.excel_file.path):
            os.remove(job.excel_file.path)
            job.excel_file = None
            job.save()
            messages.success(request, 'Excel file deleted successfully')
        else:
            messages.error(request, 'File not found')
    
    return redirect('admin_email_jobs')

@login_required
@user_passes_test(is_staff_user)
def admin_logout(request):
    """Custom logout view for admin panel"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('/admin/')
