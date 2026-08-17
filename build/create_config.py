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

from pathlib import Path
import json


BLANK = ""
CONFIG = "config.json"

# ANSI escape codes for styling
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = GREEN
MAGENTA = GREEN
BOLD = ""
RESET = "\033[0m"


class GitGardenConfig:
    """Manages CLI configuration prompting, validation, and saving settings to config.json."""

    def __init__(self):
        self.cfg_dir = Path(__file__).parents[1] / "src" / "cfg"
        self.repository = None
        self.branch = "master"
        self.commits = ""
        self.file = "py"
        self.starting_date = str()
        self.ending_date = str()
        self.push_strategy = "end"
        self.skip_days = []

    def declare_settings(self):
        """Prepares settings dictionary from the collected class attributes."""
        if self.repository == BLANK:
            print("Repository not detected, please reconfigure: ")
        return {
            "repository": self.repository,
            "branch": "master" if self.branch == BLANK else self.branch,
            "commits": self.commits,
            "file": "py" if self.file == BLANK else self.file,
            "starting_date": self.starting_date,
            "ending_date": self.ending_date,
            "push_strategy": self.push_strategy,
            "skip_days": self.skip_days,
        }

    def _parse_and_validate_date(self, date_str: str):
        """Parses a date string in DD-MM-YYYY, DD/MM/YYYY, or DD, M, YYYY formats.
        
        Returns:
            tuple: (year, month, day) representation of the date.
        Raises:
            ValueError: If the date format is invalid or values are out of bounds.
        """
        from datetime import datetime
        clean_str = date_str.strip()
        for separator in (",", "-", "/"):
            if separator in clean_str:
                parts = [p.strip() for p in clean_str.split(separator)]
                if len(parts) == 3:
                    try:
                        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                        datetime(year, month, day)
                        return (year, month, day)
                    except ValueError:
                        pass
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%d %m %Y"):
            try:
                dt = datetime.strptime(clean_str, fmt)
                return (dt.year, dt.month, dt.day)
            except ValueError:
                continue
        raise ValueError("Invalid date format. Use DD-MM-YYYY, DD/MM/YYYY or DD, M, YYYY.")

    def ask_configs(self, return_configs=False):
        """Prompts the user via CLI for configurations, validates inputs, and saves configs."""
        from datetime import datetime

        while True:
            self.repository = input(f"\n{BOLD}{CYAN}Repository URL: {RESET}").strip()
            if self.repository:
                break
            print(f"{BOLD}{RED}[ERROR] Repository URL is mandatory. Please try again.{RESET}")

        self.branch = input(f"{BOLD}{CYAN}Branch [Default: master]: {RESET}") or "master"
        self.commits = input(f"{BOLD}{CYAN}Commits per day [Default: Random]: {RESET}")
        self.file = input(f"{BOLD}{CYAN}File extension [Default: py]: {RESET}") or "py"

        # Calculate default dates
        today = datetime.now()
        try:
            last_year = today.replace(year=today.year - 1)
        except ValueError:
            from datetime import timedelta
            last_year = today - timedelta(days=365)
        default_start_str = last_year.strftime("%d-%m-%Y")
        default_end_str = today.strftime("%d-%m-%Y")

        # Validate starting date
        while True:
            start_input = input(f"\n{BOLD}{CYAN}Start date (DD-MM-YYYY) [Default: {default_start_str}]: {RESET}").strip()
            if not start_input:
                start_input = default_start_str
            try:
                start_year, start_month, start_day = self._parse_and_validate_date(start_input)
                self.starting_date = f"{start_day:02d}-{start_month:02d}-{start_year}"
                break
            except ValueError as e:
                print(f"{BOLD}{RED}[ERROR] {e} Please try again.{RESET}")

        # Validate ending date and verify order
        while True:
            end_input = input(f"{BOLD}{CYAN}End date (DD-MM-YYYY) [Default: {default_end_str}]: {RESET}").strip()
            if not end_input:
                end_input = default_end_str
            try:
                end_year, end_month, end_day = self._parse_and_validate_date(end_input)
                start_dt = datetime(start_year, start_month, start_day)
                end_dt = datetime(end_year, end_month, end_day)
                if end_dt <= start_dt:
                    print(f"{BOLD}{RED}[ERROR] End date must be after start date. Please try again.{RESET}")
                    continue
                self.ending_date = f"{end_day:02d}-{end_month:02d}-{end_year}"
                break
            except ValueError as e:
                print(f"{BOLD}{RED}[ERROR] {e} Please try again.{RESET}")

        # Prompt for days to skip
        days_input = input(f"{BOLD}{CYAN}Days to skip (comma-separated, e.g. Saturday, Sunday) [Default: None]: {RESET}")
        valid_weekdays = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
        skipped = []
        if days_input:
            import re
            parts = re.split(r'[,\s]+', days_input.strip())
            for d in parts:
                cleaned = d.lower()
                if cleaned in valid_weekdays:
                    skipped.append(cleaned)
        self.skip_days = skipped

        print(f"\n{BOLD}{MAGENTA}Push strategy:{RESET}")
        print(f" {BOLD}[1]{RESET} Push one by one (Slow, real-time graph updates)")
        print(f" {BOLD}[2]{RESET} Push once at end (Fast, graph updates within 24 hours)")
        strategy_choice = input(f"{BOLD}{CYAN}Option [1/2, Default: 1]: {RESET}")
        if strategy_choice.strip() == "2":
            self.push_strategy = "end"
        else:
            self.push_strategy = "daily"

        configs = self.declare_settings()
        self.save_configs(configs)

        print(f"\n{BOLD}{GREEN}-------------------------{RESET}")
        print(f"{BOLD}{CYAN} Repo:         {RESET} {configs['repository']}")
        print(f"{BOLD}{CYAN} Branch:       {RESET} {configs['branch']}")
        print(f"{BOLD}{CYAN} Commits/day:  {RESET} {'Random' if configs['commits'] == BLANK else configs['commits']}")
        print(f"{BOLD}{CYAN} File Type:    {RESET} .{configs['file']}")
        print(f"{BOLD}{CYAN} Date Range:   {RESET} {self.starting_date} to {self.ending_date}")
        print(f"{BOLD}{CYAN} Skip Days:    {RESET} {', '.join([d.capitalize() for d in configs['skip_days']]) if configs['skip_days'] else 'None'}")
        print(f"{BOLD}{CYAN} Push Strategy:{RESET} {configs['push_strategy']}")
        print(f"{BOLD}{GREEN}-------------------------{RESET}")

        if return_configs:
            return configs

    def save_configs(self, cfgs):
        """Saves configuration settings dictionary to the config.json file."""
        with open(self.cfg_dir / CONFIG, "w", encoding="utf-8") as file:
            json.dump(cfgs, file)
