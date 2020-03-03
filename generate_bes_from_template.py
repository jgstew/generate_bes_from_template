#!/usr/local/python
"""
generate-bes-from-template.py

Created by James Stewart (@JGStew) on 2020-03-03.
"""

# get python dictionary with config items
from examples.task_example_data import template_dict


def main():
    """Only called if this script is run directly"""
    print(template_dict)

# if called directly, then run this example:
if __name__ == '__main__':
    main()
