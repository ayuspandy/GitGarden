"""
GitGarden - Fake Commit Generator for GitHub

Copyright (C) 2026 ayuspandy

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


from datetime import datetime, timedelta


class DateChanger:
    """Manages the iteration of dates and time formatting for fake commits."""

    def __init__(self, starting_date: tuple, ending_date: tuple):
        """Initializes DateChanger with target date range and calculates total days."""
        self.starting_date = datetime(*starting_date)
        self.ending_date = datetime(*ending_date)
        self.current_iteration_day = self.starting_date
        self.current_system_date = datetime.now()
        self.days = (self.ending_date - self.starting_date).days

    @staticmethod
    def create_systemtime_object(timeobject):
        """Constructs a datetime object using current hour/minute/second combined with specific day/month/year."""

        os_date = datetime.now()

        return datetime(
            timeobject.year,  # Year
            timeobject.month,  # Month
            timeobject.day,  # Day
            os_date.hour,  # Hour
            os_date.minute,  # Minute
            os_date.second,  # Second
        )

    def change_date(self, to_future=False):
        """Formats the current iteration day as a date-time string."""
        new_date = self.create_systemtime_object(self.current_iteration_day)

        return new_date.strftime("%d-%m-%Y %H:%M:%S")

    def next_day(self, days=1):
        """Advances the current iteration date by a specified number of days."""
        self.current_iteration_day += timedelta(days=days)
