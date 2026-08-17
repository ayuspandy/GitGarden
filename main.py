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
import time
import os, shutil
import statistics
from build import GitGardenConfig
from src import GitBuilder
from src import DateChanger

import sys
import argparse
from datetime import datetime

# ANSI escape codes for styling
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = GREEN
MAGENTA = GREEN
BOLD = ""
RESET = "\033[0m"

ROOT_PATH = Path(__file__).parents[0]
FILES_DIR = ROOT_PATH / "files"


def preview_graph(params, start_date, stop_date):
    """Generates and displays a chunked ASCII representation of the simulated contribution graph."""
    from datetime import datetime, timedelta
    import random

    start_dt = datetime(*start_date)
    stop_dt = datetime(*stop_date)

    # Sunday-to-Saturday layout matching GitHub's contributions graph
    # 0 = Sunday, 1 = Monday, ..., 6 = Saturday
    start_wday = int(start_dt.strftime("%w"))
    start_sunday = start_dt - timedelta(days=start_wday)

    total_weeks = ((stop_dt - start_sunday).days // 7) + 1
    grid = [[None for _ in range(total_weeks)] for _ in range(7)]

    skip_days = params.get("skip_days", [])
    commits_setting = params.get("commits", "")

    # Run deterministic simulation using the date hash as seed for a stable visual
    current_dt = start_dt
    while current_dt <= stop_dt:
        wday = int(current_dt.strftime("%w"))
        col = (current_dt - start_sunday).days // 7
        
        day_name = current_dt.strftime("%A").lower()
        if day_name in skip_days:
            commits = 0
        else:
            if commits_setting == "":
                random.seed(int(current_dt.strftime("%Y%m%d")))
                commits = random.randint(1, 25)
            else:
                try:
                    commits = int(commits_setting)
                except ValueError:
                    random.seed(int(current_dt.strftime("%Y%m%d")))
                    commits = random.randint(1, 25)
        
        grid[wday][col] = commits
        current_dt += timedelta(days=1)
    
    # Restore random state
    random.seed(None)

    # Display colors
    # Level 0: 0 commits
    # Level 1: 1-6 commits
    # Level 2: 7-12 commits
    # Level 3: 13-18 commits
    # Level 4: 19+ commits
    color_none = " "
    color_zero = "\033[38;5;238m■\033[0m"
    
    def get_color_char(val):
        if val is None:
            return color_none
        if val == 0:
            return color_zero
        if val <= 6:
            return "\033[38;5;120m■\033[0m"
        elif val <= 12:
            return "\033[38;5;76m■\033[0m"
        elif val <= 18:
            return "\033[38;5;34m■\033[0m"
        else:
            return "\033[38;5;22m■\033[0m"

    weekday_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    print(f"\n{BOLD}{GREEN}-------------------------{RESET}")
    
    # Chunking columns dynamically based on terminal width to avoid wrapping
    import shutil
    terminal_width = shutil.get_terminal_size().columns
    # Each cell is 2 chars ("■ "). Label is 4 chars ("Sun "). We subtract 8 for safety margin.
    max_chunk_size = max(5, (terminal_width - 8) // 2)
    chunk_size = min(53, max_chunk_size)

    for chunk_start in range(0, total_weeks, chunk_size):
        chunk_end = min(chunk_start + chunk_size, total_weeks)
        if total_weeks > chunk_size:
            print(f"\n{BOLD}{CYAN}Weeks {chunk_start + 1} to {chunk_end} of {total_weeks}:{RESET}")
        
        for r in range(7):
            row_str = f"{weekday_labels[r]} "
            for c in range(chunk_start, chunk_end):
                row_str += get_color_char(grid[r][c]) + " "
            print(row_str)

    print(f"\nLegend: Less {color_zero} \033[38;5;120m■\033[0m \033[38;5;76m■\033[0m \033[38;5;34m■\033[0m \033[38;5;22m■\033[0m More")
    print(f"{BOLD}{GREEN}----------------------------------{RESET}\n")


def perform_system_checks():
    """Verifies that all required tools, configurations, and connections are available."""
    import subprocess
    
    print(f"\n{BOLD}{GREEN}RUNNING SYSTEM CHECKS{RESET}")
    
    all_ok = True
    
    # 1. Python version check
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f" {GREEN}[✓]{RESET} Python {py_version} is installed.")
    
    # 2. Git installation check
    git_installed = False
    git_version = ""
    try:
        res = subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            git_installed = True
            git_version = res.stdout.strip().replace("git version ", "")
    except Exception:
        pass
        
    if git_installed:
        print(f" {GREEN}[✓]{RESET} Git ({git_version}) is installed.")
    else:
        print(f" {RED}[✗]{RESET} Git is not installed or not found in PATH.")
        all_ok = False
        
    # 3. Git config check (user.name and user.email)
    git_config_ok = False
    if git_installed:
        git_name = ""
        git_email = ""
        try:
            name_res = subprocess.run(["git", "config", "--get", "user.name"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            email_res = subprocess.run(["git", "config", "--get", "user.email"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            git_name = name_res.stdout.strip()
            git_email = email_res.stdout.strip()
            if git_name and git_email:
                git_config_ok = True
        except Exception:
            pass
            
        if git_config_ok:
            print(f" {GREEN}[✓]{RESET} Git user.name (\"{git_name}\") and user.email (\"{git_email}\") are configured.")
        else:
            print(f" {RED}[✗]{RESET} Git user.name and/or user.email are not configured.")
            all_ok = False
    else:
        print(f" {RED}[✗]{RESET} Git configurations cannot be verified (Git missing).")
        all_ok = False
        
    # 4. Git connection check
    git_conn_ok = False
    if git_installed:
        print("Checking remote Git connection... ", end="", flush=True)
        try:
            res = subprocess.run(
                ["git", "ls-remote", "https://github.com/github/gitignore.git", "HEAD"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            if res.returncode == 0:
                git_conn_ok = True
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
            
        print("\r" + " " * 45 + "\r", end="")
        if git_conn_ok:
            print(f" {GREEN}[✓]{RESET} Git connection is active (successfully contacted remote).")
        else:
            print(f" {RED}[✗]{RESET} Git connection failed. Please check internet connection/git settings.")
            all_ok = False
    else:
        print(f" {RED}[✗]{RESET} Git connection check skipped (Git missing).")
        all_ok = False
            
    if not all_ok:
        print(f"\n{BOLD}{RED}[ERROR] System check failed. Please resolve the missing setups before running GitGarden:{RESET}")
        
        # Guide for Git Installation Failure
        if not git_installed:
            print(f"\n{BOLD}{YELLOW}1. Install Git:{RESET}")
            print("   - macOS: Install via Homebrew: brew install git")
            print("            or Xcode Command Line Tools: xcode-select --install")
            print("   - Windows: Download & install from https://git-scm.com")
            print("   - Linux (Ubuntu/Debian): sudo apt update && sudo apt install git")
            
        # Guide for Git Configuration Failure
        if git_installed and not git_config_ok:
            print(f"\n{BOLD}{YELLOW}2. Configure your Git Identity:{RESET}")
            print("   Run the following commands in your terminal to set up your commit author details:")
            print("   git config --global user.name \"Your Name\"")
            print("   git config --global user.email \"your.email@example.com\"")
            
        # Guide for Connection Failure
        if git_installed and not git_conn_ok:
            print(f"\n{BOLD}{YELLOW}3. Fix Git Connection / Authentication:{RESET}")
            print("   - Ensure you are connected to the internet.")
            print("   - If using SSH, ensure your SSH key is added to GitHub: ssh -T git@github.com")
            print("   - Verify that proxy settings or firewalls aren't blocking Git network traffic.")
            
        print()
        sys.exit(1)


def main():
    """Main execution flow for GitGarden. Prompts for configuration, builds repository, and generates commits."""
    perform_system_checks()
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="GitGarden - Fake Commit Generator for GitHub")
        parser.add_argument("-r", "--repo", required=True, help="Repository URL")
        parser.add_argument("-b", "--branch", default="master", help="Branch name (default: master)")
        parser.add_argument("-c", "--commits", default="", help="Commits per day (default: Random)")
        parser.add_argument("-f", "--file", default="py", help="File extension (default: py)")
        
        # Calculate default dates
        today = datetime.now()
        try:
            last_year = today.replace(year=today.year - 1)
        except ValueError:
            from datetime import timedelta
            last_year = today - timedelta(days=365)
        default_start_str = last_year.strftime("%d-%m-%Y")
        default_end_str = today.strftime("%d-%m-%Y")
        
        parser.add_argument("-s", "--start-date", default=default_start_str, help=f"Start Date (DD-MM-YYYY) [Default: {default_start_str}]")
        parser.add_argument("-e", "--end-date", default=default_end_str, help=f"End Date (DD-MM-YYYY) [Default: {default_end_str}]")
        parser.add_argument("-d", "--skip-days", default="", help="Days to skip (comma-separated, e.g. Saturday, Sunday) [Default: None]")
        parser.add_argument("-p", "--push-strategy", choices=["daily", "end"], default="daily", help="Push strategy: daily or end (default: daily)")
        
        args = parser.parse_args()
        
        config_manager = GitGardenConfig()
        
        repo = args.repo.strip()
        if not repo:
            print(f"{BOLD}{RED}[ERROR] Repository URL is mandatory.{RESET}")
            sys.exit(1)
            
        config_manager.repository = repo
        config_manager.branch = args.branch
        config_manager.commits = args.commits
        config_manager.file = args.file
        
        # Validate starting date
        try:
            start_year, start_month, start_day = config_manager._parse_and_validate_date(args.start_date)
            config_manager.starting_date = f"{start_day:02d}-{start_month:02d}-{start_year}"
        except ValueError as e:
            print(f"{BOLD}{RED}[ERROR] Start date: {e}{RESET}")
            sys.exit(1)
            
        # Validate ending date and verify order
        try:
            end_year, end_month, end_day = config_manager._parse_and_validate_date(args.end_date)
            start_dt = datetime(start_year, start_month, start_day)
            end_dt = datetime(end_year, end_month, end_day)
            if end_dt <= start_dt:
                print(f"{BOLD}{RED}[ERROR] End date must be after start date.{RESET}")
                sys.exit(1)
            config_manager.ending_date = f"{end_day:02d}-{end_month:02d}-{end_year}"
        except ValueError as e:
            print(f"{BOLD}{RED}[ERROR] End date: {e}{RESET}")
            sys.exit(1)
            
        # Parse skip days
        valid_weekdays = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
        skipped = []
        if args.skip_days:
            import re
            parts = re.split(r'[,\s]+', args.skip_days.strip())
            for d in parts:
                cleaned = d.lower()
                if cleaned in valid_weekdays:
                    skipped.append(cleaned)
        config_manager.skip_days = skipped
        config_manager.push_strategy = args.push_strategy
        
        params = config_manager.declare_settings()
        config_manager.save_configs(params)
        
        print(f"\n{BOLD}{GREEN}-------------------------{RESET}")
        print(f"{BOLD}{CYAN} Repo:         {RESET} {params['repository']}")
        print(f"{BOLD}{CYAN} Branch:       {RESET} {params['branch']}")
        print(f"{BOLD}{CYAN} Commits/day:  {RESET} {'Random' if params['commits'] == '' else params['commits']}")
        print(f"{BOLD}{CYAN} File type:    {RESET} .{params['file']}")
        print(f"{BOLD}{CYAN} Date range:   {RESET} {config_manager.starting_date} to {config_manager.ending_date}")
        print(f"{BOLD}{CYAN} Skip days:    {RESET} {', '.join([d.capitalize() for d in params['skip_days']]) if params['skip_days'] else 'None'}")
        print(f"{BOLD}{CYAN} Push strategy:{RESET} {params['push_strategy']}")
        print(f"{BOLD}{GREEN}-------------------------{RESET}\n")
    else:
        params = GitGardenConfig().ask_configs(return_configs=True)

    start_date = read_date(params["starting_date"])
    stop_date = read_date(params["ending_date"])

    preview_graph(params, start_date, stop_date)

    try:
        confirm = input(f"{BOLD}{YELLOW}Do you want to proceed with generating commits? [y/n]: {RESET}").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)

    if confirm not in ("y", "yes"):
        print("Aborted.")
        sys.exit(0)

    system = DateChanger(starting_date=start_date, ending_date=stop_date)

    git = GitBuilder(directory=FILES_DIR)

    git.init_repository()

    git.set_remote_repository(params["repository"])

    time_records = []
    day_counter = 0
    push_strategy = params.get("push_strategy", "end")

    skip_days = params.get("skip_days", [])

    while system.current_iteration_day != system.ending_date:

        starting_time = time.time()

        current_day_name = system.current_iteration_day.strftime("%A").lower()
        if current_day_name in skip_days:
            system.next_day()
            day_counter += 1
            continue

        date = system.change_date()

        for _ in range(git.get_commits_number()):

            git.execute(push=False, date=date)

        if push_strategy == "daily":
            git.push()

        system.next_day()

        time_records.append(time.time() - starting_time)

        approx_time = round(
            int(statistics.mean(time_records) * (system.days - day_counter)) / 60, 2
        )
        print(f"{BOLD}{CYAN}Progress: {day_counter + 1}/{system.days} days | Est. remaining: {approx_time}m{RESET}", end="\r")

        day_counter += 1

    print(f"\n{BOLD}{GREEN}[SUCCESS] Commits generated successfully.{RESET}")

    if push_strategy == "end":
        print(f"{BOLD}{CYAN}Pushing all commits to the remote repository...{RESET}")
        git.push()


def read_date(date: str):
    """Parses date string of formats DD-MM-YYYY, DD/MM/YYYY, or DD, M, YYYY into a tuple of ints (year, month, day)."""
    clean_str = date.strip()
    for separator in (",", "-", "/"):
        if separator in clean_str:
            parts = [p.strip() for p in clean_str.split(separator)]
            if len(parts) == 3:
                try:
                    # Parts are: day, month, year
                    return (int(parts[2]), int(parts[1]), int(parts[0]))
                except ValueError:
                    pass
    raise ValueError(f"Could not parse date: '{date}'. Use format DD-MM-YYYY, DD/MM/YYYY, or DD, M, YYYY.")

if __name__ == "__main__":
    main()
