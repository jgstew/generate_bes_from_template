#!/usr/local/python
"""
generate-bes-from-template.py

Created by James Stewart (@JGStew) on 2020-03-03.
"""

from __future__ import absolute_import

import os
import pystache

def generate_bes_from_template(template_dict):
    """Generate BES XML file from info in template_dict hash table"""
    file_path = template_dict['template_file_path']
    # check if template file exists and readable:
    if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
        # run render of template, return result:
        return pystache.Renderer().render_path(file_path, template_dict)
    else:
        return "ERROR: No Template File Found!"


def main():
    """Only called if this script is run directly"""
    # get python dictionary with example config items
    #from examples.task_example_data import template_dict
    template_dict = {
                'template_file_path': 'examples/TEMPLATE_TASK.bes',
                'title': 'Example Generated From Template!',
                'download_size': 9999,
                'prefetch': 'prefetch file.txt',
                'action_script':
                """
delete /tmp/file.txt
copy __Download/file.txt /tmp/file.txt
"""
                }
    print(template_dict)
    print(generate_bes_from_template(template_dict))

# if called directly, then run this example:
if __name__ == '__main__':
    main()
