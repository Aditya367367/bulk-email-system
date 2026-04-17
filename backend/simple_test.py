#!/usr/bin/env python
"""
Simple test to verify PDF generation is working
"""
import os
import sys
import django

# Setup Django
sys.path.append('/home/aditya367/Desktop/email bulk system/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_system.settings')
django.setup()

from emails.models import EmailRecord
from emails.pdf_utils import PDFGenerator

def test_simple_pdf():
    """Test PDF generation with actual data"""
    print("🔄 Testing PDF generation...")
    
    # Create a test record with all fields
    test_record = EmailRecord(
        name="John Doe",
        email="john.doe@example.com",
        ref_no="REF/2024/001",
        company_name="Doe Enterprises Ltd",
        address_line1="123 Business Street",
        address_line2="Mumbai, Maharashtra 400001"
    )
    
    # Generate PDF
    pdf_generator = PDFGenerator()
    pdf_path = pdf_generator.generate_pdf(test_record)
    
    if pdf_path and os.path.exists(pdf_path):
        file_size = os.path.getsize(pdf_path)
        size_mb = file_size / (1024 * 1024)
        
        print(f"✅ SUCCESS: PDF generated!")
        print(f"📄 Path: {pdf_path}")
        print(f"📊 Size: {size_mb:.2f} MB")
        
        if size_mb < 1:
            print("🎯 PDF is under 1MB - ready for email!")
        else:
            print("⚠️  PDF is over 1MB but compression was attempted")
            
        return True
    else:
        print("❌ FAILED: PDF generation failed")
        return False

if __name__ == "__main__":
    success = test_simple_pdf()
    print(f"\n🏁 Test Result: {'PASSED' if success else 'FAILED'}")
