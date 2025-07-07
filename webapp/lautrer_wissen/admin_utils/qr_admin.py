# Copyright (c) 2025 Vision Impulse GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Authors: Benjamin Bischke

from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.utils.html import format_html
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from django.db import models
import qrcode
from io import BytesIO


class CustomAdminWithQR(admin.ModelAdmin):

    def get_list_display(self, request):
        if hasattr(self.model, 'MAP_FIELDS'):
            field_names = list(self.model.MAP_FIELDS.keys())
        else:
            field_names = [
                field.name for field in self.model._meta.get_fields()
                if isinstance(field, models.Field) and not field.many_to_many and not field.one_to_many
            ]
        return ('qr_code_button',) + tuple(field_names)

    def qr_code_button(self, obj):
        return format_html(
            '<a class="button" style="min-width: 70px; display: inline-block;" href="{}" target="_blank">QR-Code</a>',
            f'generate_qr/{obj.pk}'
        )

    qr_code_button.short_description = 'QR-Code'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate_qr/<int:pk>', self.admin_site.admin_view(self.generate_qr_pdf))
        ]
        return custom_urls + urls

    def generate_qr_pdf(self, request, pk):
        obj = self.model.objects.get(pk=pk)

        url = obj.get_frontend_url()

        qr = qrcode.make(url)
        qr_buffer = BytesIO()
        qr.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)

        qr_image = ImageReader(qr_buffer)

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setTitle(f"QR Code")
        c.drawImage(qr_image, 125, 350, width=350, height=350)

        fields_mapping = getattr(obj.__class__, 'MAP_FIELDS', {})
        visible_object_name = getattr(obj.__class__, 'VISIBLE_OBJECT_NAME', "")
        start = 250
        c.drawString(100, start, "OBJEKTART: " + visible_object_name )
        start -=20 
        c.drawString(100, start, "URL: " + url )
        start -=30 
        for model_field, response_field in fields_mapping.items():
            val = getattr(obj, model_field, None)
            if val is not None and val != "":
                c.drawString(100, start, response_field + ": " + str(val) )
                start -=20 

        c.showPage()
        c.save()
        buffer.seek(0)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="qr_info_{pk}.pdf"'
        response.write(buffer.getvalue())
        return response
    
    def generate_qr(self, request, pk):
        print(request)
        obj = self.model.objects.get(pk=pk)
        url = obj.get_frontend_url()

        qr = qrcode.make(url)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        return HttpResponse(buffer, content_type='image/png')