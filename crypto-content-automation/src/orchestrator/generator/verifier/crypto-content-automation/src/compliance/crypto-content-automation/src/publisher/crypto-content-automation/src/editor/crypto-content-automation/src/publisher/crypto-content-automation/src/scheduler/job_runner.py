# Copyright 2026 Георги Владимиров
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

import time
import schedule
from datetime import datetime
from typing import Callable


class JobRunner:
    """
    Central scheduler for automated content generation, verification
    and publishing pipelines.
    """

    def __init__(self):
        self.jobs = []

    def register_daily(self, time_utc: str, task: Callable):
        """
        Run task every day at fixed UTC time (HH:MM).
        """
        job = schedule.every().day.at(time_utc).do(self._wrap(task))
        self.jobs.append(job)

    def register_hourly(self, task: Callable):
        """
        Run task every hour.
        """
        job = schedule.every().hour.do(self._wrap(task))
        self.jobs.append(job)

    def register_interval(self, minutes: int, task: Callable):
        """
        Run task every N minutes.
        """
        job = schedule.every(minutes).minutes.do(self._wrap(task))
        self.jobs.append(job)

    def _wrap(self, task: Callable):
        def safe_task():
            start = datetime.utcnow()
            try:
                task()
            except Exception as e:
                print(f"[{start.isoformat()}] JOB ERROR: {e}")
            else:
                end = datetime.utcnow()
                print(f"[{start.isoformat()}] JOB OK in {(end-start).total_seconds()}s")
        return safe_task

    def run_forever(self, poll_interval: int = 30):
        """
        Blocking loop. Executes scheduled jobs.
        """
        print("Scheduler started.")
        while True:
            schedule.run_pending()
            time.sleep(poll_interval)
