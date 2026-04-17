import os
import tempfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.utils.text import slugify
from PIL import Image
from weasyprint import HTML, CSS


class PDFGenerator:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = os.path.join(settings.BASE_DIR, 'pdf tamplate')

    def generate_pdf(self, record):
        try:
            html_content = self._build_pdf_html(record)
            final_pdf_path = self._get_output_path(record)

            os.makedirs(os.path.dirname(final_pdf_path), exist_ok=True)

            HTML(string=html_content, base_url=self.template_dir).write_pdf(
                final_pdf_path,
                stylesheets=[CSS(string=self._get_pdf_css())],
            )

            return final_pdf_path
        except Exception as e:
            print(f"Error generating PDF for {record.name}: {str(e)}")
            return None

    def _build_pdf_html(self, record):
        total_pages = 1 + len(self._get_static_page_names())
        page1_html = self._render_first_page(record, total_pages)
        static_pages_html = self._build_static_pages_html(total_pages)
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Cinefil License PDF</title>
</head>
<body>
  {page1_html}
  {static_pages_html}
</body>
</html>
"""

    def _render_first_page(self, record, total_pages):
        template_path = os.path.join(self.template_dir, 'page1.html')
        with open(template_path, 'r', encoding='utf-8') as template_file:
            template = template_file.read()

        context = self._build_context(record)
        rendered = self._replace_placeholders(template, context)

        for asset_name in [
            'Cinefil License Application Form NEW_page-0001 1.jpg',
            'footer.jpg',
        ]:
            optimized_uri = self._get_optimized_image_uri(asset_name)
            if optimized_uri:
                rendered = rendered.replace(f'src="{asset_name}"', f'src="{optimized_uri}"')

        return rendered

    def _build_context(self, record):
        context = {}

        for field in record._meta.fields:
            value = getattr(record, field.name, '')
            context[field.name] = '' if value is None else str(value)

        context['address_line1'] = context.get('address_line1') or self._split_address(record.address)[0]
        context['address_line2'] = context.get('address_line2') or self._split_address(record.address)[1]
        context['company_name'] = context.get('company_name') or context.get('name', '')

        return context

    def _replace_placeholders(self, template, context):
        rendered = template
        for key, value in context.items():
            rendered = rendered.replace(f'{{{{ {key} }}}}', value)
            rendered = rendered.replace(f'{{{{{key}}}}}', value)
        return rendered

    def _split_address(self, address):
        if not address:
            return '', ''

        parts = [part.strip() for part in str(address).split(',') if part.strip()]
        if len(parts) <= 1:
            return str(address).strip(), ''
        return parts[0], ', '.join(parts[1:])

    def _build_static_pages_html(self, total_pages):
        pages = []
        for index, image_name in enumerate(self._get_static_page_names(), start=2):
            image_path = os.path.join(self.template_dir, image_name)
            if not os.path.exists(image_path):
                print(f"Warning: {image_name} not found in {self.template_dir}")
                continue

            optimized_uri = self._get_optimized_image_uri(image_name)
            if not optimized_uri:
                continue

            pages.append(
                f"""
<section class="static-page">
  <img src="{optimized_uri}" alt="{image_name}">
  <div class="page-number">Page {index} out of {total_pages}</div>
</section>
"""
            )

        return ''.join(pages)

    def _get_static_page_names(self):
        page_names = []
        for filename in sorted(os.listdir(self.template_dir)):
            lower_name = filename.lower()
            if not lower_name.startswith('page') or not lower_name.endswith(('.jpg', '.jpeg', '.png')):
                continue
            if lower_name == 'page1.jpg':
                continue
            page_names.append(filename)
        return page_names

    def _get_output_path(self, record):
        folder_name = self._get_job_folder_name(record)
        return os.path.join(
            settings.MEDIA_ROOT,
            'pdfs',
            folder_name,
            f'cinefil_license_{record.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )

    def _get_job_folder_name(self, record):
        excel_name = ''
        if getattr(record, 'email_job', None) and getattr(record.email_job, 'excel_file', None):
            excel_name = Path(record.email_job.excel_file.name).stem

        if not excel_name:
            excel_name = f'job-{getattr(record, "email_job_id", "unknown")}'

        return slugify(excel_name) or f'job-{getattr(record, "email_job_id", "unknown")}'

    def _get_optimized_image_uri(self, image_name):
        source_path = os.path.join(self.template_dir, image_name)
        if not os.path.exists(source_path):
            return None

        optimized_path = os.path.join(self.temp_dir, image_name)
        if os.path.exists(optimized_path):
            return Path(optimized_path).as_uri()

        with Image.open(source_path) as image:
            save_kwargs = {}
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')

            if image_name.lower().startswith('page'):
                save_kwargs = {'quality': 45, 'optimize': True}
            else:
                save_kwargs = {'quality': 60, 'optimize': True}

            image.save(optimized_path, format='JPEG', **save_kwargs)

        return Path(optimized_path).as_uri()

    def _get_pdf_css(self):
        return """
@page {
    size: A4;
    margin: 0;
}

html, body {
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, sans-serif;
}

.container {
    box-sizing: border-box;
}

.static-page {
    page-break-before: always;
    break-before: page;
    width: 210mm;
    height: 297mm;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.static-page img {
    display: block;
    max-width: 210mm;
    max-height: 297mm;
    width: auto;
    height: auto;
    object-fit: contain;
    object-position: center center;
    margin: 0 auto;
    transform: translate(-32px, -8px);
}

.page-number {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 8px;
    text-align: center;
    font-size: 11px;
    color: #333;
}
"""

    def __del__(self):
        try:
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
        except Exception:
            pass
