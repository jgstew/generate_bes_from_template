"""test generate_bes_from_template"""
# pylint: disable=import-error,wildcard-import,undefined-variable,wrong-import-position,unused-wildcard-import

import argparse
import os.path
import sys


# don't create bytecode for tests because it is cluttery in python2
sys.dont_write_bytecode = True

# check for --test_pip arg
parser = argparse.ArgumentParser()
parser.add_argument("--test_pip", help="to test package installed with pip",
                    action="store_true")
args = parser.parse_args()

if not args.test_pip:
    # add module folder to import paths for testing local src
    sys.path.append(
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
    )
    # reverse the order so we make sure to get the local src module
    sys.path.reverse()

from generate_bes_from_template import *

# pylint: disable=line-too-long
assert str(action_prefetch_from_template.main()) == (
    "prefetch LGPO.zip sha1:0c74dac83aed569607aaa6df152206c709eef769 size:815660 https://download.microsoft.com/download/8/5/C/85C25433-A1B0-4FFA-9429-7E023E7DA8D8/LGPO.zip sha256:6ffb6416366652993c992280e29faea3507b5b5aa661c33ba1af31f48acea9c4"
)
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
assert str(action_createfile_from_file.main()).startswith(
    """delete __createfile

// --- START of contents of action_createfile_from_file.py ------------
createfile until __END_OF_FILE__
#!/usr/local/python
"""
)