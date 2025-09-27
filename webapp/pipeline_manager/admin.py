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
from django.utils.html import format_html
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponseRedirect
import subprocess
from .models import Pipeline, ResourceOSM, ResourceWFSFile, LocalResourceFile, ResourceWikipage, RemoteResourceFile
from .models import PipelineType
from .models import PipelineSchedule
from .models import PipelineRun, PipelineRunStep



# --- Inlines ---
class ResourceOSMInline(admin.StackedInline):
    model = ResourceOSM
    extra = 0
    can_delete = False  

class ResourceWFSFileInline(admin.StackedInline):
    model = ResourceWFSFile
    extra = 0
    can_delete = False  

class LocalResourceFileInline(admin.StackedInline):
    model = LocalResourceFile
    extra = 0
    can_delete = False  
    
class ResourceWikipageInline(admin.StackedInline):
    model = ResourceWikipage
    extra = 0
    can_delete = False  

class RemoteResourceFileInline(admin.StackedInline):
    model = RemoteResourceFile
    extra = 0
    can_delete = False  


class BasePipelineAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'run_pipeline_button')

    def run_pipeline_button(self, obj):
        return format_html(
            '<a class="button" href="run/{}/">Run</a>',
            obj.pk
        )
    run_pipeline_button.short_description = 'Run Pipeline'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('run/<int:pipeline_id>/', self.admin_site.admin_view(self.run_pipeline_view), name="run_pipeline")
        ]
        return custom_urls + urls

    def run_pipeline_view(self, request, pipeline_id):
        from .models import Pipeline
        pipeline = Pipeline.objects.get(id=pipeline_id)
        
        # Launch the command async
        subprocess.Popen(['python', 'manage.py', 'run_data_pipeline', str(pipeline.name), "--caller=manual"])

        self.message_user(request, f"Pipeline '{pipeline.name}' is running.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))



@admin.register(Pipeline)
class PipelineAdmin(BasePipelineAdmin):

    readonly_fields = ("name", )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        inlines = []
        if obj.name == PipelineType.OSM.name:
            inlines = [ResourceOSMInline]
        elif obj.name == PipelineType.KL_GEO_WFS.name:
            inlines = [ResourceWFSFileInline]
        elif obj.name == PipelineType.WIKIPEDIA.name:
            inlines = [ResourceWikipageInline]
        elif obj.name == PipelineType.WIFI_LOCAL.name:
            inlines = [LocalResourceFileInline]
        elif obj.name in [PipelineType.TTN_GATEWAY.name, PipelineType.WIFI_FREIFUNK.name,
                          PipelineType.WIFI_FREIFUNK.name, PipelineType.VRN.name,
                          PipelineType.EV_STATIONS.name, PipelineType.KL_EVENTS.name,
                          PipelineType.KL_GEO_RESOURCES.name, PipelineType.EMERGENCY_POINTS.name,
                          PipelineType.KL_EVENTS_RIS.name]:
            inlines = [RemoteResourceFileInline]

        return [inline(self.model, self.admin_site) for inline in inlines]


@admin.register(PipelineSchedule)
class PipelineScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'cron_expression', 'is_active', )
    list_editable = ('cron_expression', 'is_active')
    search_fields = ('name',)



class PipelineRunStepInline(admin.TabularInline):
    model = PipelineRunStep
    readonly_fields = ('step_name', 'status', 'started_at', 'finished_at', 'message')
    extra = 0
    can_delete = False


@admin.register(PipelineRun)
class PipelineRunAdmin(admin.ModelAdmin):
    list_display = ('pipeline_name', 'origin', 'status', 'started_at', 'finished_at')
    readonly_fields = ( 'error_message', 'created_at')
    inlines = [PipelineRunStepInline]


admin.site._registry[PipelineSchedule].model._meta.verbose_name = "Daten Pipeline Cron-Job"
admin.site._registry[PipelineSchedule].model._meta.verbose_name_plural = "Daten Pipeline Cron-Jobs"

admin.site._registry[Pipeline].model._meta.verbose_name = "Daten Pipeline"
admin.site._registry[Pipeline].model._meta.verbose_name_plural = "Daten Pipelines"
