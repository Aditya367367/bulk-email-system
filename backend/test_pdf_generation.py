#!/usr/bin/env python
"""
Test script for multi-page PDF generation
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

def test_pdf_generation():
    """Test the new multi-page PDF generation"""
    print("Testing multi-page PDF generation...")
    
    # Create a test record
    test_record = EmailRecord(
        name="Test User",
        email="test@example.com",
        ref_no="REF/2024/001",
        company_name="Test Company Ltd",
        address_line1="123 Test Street",
        address_line2="Test City, 12345"
    )
    
    # Generate PDF
    pdf_generator = PDFGenerator()
    pdf_path = pdf_generator.generate_pdf(test_record)
    
    if pdf_path:
        print(f"✅ PDF generated successfully: {pdf_path}")
        
        # Check file size
        file_size = os.path.getsize(pdf_path)
        size_mb = file_size / (1024 * 1024)
        print(f"📄 File size: {size_mb:.2f} MB")
        
        if size_mb < 1:
            print("✅ PDF is under 1MB - ready for email!")
        else:
            print("⚠️  PDF is over 1MB - compression needed")
            
        return True
    else:
        print("❌ PDF generation failed")
        return False

if __name__ == "__main__":
    test_pdf_generation()
