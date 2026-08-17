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
import random
import os
import json
import shlex
from .comment_builder import CommentBuilder
from .file_builder import FileBuilder

BLANK = ""
CONFIG = "config.json"

# ANSI escape codes for styling
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = ""
RESET = "\033[0m"


class GitBuilder:
    """Handles git operations including initialization, staging, committing, and pushing."""

    def __init__(self, directory, files="."):
        self.comment_generator = CommentBuilder()
        self.file_generator = FileBuilder()
        self.directory = directory
        self.filepath = Path(__file__).parents[0]
        self.cfgs = self.read_configs()
        self.branch = self.cfgs["branch"]
        self.files = files

    @staticmethod
    def random_commits(n=25):
        """Generates a random number of commits to execute on a single day, up to n."""
        return random.randint(1, n)

    def read_configs(self):
        """Reads configuration options from the local config.json file."""
        with open(self.filepath / "cfg" / CONFIG, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_commits_number(self):
        """Gets the configured number of commits per day, falling back to random if not set or invalid."""
        if not self.cfgs["commits"] == BLANK:
            try:
                return int(self.cfgs["commits"])

            except Exception:
                print(f"\n{BOLD}{YELLOW}[WARN] Invalid commit count in config. Defaulting to random commits.{RESET}")

        return self.random_commits()

    def init_repository(self):
        """Initializes a new git repository in the workspace."""
        command = "git init >/dev/null 2>&1"
        status = os.system(command)
        if status != 0:
            print(f"\n{BOLD}{RED}[ERROR] Failed to initialize git repository. Please ensure Git is installed.{RESET}")
            import sys
            sys.exit(1)

    def set_remote_repository(self, repo):
        """Sets the git remote origin URL for pushing commits."""
        command = f"git remote add origin {repo} >/dev/null 2>&1 || git remote set-url origin {repo} >/dev/null 2>&1"
        status = os.system(command)
        if status != 0:
            print(f"\n{BOLD}{RED}[ERROR] Failed to set remote repository. Please check your repository URL: {repo}{RESET}")
            import sys
            sys.exit(1)

    def add(self):
        """Stages all pending file modifications and untracked files to git."""
        command = "git add . >/dev/null 2>&1"
        status = os.system(command)
        if status != 0:
            print(f"\n{BOLD}{RED}[ERROR] Failed to stage files (git add).{RESET}")
            import sys
            sys.exit(1)

    def commit(self, message: str, date: str):
        """Commits changes with a specified commit message and custom author/committer date stamps."""
        quoted_date = shlex.quote(date)
        quoted_message = shlex.quote(message)
        command = (
            f"GIT_AUTHOR_DATE={quoted_date} "
            f"GIT_COMMITTER_DATE={quoted_date} "
            f"git commit --date={quoted_date} -m {quoted_message} >/dev/null 2>&1"
        )
        status = os.system(command)
        if status != 0:
            print(f"\n{BOLD}{RED}[ERROR] Failed to commit changes. Please check git configurations.{RESET}")
            import sys
            sys.exit(1)

    def push(self):
        """Pushes the commits to the remote branch on the git origin."""
        command = f"git push origin {self.branch}"
        status = os.system(f"{command} >/dev/null 2>&1")
        if status != 0:
            print(f"\n{BOLD}{RED}[ERROR] Failed to push to branch '{self.branch}'. Please check remote repository settings and authentication.{RESET}")
            import sys
            sys.exit(1)

    def execute(self, date: str, push=True):
        """Generates a dummy file, stages it, commits it under a specific date, and optionally pushes."""
        self.file_generator.create_file(self.directory)
        self.add()
        comment = self.comment_generator.comment()
        self.commit(message=comment, date=date)
        if push:
            self.push()
