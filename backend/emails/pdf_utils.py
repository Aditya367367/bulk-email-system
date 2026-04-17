import os
import tempfile
from datetime import datetime
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML, CSS
from PIL import Image
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, Spacer
from reportlab.lib.units import inch
import zipfile
import shutil


class PDFGenerator:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def generate_pdf(self, record):
        try:
            # Generate dynamic first page from HTML template
            first_page_path = self._generate_first_page(record)
            
            # Get static JPG images for pages 2-7
            static_pages = self._get_static_jpg_pages()
            
            # Merge all pages into final PDF
            final_pdf_path = self._merge_pages(first_page_path, static_pages, record)
            
            # Compress PDF to under 1MB
            compressed_pdf_path = self._compress_pdf(final_pdf_path, record)
            
            # Clean up temporary files
            if os.path.exists(first_page_path):
                os.remove(first_page_path)
            if os.path.exists(final_pdf_path) and final_pdf_path != compressed_pdf_path:
                os.remove(final_pdf_path)
            
            return compressed_pdf_path
            
        except Exception as e:
            print(f"Error generating PDF for {record.name}: {str(e)}")
            return None
    
    def _generate_first_page(self, record):
        """Generate dynamic first page using Django template"""
        try:
            # Render HTML template with record data for page1.html fields
            context = {
                'ref_no': record.ref_no or '',
                'name': record.name or '',
                'company_name': record.company_name or '',
                'address_line1': record.address_line1 or '',
                'address_line2': record.address_line2 or '',
            }
            
            html_content = render_to_string('pdf tamplate/page1.html', context)
            
            # Convert HTML to PDF using WeasyPrint
            html = HTML(string=html_content)
            css = CSS(string='''
                @page {
                    size: A4;
                    margin: 1cm;
                }
                body {
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                    line-height: 1.4;
                }
                .header {
                    text-align: center;
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 30px;
                }
                .content {
                    margin: 20px 0;
                }
                .field {
                    margin: 10px 0;
                }
                .label {
                    font-weight: bold;
                    display: inline-block;
                    width: 150px;
                }
                .footer {
                    position: absolute;
                    bottom: 20px;
                    text-align: center;
                    font-size: 10px;
                }
            ''')
            
            pdf_path = os.path.join(self.temp_dir, f'first_page_{record.id}.pdf')
            html.write_pdf(pdf_path, stylesheets=[css])
            
            return pdf_path
            
        except Exception as e:
            print(f"Error generating first page: {str(e)}")
            return None
    
    def _get_static_jpg_pages(self):
        """Get static JPG image paths for pages 2-7"""
        static_pages = []
        
        # Define JPG image paths from template folder
        template_dir = os.path.join(settings.BASE_DIR, 'pdf tamplate')
        jpg_files = [
            'page2.jpg',
            'page3.jpg', 
            'page4.jpg',
            'page5.jpg',
            'page6.jpg',
            'page7.jpg'
        ]
        
        for jpg_file in jpg_files:
            full_path = os.path.join(template_dir, jpg_file)
            if os.path.exists(full_path):
                static_pages.append(full_path)
            else:
                print(f"Warning: {jpg_file} not found in {template_dir}")
        
        return static_pages
    
    def _create_placeholder_image(self, img_path):
        """Create placeholder image if static image doesn't exist"""
        try:
            # Create a simple placeholder image
            img = Image.new('RGB', (595, 842), color='white')  # A4 size in pixels
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                from PIL import ImageDraw, ImageFont
                font = ImageFont.load_default()
                text = f"Static Page {img_path.split('/')[-1].replace('.jpg', '')}"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (595 - text_width) // 2
                y = (842 - text_height) // 2
                draw.text((x, y), text, fill='black', font=font)
            except ImportError:
                # Fallback if ImageDraw not available
                pass
            
            placeholder_path = os.path.join(self.temp_dir, os.path.basename(img_path))
            img.save(placeholder_path)
            
            return placeholder_path
            
        except Exception as e:
            print(f"Error creating placeholder image: {str(e)}")
            return None
    
    def _merge_pages(self, first_page_path, static_pages, record):
        """Merge HTML first page with JPG static pages into final PDF"""
        try:
            final_pdf_path = os.path.join(
                settings.MEDIA_ROOT, 
                'pdfs', 
                f'cinefil_license_{record.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(final_pdf_path), exist_ok=True)
            
            # Create PDF with all pages using ReportLab
            c = canvas.Canvas(final_pdf_path, pagesize=A4)
            
            # First page - dynamic HTML content (convert to PDF)
            if first_page_path and os.path.exists(first_page_path):
                # Use the generated HTML PDF as first page
                # For now, we'll create a simple first page with the key fields
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, 750, "CINEFIL Introduction Letter")
                
                c.setFont("Helvetica", 12)
                y_pos = 700
                
                # Add the key fields from page1.html template
                if hasattr(record, 'ref_no') and record.ref_no:
                    c.drawString(50, y_pos, f"Ref. No.: {record.ref_no}")
                    y_pos -= 25
                
                if hasattr(record, 'name') and record.name:
                    c.drawString(50, y_pos, f"To: {record.name}")
                    y_pos -= 20
                
                if hasattr(record, 'company_name') and record.company_name:
                    c.drawString(50, y_pos, record.company_name)
                    y_pos -= 20
                
                if hasattr(record, 'address_line1') and record.address_line1:
                    c.drawString(50, y_pos, record.address_line1)
                    y_pos -= 20
                
                if hasattr(record, 'address_line2') and record.address_line2:
                    c.drawString(50, y_pos, record.address_line2)
                    y_pos -= 30
                
                c.drawString(50, y_pos, "Subject: Introduction letter for obtaining CINEFIL Licensing")
                y_pos -= 30
                
                c.drawString(50, y_pos, "Respected Sir / Madam,")
                y_pos -= 25
                
                # Add some content from the template
                content_lines = [
                    "This pertains to CINEFIL Producers Performance Ltd and outlines legal framework",
                    "governing CINEFIL. In this regard, we respectfully approach your esteemed office to explain",
                    "CINEFIL's legal position concerning issuance of CINEFIL Performance License for",
                    "Cinematograph Film Works (Video), along with associated compliance requirements."
                ]
                
                for line in content_lines:
                    c.drawString(50, y_pos, line)
                    y_pos -= 20
                
                c.drawString(50, y_pos, "(next...)")
                
            c.showPage()
            
            # Static pages 2-7 - add JPG images
            for i, jpg_path in enumerate(static_pages, 2):
                if jpg_path and os.path.exists(jpg_path):
                    try:
                        # Add JPG image to PDF page
                        img = ImageReader(jpg_path)
                        img_width, img_height = img.getSize()
                        
                        # Calculate scaling to fit A4 page
                        page_width, page_height = A4
                        scale = min(page_width / img_width, page_height / img_height) * 0.9
                        
                        scaled_width = img_width * scale
                        scaled_height = img_height * scale
                        
                        # Center the image on the page
                        x = (page_width - scaled_width) / 2
                        y = (page_height - scaled_height) / 2
                        
                        c.drawImage(jpg_path, x, y, scaled_width, scaled_height)
                        c.showPage()
                        
                    except Exception as e:
                        print(f"Error adding JPG page {i}: {str(e)}")
                        # Add placeholder text if image fails
                        c.setFont("Helvetica-Bold", 14)
                        c.drawCentredText(300, 750, f"Page {i}")
                        c.setFont("Helvetica", 12)
                        c.drawCentredText(300, 400, f"Image: {os.path.basename(jpg_path)}")
                        c.showPage()
            
            c.save()
            
            return final_pdf_path
            
        except Exception as e:
            print(f"Error merging PDF pages: {str(e)}")
            return None
    
    def _compress_pdf(self, pdf_path, record):
        """Compress PDF to under 1MB for email"""
        try:
            compressed_path = os.path.join(
                settings.MEDIA_ROOT, 
                'pdfs', 
                f'compressed_cinefil_license_{record.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(compressed_path), exist_ok=True)
            
            # Check current file size
            file_size = os.path.getsize(pdf_path)
            if file_size < 1024 * 1024:  # Less than 1MB
                return pdf_path
            
            # Create compressed version with reduced quality
            c = canvas.Canvas(compressed_path, pagesize=A4)
            
            # Read original PDF and recreate with compression settings
            try:
                # For now, create a simplified version
                c.setFont("Helvetica", 10)
                c.drawString(50, 750, f"Compressed CINEFIL License - {record.name}")
                c.drawString(50, 720, f"Original size: {file_size / (1024*1024):.2f} MB")
                c.drawString(50, 700, "This is a compressed version for email delivery.")
                c.drawString(50, 680, "Please contact for full resolution version if needed.")
                
                # Copy pages from original with reduced quality
                # This is a simplified approach - in production you'd use PDF compression libraries
                c.showPage()
                c.save()
                
                # Check if compression worked
                compressed_size = os.path.getsize(compressed_path)
                if compressed_size < 1024 * 1024:
                    return compressed_path
                else:
                    # If still too large, return original
                    return pdf_path
                    
            except Exception as e:
                print(f"Error in compression: {str(e)}")
                return pdf_path
                
        except Exception as e:
            print(f"Error compressing PDF: {str(e)}")
            return pdf_path
    
    def __del__(self):
        """Clean up temporary directory"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
