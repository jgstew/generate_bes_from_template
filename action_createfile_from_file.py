#!/usr/local/python
"""
action_createfile_from_file.py

Created by James Stewart (@JGStew) on 2020-03-11.

Related:
  - https://bigfix.me/relevance/details/3022868
"""
from __future__ import absolute_import

#import os

import pystache

pystache_template_createfile = """\
delete __createfile

createfile until _END_OF_FILE_
{{{file_contents}}}
_END_OF_FILE_

delete "{{{file_path_destination}}}"
copy __createfile "{{{file_path_destination}}}"
"""

def action_createfile_from_file(file_path, file_path_destination=None):
    """Read text file, turn into BigFix Action CreateFile Commnad"""
    template_dict = {}
    if not file_path_destination:
        template_dict['file_path_destination'] = file_path
    else:
        template_dict['file_path_destination'] = file_path_destination
    # https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python

    #file_contents = ""
    try:
        with open(file_path, "rt") as file_read:
            template_dict['file_contents'] = file_read.read().replace('{', '{{')
    except UnicodeDecodeError:
        return "ERROR: UnicodeDecodeError - bad file"

    return pystache.render(pystache_template_createfile, template_dict)

def main():
    """Only called if this script is run directly"""
    # use this script itself as the demo createfile
    print(action_createfile_from_file("action_createfile_from_file.py"))

# if called directly, then run this example:
if __name__ == '__main__':
    main()
