#!/usr/local/python
"""
action_createfile_from_file.py

Created by James Stewart (@JGStew) on 2020-03-11.
"""
from __future__ import absolute_import

import os

import pystache

def action_createfile_from_file(file_path, file_path_destination=None):
    """Read text file, turn into BigFix Action CreateFile Commnad"""
    if not file_path_destination:
        file_path_destination = file_path
    # https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python

    file_contents = ""
    try:
        with open(file_path, "rt") as file_read:
            file_contents = file_read.read()
    except UnicodeDecodeError:
        return "ERROR: UnicodeDecodeError - bad file"

    return file_contents

def main():
    """Only called if this script is run directly"""
    print(action_createfile_from_file("action_createfile_from_file.py"))

# if called directly, then run this example:
if __name__ == '__main__':
    main()