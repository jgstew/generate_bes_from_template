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

PYSTACHE_TEMPLATE_CREATEFILE = """\
delete __createfile

createfile until {{{token_end_of_file}}}
{{{file_contents}}}
{{{token_end_of_file}}}

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

    # default token for end of file if not included
    if 'token_end_of_file' not in template_dict:
        template_dict['token_end_of_file'] = '_END_OF_FILE_'

    # https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
    try:
        with open(file_path, "rt") as file_read:
            # need to escape `{` for BigFix CreateFile command
            template_dict['file_contents'] = file_read.read().replace('{', '{{')
    except UnicodeDecodeError:
        return "ERROR: UnicodeDecodeError - bad file"

    # make sure file contents does not contain END_OF_FILE token
    while template_dict['token_end_of_file'] in template_dict['file_contents']:
        template_dict['token_end_of_file'] = "_" + template_dict['token_end_of_file'] + "_"

    return pystache.render(PYSTACHE_TEMPLATE_CREATEFILE, template_dict)

def main():
    """Only called if this script is run directly"""
    # use this script itself as the demo createfile
    print(action_createfile_from_file("action_createfile_from_file.py"))

# if called directly, then run this example:
if __name__ == '__main__':
    main()
