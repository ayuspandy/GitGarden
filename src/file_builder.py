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

WORDS = "random_words.txt"
FILE_TXT = "file_txt.txt"
CONFIG = "config.json"

class FileBuilder:
    """Handles target file name generation, path checks, and populating file content."""

    def __init__(self):
        self.filepath = Path(__file__).parents[0]
        self.txt_path = self.filepath / "txt"
        self.words_file = self.txt_path / WORDS 
        self.file_txt = self.txt_path / FILE_TXT 
        self.words = self.read_text(self.words_file)
        self.file_text = self.read_text(self.file_txt)
        self.filename = None
        self.filetype = self.read_filetype()

    @staticmethod
    def path_exists(dirname):
        """Checks if a given path/directory exists on the filesystem."""
        return os.path.exists(dirname)

    @staticmethod
    def generate_extra_file(file, dirname):
        """Generates a file name with a unique counter suffix if the name is already taken."""
        _splited_file = file.split(".")
        same_name_files = [
            directory_file
            for directory_file in os.listdir(dirname)
            if _splited_file[0] in directory_file
        ]
        return f"{_splited_file[0]}{len(same_name_files) + 1}.{_splited_file[1]}"

    def write_new_file(self, filename):
        """Writes loaded lines from file_text to the specified output file path."""
        with open(filename, "w", encoding="utf-8") as file:
            for line in self.file_text:
                file.write(f"{line}\n")

    def read_filetype(self):
        """Reads and returns the desired file type extension from the configurations."""
        with open(self.filepath / "cfg" / CONFIG, "r", encoding="utf-8") as file:

            file_type = json.load(file)["file"]
            return file_type

    def file_in_path(self, dirname):
        """Checks if the currently set filename already exists in the given directory."""
        return os.path.exists(f"{dirname}/{self.filename}")

    def generate_name(self):
        """Generates a random filename using words from random_words.txt and the configured file extension."""
        self.filename = f"{random.choice(self.words)}.{self.filetype}"
        return self.filename

    def read_text(self, file):
        """Reads lines from a file and returns them as a list of strings, stripping newlines."""
        if self.path_exists(file):
            with open(file, "r", encoding="utf-8") as loaded_file:
                return [line.rstrip("\n") for line in loaded_file.readlines()]
        return ["file"]

    def create_file(self, dirname):
        """Creates a new code/text file with random words as the name and writes dummy content into it."""
        if self.path_exists(dirname):
            file = self.generate_name()
            if self.file_in_path(dirname):
                file = self.generate_extra_file(file, dirname)
            self.write_new_file(dirname / file)
