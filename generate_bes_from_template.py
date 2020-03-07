#!/usr/local/python
"""
generate-bes-from-template.py

Created by James Stewart (@JGStew) on 2020-03-03.
"""

from __future__ import absolute_import

import os
import datetime

import pystache

def generate_bes_from_template(template_dict):
    """Generate BES XML file from info in template_dict hash table"""
    file_path = template_dict['template_file_path']
    # check if template file exists and readable:
    if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
        if not 'SourceReleaseDate' in template_dict:
            template_dict['SourceReleaseDate'] = yyyymmdd()
        if not 'x-fixlet-modification-time' in template_dict:
            template_dict['x-fixlet-modification-time'] = fixlet_modification_time()
        # run render of template, return result:
        return pystache.Renderer().render_path(file_path, template_dict)
    return "ERROR: No Template File Found!"

def yyyymmdd(separator="-", date_to_format=datetime.datetime.today()):
    """By default, get YYYY-MM-DD of today in local time zone"""
    return date_to_format.strftime('%Y' + separator + '%m' + separator + '%d')

def fixlet_modification_time(date_to_format=datetime.datetime.now(datetime.timezone.utc)):
    """By default, get the bigfix fixlet format of time of now in UTC
    Example: Tue, 03 Mar 2020 19:37:59 +0000"""
    return date_to_format.strftime('%a, %d %b %Y %H:%M:%S %z')

def main():
    """Only called if this script is run directly"""
    # get python dictionary with example config items
    #from examples.task_example_data import template_dict
    template_dict = {
                'template_file_path': 'examples/TEMPLATE_TASK.bes',
                'Title': 'Example Generated From Template',
                'Description': 'This Task was generated automatically!',
                'Relevance': """ Comment: Always False */ FALSE ; \
/* This example doesn't do anything, so it is always false. """,
                'DownloadSize': 9999,
                'SourceID': 'JGStew',
                'prefetch': 'prefetch file.txt',
                'action_script':
                """
delete /tmp/file.txt
copy __Download/file.txt /tmp/file.txt
"""
                }
    #print(template_dict)
    print(generate_bes_from_template(template_dict))

# if called directly, then run this example:
if __name__ == '__main__':
    main()
