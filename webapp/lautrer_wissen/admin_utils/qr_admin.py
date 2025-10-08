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

import qrcode

from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.utils.html import format_html
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from django.db import models
from io import BytesIO
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from ..forms import GeoForm


class CustomAdminWithQR(admin.ModelAdmin):

    form = GeoForm
    exclude = ("geometry",)

    def get_list_display(self, request):
        # if hasattr(self.model, 'MAP_FIELDS'):
        #    field_names = list(self.model.MAP_FIELDS.keys())
        # else:
        field_names = [
            field.name
            for field in self.model._meta.get_fields()
            if isinstance(field, models.Field)
            and not field.many_to_many
            and not field.one_to_many
        ]
        return tuple(field_names) + ("qr_code_button",)

    def qr_code_button(self, obj):
        return format_html(
            '<a class="button" style="min-width: 70px; display: inline-block;" href="{}" target="_blank">QR-Code</a>',
            f"generate_qr/{obj.pk}",
        )

    qr_code_button.short_description = "QR-Code"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "generate_qr/<int:pk>", self.admin_site.admin_view(self.generate_qr_pdf)
            )
        ]
        return custom_urls + urls

    def generate_qr_pdf(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        url = obj.get_frontend_url()

        # === Generate QR code ===
        qr = qrcode.make(url)
        qr_buffer = BytesIO()
        qr.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        # === PDF setup ===
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch,
        )
        doc.title = "QR-Code"

        styles = getSampleStyleSheet()
        normal = styles["Normal"]
        title_style = styles["Heading2"]

        elements = []

        # === QR code ===
        qr_image = Image(qr_buffer, width=200, height=200)
        elements.append(qr_image)
        elements.append(Spacer(1, 0.3 * inch))

        # === Object info ===
        visible_object_name = getattr(obj.__class__, "VISIBLE_OBJECT_NAME", "")
        fields_mapping = getattr(obj.__class__, "MAP_FIELDS", {})

        elements.append(Paragraph(f"<b>OBJEKTART:</b> {visible_object_name}", normal))
        elements.append(Paragraph(f"<b>URL:</b> {url}", normal))
        elements.append(Spacer(1, 0.2 * inch))

        # === Add field mappings ===
        for model_field, response_field in fields_mapping.items():
            val = getattr(obj, model_field, None)
            if val:
                text = f"<b>{response_field}:</b> {val}"
                elements.append(Paragraph(text, normal))
                elements.append(Spacer(1, 0.1 * inch))

        # === Build PDF ===
        doc.build(elements)

        buffer.seek(0)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'inline; filename="qr_code_{visible_object_name}_{pk}.pdf"'
        )
        response.write(buffer.getvalue())
        return response
