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

import os

from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import HttpResponse, Http404
from django.shortcuts import render
from .models import MonitoringDashboard
from .models import DockerContainerStatus
from django.http import FileResponse, HttpResponseNotFound
from django.urls import reverse

from . import views


HTML_REPORT_PATH = "/logs/analysis/nginx_report.html"


@admin.register(MonitoringDashboard)
class MonitoringDashboardAdmin(admin.ModelAdmin):
    """Directly show the NGINX dashboard in admin."""
    change_list_template = "admin/monitoring/nginx_dashboard.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "nginx-dashboard/",
                self.admin_site.admin_view(
                    lambda request: views.nginx_dashboard_page(request, admin_site=self.admin_site)
                ),
                name="monitoring-nginx-dashboard",
            ),
            path(
                "nginx-dashboard/raw/",
                self.admin_site.admin_view(views.nginx_dashboard_raw),
                name="monitoring-nginx-dashboard-raw",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """Redirect the default list view directly to nginx-dashboard."""
        from django.shortcuts import redirect
        return redirect("admin:monitoring-nginx-dashboard")

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False


@admin.register(DockerContainerStatus)
class DockerContainerStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "last_updated", "download_log_link")
    readonly_fields = ("last_updated","name", "status", "download_log_link")

    def get_urls(self):
        """Add a custom URL for downloading the log file"""
        urls = super().get_urls()
        custom_urls = [
            path(
                "download-log/<int:object_id>/",
                self.admin_site.admin_view(self.download_log_view),
                name="dockercontainerstatus_download_log",
            ),
        ]
        return custom_urls + urls

    def download_log_link(self, obj):
        """Show a clickable link in admin list view"""
        if not obj or not obj.log_file:
            return "-"
        url = reverse("admin:dockercontainerstatus_download_log", args=[obj.pk])
        return format_html('<a class="button" href="{}">Download</a>', url)

    download_log_link.short_description = "Log File"
    download_log_link.allow_tags = True

    def download_log_view(self, request, object_id):
        """Serve the log file for download"""
        obj = self.get_object(request, object_id)
        if not obj:
            return HttpResponseNotFound("Object not found")

        log_path = obj.log_file  # should be an absolute file path
        if not log_path or not os.path.exists(log_path):
            return HttpResponseNotFound("Log file not found")

        return FileResponse(open(log_path, "rb"), as_attachment=True, filename=os.path.basename(log_path))

    
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False