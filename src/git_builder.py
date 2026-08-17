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
        self.directory = Path(directory)
        self.git_dir = self.directory.parent
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

    def _run_git_command(self, cmd_args, env=None, error_msg="Error executing git command"):
        import subprocess
        import sys
        
        run_env = os.environ.copy()
        if env:
            run_env.update(env)
            
        res = subprocess.run(
            cmd_args,
            cwd=self.git_dir,
            env=run_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode != 0:
            print(f"\n{BOLD}{RED}[ERROR] {error_msg}{RESET}")
            if res.stderr.strip():
                print(f"{YELLOW}Git error output:{RESET}\n{res.stderr.strip()}")
            if res.stdout.strip():
                print(f"{YELLOW}Git output:{RESET}\n{res.stdout.strip()}")
            sys.exit(1)
        return res

    def init_repository(self):
        """Initializes a new git repository in the workspace."""
        os.makedirs(self.directory, exist_ok=True)
        git_sub_dir = self.directory / ".git"
        if git_sub_dir.exists():
            import shutil
            shutil.rmtree(git_sub_dir)
        self._run_git_command(["git", "init"], error_msg="Failed to initialize git repository. Please ensure Git is installed.")
        self._run_git_command(["git", "checkout", "-B", self.branch], error_msg=f"Failed to set local branch to '{self.branch}'.")

    def set_remote_repository(self, repo):
        """Sets the git remote origin URL for pushing commits."""
        import subprocess
        os.makedirs(self.directory, exist_ok=True)
        res = subprocess.run(
            ["git", "remote", "add", "origin", repo],
            cwd=self.git_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode != 0:
            res2 = subprocess.run(
                ["git", "remote", "set-url", "origin", repo],
                cwd=self.git_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if res2.returncode != 0:
                print(f"\n{BOLD}{RED}[ERROR] Failed to set remote repository. Please check your repository URL: {repo}{RESET}")
                if res2.stderr.strip():
                    print(f"{YELLOW}Git error output:{RESET}\n{res2.stderr.strip()}")
                import sys
                sys.exit(1)

    def add(self):
        """Stages all pending file modifications and untracked files to git."""
        self._run_git_command(["git", "add", "."], error_msg="Failed to stage files (git add).")

    def commit(self, message: str, date: str):
        """Commits changes with a specified commit message and custom author/committer date stamps."""
        env = {
            "GIT_AUTHOR_DATE": date,
            "GIT_COMMITTER_DATE": date
        }
        self._run_git_command(
            ["git", "commit", f"--date={date}", "-m", message],
            env=env,
            error_msg="Failed to commit changes. Please check git configurations."
        )

    def push(self):
        """Pushes the commits to the remote branch on the git origin."""
        self._run_git_command(
            ["git", "push", "origin", self.branch],
            error_msg=f"Failed to push to branch '{self.branch}'. Please check remote repository settings and authentication."
        )

    def execute(self, date: str, push=True):
        """Generates a dummy file, stages it, commits it under a specific date, and optionally pushes."""
        self.file_generator.create_file(self.directory)
        self.add()
        comment = self.comment_generator.comment()
        self.commit(message=comment, date=date)
        if push:
            self.push()
