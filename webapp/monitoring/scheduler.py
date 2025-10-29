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

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.utils import timezone
from django.core.management import call_command
from pipeline_manager.models import PipelineSchedule
from django.db import OperationalError
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("webapp")

m_scheduler = None

def sync_docker_job():
    call_command("update_docker_status")

def start():
    
    global m_scheduler
    if m_scheduler is not None:
        logger.warning("Scheduler already started.")
        return

    m_scheduler = BackgroundScheduler(timezone=timezone.get_current_timezone())
    m_scheduler.add_jobstore(DjangoJobStore(), "default")

    m_scheduler.add_job(
        sync_docker_job,
        trigger=CronTrigger(minute="*/1"),
        id="sync_docker_status",
        replace_existing=True,
        name="Sync Docker status from log file"
    )
    m_scheduler.start()
    logger.info("Scheduler started with all active pipelines.")
