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


JAZZMIN_SETTINGS = {
    "site_title": "LW Admin",
    "site_header": "Lauter Wissen Admin",
    "site_brand": "Lauter Wissen",
    "welcome_sign": "Welcome to the Lauter Wissen admin dashboard",
    "navigation_expanded": False,
    "show_sidebar": True,
    "show_ui_builder": True,
    "order_with_respect_to": ["monitoring",  
                              "pipeline_manager",
                              "lautrer_wissen", 
                              "frontend_config", 
                              "auth", 
                              "django_apscheduler"],
    "icons": {
        "monitoring": "fas fa-chart-area",
        "pipeline_manager": "fas fa-download",
        "lautrer_wissen": "fas fa-database",
        "frontend_config": "fas fa-desktop",
        "auth": "fas fa-users-cog",
        "django_apscheduler": "fas fa-clock",
        
        # System monitoring
        "monitoring.MonitoringDashboard": "fas fa-chart-line",
        "monitoring.DockerContainerStatus": "fab fa-docker",

        # Users and Groups
        "auth.User": "fas fa-user",                 
        "auth.Group": "fas fa-users",

        # Frontend Config
        "frontend_config.ModelConfig": "fas fa-sliders-h",
        "frontend_config.MapLayerGroup": "fas fa-layer-group",

        # AppScheduler
        "django_apscheduler.DjangoJob": "fas fa-tasks",
        "django_apscheduler.DjangoJobExecution": "fas fa-history",

        # Pipeline Manager 
        "pipeline_manager.Pipeline": "fas fa-cogs",
        "pipeline_manager.PipelineRun": "fas fa-tasks",
        "pipeline_manager.PipelineSchedule": "fas fa-calendar-alt",
    },
}

JAZZMIN_UI_TWEAKS = {
    "sidebar_nav_child_indent": True,
}