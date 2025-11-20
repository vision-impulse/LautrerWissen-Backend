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
 

"""
URL configuration for webapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from lautrer_wissen.urls import router as lautrer_wissen_router
from frontend_config.urls import router as frontend_config_router

router = DefaultRouter()
router.registry.extend(lautrer_wissen_router.registry)
router.registry.extend(frontend_config_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("admin/monitoring/", include("monitoring.urls")), 
    path('admin/pipeline_manager/', include('pipeline_manager.urls')),  
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)