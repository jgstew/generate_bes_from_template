#!/usr/local/python
"""
action_createfile_from_file.py

Created by James Stewart (@JGStew) on 2020-03-11.

Related:
  - https://bigfix.me/relevance/details/3022868
"""
from __future__ import absolute_import

import os.path

# import pystache
import chevron  # pylint: disable=import-error

PYSTACHE_TEMPLATE_CREATEFILE = """\
delete __createfile

// --- START of contents of {{{file_name}}} ------------
createfile until {{{token_end_of_file}}}
{{{file_contents}}}
{{{token_end_of_file}}}
// --- END of contents of {{{file_name}}} ------------

delete "{{{file_path_destination}}}"
copy __createfile "{{{file_path_destination}}}"
"""


def action_createfile_from_file(file_path, file_path_destination=None):
    """Read text file, turn into BigFix Action CreateFile Command"""
    template_dict = {}
    if not file_path_destination:
        template_dict["file_path_destination"] = file_path
    else:
        template_dict["file_path_destination"] = file_path_destination

    # default token for end of file if not included
    if "token_end_of_file" not in template_dict:
        template_dict["token_end_of_file"] = "_END_OF_FILE_"

    if "file_name" not in template_dict:
        template_dict["file_name"] = get_filename_from_pathname(
            template_dict["file_path_destination"]
        )  # pylint: disable=line-too-long

    # https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
    try:
        with open(file_path, "rt") as file_read:
            # need to escape `{` for BigFix CreateFile command
            template_dict["file_contents"] = file_read.read().replace("{", "{{")
    except UnicodeDecodeError:
        return "ERROR: UnicodeDecodeError - bad file"

    # make sure file contents does not contain END_OF_FILE token
    while template_dict["token_end_of_file"] in template_dict["file_contents"]:
        template_dict["token_end_of_file"] = (
            "_" + template_dict["token_end_of_file"] + "_"
        )

    return chevron.render(PYSTACHE_TEMPLATE_CREATEFILE, template_dict)


def get_filename_from_pathname(pathname):
    """splits the filename from end of string after path separators including }"""
    # https://github.com/jgstew/tools/blob/master/Python/get_filename_from_pathname.py
    return pathname.replace("\\", "/").replace("}", "/").split("/")[-1]


def main():
    """Only called if this script is run directly"""
    # use this script itself as the demo createfile
    output_string = action_createfile_from_file(os.path.abspath(__file__))
    print(output_string)
    return output_string


# if called directly, then run this example:
if __name__ == "__main__":
    main()
