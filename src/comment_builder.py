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

import json
import os
import random
from pathlib import Path

COMMENTS = "comments.json"

class CommentBuilder:
    """Loads and randomly selects commit comments from a configuration file."""

    def __init__(self):

        self.filepath = Path(__file__).parents[0]
        self.cfg_path = self.filepath / "cfg"
        self.comments_file = self.cfg_path / COMMENTS
        self.comments = self.load_comments()

    def comments_file_exists(self):
        """Checks if the comments configuration file exists."""
        return os.path.exists(self.comments_file)

    def load_comments(self):
        """Loads commit messages from comments.json or falls back to a generic message."""
        if self.comments_file_exists():
            with open(self.comments_file, "r", encoding="utf-8") as file:
                return json.load(file)["comments"]
        return self.generic_comment()

    def generic_comment(self):
        """Returns a list with a single default fallback commit message."""
        return ["Fix( comments.json is not working, fix it )"]

    def comment(self):
        """Selects and returns a random commit message from the loaded comments."""
        return random.choice(self.comments)
