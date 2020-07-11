

import xml.etree.ElementTree as ElementTree
import datetime

import sys
# add parent directory(s) to path search for python modules
sys.path.append('../')
sys.path.append('../../')


from bigfix_prefetch.prefetch_from_dictionary import *

#import bigfix_prefetch.url_to_prefetch

# https://github.com/jgstew/generate_bes_from_template
from generate_bes_from_template import generate_bes_from_template


def main():
    """Only called if this script is run directly"""

    xml_root = ElementTree.parse("../CatalogPC.xml")

    count = 0

    # https://stackoverflow.com/a/33280875/861745
    for elem in xml_root.findall("./SoftwareComponent/ComponentType[@value='BIOS']..."):
        print(elem.attrib['size'])
        print(elem.attrib['hashMD5'])
        print("http://downloads.dell.com/" + elem.attrib['path'])
        #print(elem.attrib['releaseDate'])
        print(datetime.datetime.strptime(elem.attrib['releaseDate'], '%b %d, %Y').strftime('%Y-%m-%d'))


        #prefetch_dictionary_result = url_to_prefetch.url_to_prefetch( "http://downloads.dell.com/" + elem.attrib['path'] , True )
        prefetch_dictionary_result = {'file_name': 'Latitude_5495_1.3.4.exe', 'file_size': 6154960, 'file_sha1': '3896f19d84c39d81af9db447043e2b048ab286f0', 'file_sha256': 'ab1ce685ba9c5162fadffca2f2e1d654f4b045334793446d6b1c91c0e62eea23', 'file_md5': '488d59fdd41345213f082bddbcad0be1', 'download_url': 'http://downloads.dell.com/FOLDER06217780M/1/Latitude_5495_1.3.4.exe'}
        print(prefetch_dictionary_result)

        # Check file size matches:
        if int(prefetch_dictionary_result['file_size']) != int(elem.attrib['size']):
            print("ERROR: file size from download doesn't match catalog")
            break
        # Check md5 hash matches:
        if prefetch_dictionary_result['file_md5'] != elem.attrib['hashMD5']:
            print("ERROR: file md5 hash from download doesn't match catalog")
            break


        template_dict = {
            'template_file_path': 'examples/TEMPLATE_BIOS_Update.bes',
            'vendor': 'Dell',
            'model': 'Latitude 5495',
            'bios_version': elem.attrib['vendorVersion'],
            'DownloadSize': elem.attrib['size'],
            'SourceReleaseDate': datetime.datetime.strptime(elem.attrib['releaseDate'], '%b %d, %Y').strftime('%Y-%m-%d')
        }
        template_dict['BIOS_Update_Prefetch'] = '\n' + prefetch_from_dictionary(prefetch_dictionary_result)
        template_dict['BIOS_Update_ActionScript'] = '\n' + 'waithidden __Download\\' + prefetch_dictionary_result['file_name'] + r' /s /l="{ pathname of folder "__BESData\__Global\Logs" of parent folder of client }\install_Dell_BIOS_Update.log"'
        print(template_dict)
        #print( generate_bes_from_template(template_dict) )
        with open("BIOS_Update_" + template_dict['vendor'] + "_" + template_dict['model'] + "_" + template_dict['bios_version'] +".bes", 'w') as filetowrite:
            filetowrite.write(generate_bes_from_template.generate_bes_from_template(template_dict))


        count += 1
        break

    #print(count)


# if called directly, then run this example:
if __name__ == '__main__':
    main()
