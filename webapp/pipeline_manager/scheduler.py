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
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.utils import timezone
from django.core.management import call_command
from pipeline_manager.models import PipelineSchedule
from django.db import OperationalError
import logging


logger = logging.getLogger("webapp")

scheduler = None

def run_pipeline(schedule_id):
    """Run the pipeline corresponding to a PipelineSchedule."""
    try:
        schedule = PipelineSchedule.objects.get(pk=schedule_id)
    except PipelineSchedule.DoesNotExist:
        logger.warning("Schedule %s no longer exists.", schedule_id)
        return

    logger.info("Running scheduled pipeline: %s (id=%s)", schedule.name, schedule.pk)
    call_command("run_data_pipeline", schedule.name)


def cron_trigger_from_expr(expr):
    """Convert a cron string (e.g. '0 2 * * *') into an APScheduler CronTrigger."""
    from apscheduler.triggers.cron import CronTrigger
    expr = expr.strip()
    return CronTrigger.from_crontab(expr)


def _parse_cron_expression(expr):
    """Convert a cron string like '0 2 * * *' to APScheduler kwargs."""
    minute, hour, day, month, day_of_week = expr.split()
    return dict(minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week)


def sync_schedules():
    """Fully resync APScheduler jobs with PipelineSchedule DB table."""
    global scheduler
    if scheduler is None:
        logger.error("Scheduler not initialized; cannot sync schedules.")
        return

    try:
        db_schedules = list(PipelineSchedule.objects.filter(is_active=True))
    except OperationalError:
        logger.warning("Database not ready — skipping schedule sync.")
        return

    logger.info("Resyncing %s active pipeline schedules...", len(db_schedules))

    for job in scheduler.get_jobs():
        scheduler.remove_job(job.id)

    for sched in db_schedules:
        try:
            trigger = cron_trigger_from_expr(sched.cron_expression)
            scheduler.add_job(
                run_pipeline,
                trigger=trigger,
                id=f"pipeline_{sched.name}",
                args=[sched.pk],
                replace_existing=True,
                name=f"pipeline:{sched.name}"
            )
            logger.info("Added job for pipeline %s (%s)", sched.name, sched.cron_expression)
        except Exception as e:
            logger.error("Failed to add job for %s: %s", sched.name, e)

    logger.info("Schedule sync complete. Total jobs: %d", len(scheduler.get_jobs()) - 1)


def start():
    """Initialize scheduler and start periodic resync."""
    global scheduler
    if scheduler is not None:
        logger.warning("Scheduler already started.")
        return

    scheduler = BackgroundScheduler(timezone=timezone.get_current_timezone())
    scheduler.add_jobstore(DjangoJobStore(), "default")

    sync_schedules()

    scheduler.start()
    logger.info("Scheduler started with all active pipelines.")
