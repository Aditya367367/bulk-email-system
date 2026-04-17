# Django admin disabled due to Python 3.14 compatibility issues with Django 4.2.7
# The admin panel causes 'super' object has no attribute 'dicts' errors
# Use API endpoints for data management instead

# from django.contrib import admin
# from .models import EmailJob, EmailRecord, DailyEmailLimit
# 
# # Registration commented out to avoid compatibility issues
# # admin.site.register(EmailJob)
# # admin.site.register(EmailRecord) 
# # admin.site.register(DailyEmailLimit)
