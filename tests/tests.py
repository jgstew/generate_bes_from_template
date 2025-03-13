"""test generate_bes_from_template"""

# pylint: disable=import-error,wildcard-import,undefined-variable,wrong-import-position,unused-wildcard-import,consider-using-f-string

import argparse
import os.path
import sys

# don't create bytecode for tests because it is cluttery in python2
sys.dont_write_bytecode = True

# check for --test_pip arg
parser = argparse.ArgumentParser()
parser.add_argument(
    "--test_pip", help="to test package installed with pip", action="store_true"
)
args = parser.parse_args()

if not args.test_pip:
    # add module folder to import paths for testing local src
    sys.path.append(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
    )
    # reverse the order so we make sure to get the local src module
    sys.path.reverse()

from generate_bes_from_template import *

tests_count = 0  # pylint: disable=invalid-name

# print(action_prefetch_from_template.__file__)

# make sure we are testing the right place:
if args.test_pip:
    # this will false positive on windows
    assert "/src/" not in action_prefetch_from_template.__file__
else:
    # check for only 'src' so it will work on windows and non-windows
    assert "src" in action_prefetch_from_template.__file__


def test_partials(partials_path="."):
    """test mustache template partials"""
    print("test_partials()")
    script_folder = os.path.dirname(os.path.abspath(__file__))
    template_file_path = os.path.join(script_folder, "TemplateExample.mustache")
    result = generate_bes_from_template.generate_content_from_template(  # pylint: disable=unexpected-keyword-arg
        {}, template_file_path, partials_path=partials_path
    )
    return result


# pylint: disable=line-too-long
assert str(action_prefetch_from_template.main()) == (
    "prefetch LGPO.zip sha1:0c74dac83aed569607aaa6df152206c709eef769 size:815660 https://download.microsoft.com/download/8/5/C/85C25433-A1B0-4FFA-9429-7E023E7DA8D8/LGPO.zip sha256:6ffb6416366652993c992280e29faea3507b5b5aa661c33ba1af31f48acea9c4"
)
tests_count += 1
assert str(generate_bes_from_template.main()).startswith(
    """<?xml version="1.0" encoding="UTF-8"?>
<BES xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="BES.xsd">
	<Task>
		<Title>Example Generated From Template</Title>
		<Description><![CDATA[ This Task was generated automatically! ]]></Description>
				<Relevance><![CDATA[ Comment: Always False */ FALSE /* This example doesn't do anything, so it is always false. ]]></Relevance>
				<Relevance><![CDATA[ TRUE ]]></Relevance>
						<Category></Category>
		<DownloadSize>9999</DownloadSize>
		<Source>Internal</Source>
		<SourceID><![CDATA[JGStew]]></SourceID>
"""
)
tests_count += 1
assert str(action_createfile_from_file.main()).startswith(
    """delete __createfile

// --- START of contents of action_createfile_from_file.py ------------
createfile until __END_OF_FILE__
#!/usr/local/python
"""
)
tests_count += 1

if not args.test_pip:
    script_folder_path = os.path.dirname(os.path.abspath(__file__))
    # print(test_partials(script_folder_path))
    assert str(test_partials(script_folder_path)).startswith("Hello, World!")
    tests_count += 1
    assert str(test_partials(script_folder_path)).startswith(
        "Hello, World! You can load partials from a folder!"
    )
    tests_count += 1

# tests pass, return 0:
print("-------------------------------------")
print("Success: %d Tests pass" % tests_count)
print("")
sys.exit(0)
