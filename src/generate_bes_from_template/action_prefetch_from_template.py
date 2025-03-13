#!/usr/local/python
"""
action_prefetch_from_template.py

Created by James Stewart (@JGStew) on 2020-03-14.

Related:
  - https://github.com/jgstew/generate_prefetch
  - https://github.com/jgstew/tools/blob/master/Python/url_to_prefetch.py
"""
from __future__ import absolute_import

# import pystache
import chevron  # pylint: disable=import-error

# import os


PYSTACHE_TEMPLATE_PREFETCH_STATEMENT = """\
prefetch {{{file_name_downloaded}}} sha1:{{{file_sha1}}} \
size:{{{file_size}}} {{{download_url}}} sha256:{{{file_sha256}}}\
"""

PYSTACHE_TEMPLATE_PREFETCH_BLOCK_ITEM = """\
add prefetch item name={{{file_name_downloaded}}} sha1={{{file_sha1}}} \
size={{{file_size}}} url={{{download_url}}} sha256={{{file_sha256}}}\
"""


def action_prefetch_from_template(
    template_dict,
    pystache_template=PYSTACHE_TEMPLATE_PREFETCH_STATEMENT,
):
    """
    returns a prefetch in a particular format based upon
     which template is passed in
    """
    # force SHA1 & SHA256 to be lowercase
    # remove commas and decimals from file_size
    # get file_name_downloaded from URL if not included
    return chevron.render(pystache_template, template_dict)


def main():
    """Only called if this script is run directly"""
    # use this script itself as the demo createfile
    template_dict = {
        "file_name_downloaded": "LGPO.zip",
        "download_url": "https://download.microsoft.com/download/8/5/C/85C25433-A1B0-4FFA-9429-7E023E7DA8D8/LGPO.zip",  # pylint: disable=line-too-long
        "file_size": "815660",
        "file_sha1": "0c74dac83aed569607aaa6df152206c709eef769",
        "file_sha256": "6ffb6416366652993c992280e29faea3507b5b5aa661c33ba1af31f48acea9c4",
    }
    print(
        action_prefetch_from_template(
            template_dict, PYSTACHE_TEMPLATE_PREFETCH_BLOCK_ITEM
        )
    )
    output_string = action_prefetch_from_template(template_dict)
    print(output_string)
    return output_string


# if called directly, then run this example:
if __name__ == "__main__":
    main()
