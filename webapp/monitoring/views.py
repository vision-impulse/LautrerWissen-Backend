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

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt


HTML_REPORT_PATH = "/logs/analysis/nginx_report.html"


def nginx_dashboard_page(request, admin_site=None):
    """Render the NGINX GoAccess dashboard within the Django admin layout."""
    raw_url = "../nginx-dashboard/raw/"

    context = {
        "title": "NGINX Access Dashboard",
        "raw_url": raw_url,
    }

    # If admin_site was passed (from admin.get_urls)
    if admin_site:
        # Add admin layout context (sidebar, branding, user, etc.)
        context.update(admin_site.each_context(request))

    return render(request, "admin/monitoring/nginx_dashboard.html", context)


@xframe_options_exempt
def nginx_dashboard_raw(request):
    if not os.path.exists(HTML_REPORT_PATH):
        raise Http404("NGINX report not found")

    with open(HTML_REPORT_PATH, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    return HttpResponse(content, content_type="text/html")





