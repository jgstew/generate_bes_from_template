"""
Generate Dell BIOS Update fixlets from catalog file

Requires:
pip install bigfix-prefetch
pip install generate-bes-from-template
pip install cabarchive
"""

import datetime
import os
import urllib.error

# pylint: disable=line-too-long,fixme,invalid-name,import-error,wildcard-import,undefined-variable,no-member,wrong-import-position
import xml.etree.ElementTree  # pylint: disable=consider-using-from-import

import cabarchive
from bigfix_prefetch import prefetch_from_dictionary  # noqa: F403
from bigfix_prefetch.prefetch_from_url import url_to_prefetch  # noqa: F403

# https://github.com/jgstew/generate_bes_from_template
from generate_bes_from_template import generate_bes_from_template


def main():
    """Only called if this script is run directly"""
    BUILD_DIRECTORY = "examples/build/"

    try:
        os.mkdir(BUILD_DIRECTORY)
    except FileExistsError:
        pass

    # delete the CatalogPC.cab file if it is older than 1 week
    # this is needed because the CatalogPC.cab file is updated frequently
    if os.path.exists(BUILD_DIRECTORY + "CatalogPC.cab"):
        file_mod_time = os.path.getmtime(BUILD_DIRECTORY + "CatalogPC.cab")
        if (
            datetime.datetime.now() - datetime.datetime.fromtimestamp(file_mod_time)
        ).days > 7:
            os.remove(BUILD_DIRECTORY + "CatalogPC.cab")
            print("Deleted old CatalogPC.cab file")

    # automatically download the newest Dell CatalogPC.cab file
    # https://downloads.dell.com/catalog/CatalogPC.cab
    if not os.path.exists(BUILD_DIRECTORY + "CatalogPC.cab"):
        url_to_prefetch(
            "https://downloads.dell.com/catalog/CatalogPC.cab",
            True,
            BUILD_DIRECTORY + "CatalogPC.cab",
        )

    # delete the CatalogPC.xml file so we can extract it again
    # this is needed because the CatalogPC.cab file is updated frequently
    # and we want to ensure we are using the latest version
    if os.path.exists(BUILD_DIRECTORY + "CatalogPC.xml"):
        os.remove(BUILD_DIRECTORY + "CatalogPC.xml")

    # extract the CatalogPC.cab file to the build directory
    with open(BUILD_DIRECTORY + "CatalogPC.cab", "rb") as f:
        cab_data = f.read()

    archive = cabarchive.CabArchive(cab_data)
    for filename, cab_file_obj in archive.items():
        output_path = os.path.join(BUILD_DIRECTORY, filename)
        with open(output_path, "wb") as outfile:
            outfile.write(cab_file_obj.buf)
        print(f"Extracted: {filename} to {output_path}")

    # parse the CatalogPC.xml file
    xml_root = xml.etree.ElementTree.parse(BUILD_DIRECTORY + "CatalogPC.xml")

    count = 0
    xml_bios_count = 0

    # https://stackoverflow.com/a/33280875/861745
    for elem in xml_root.findall(
        ".//SoftwareComponent/ComponentType[@value='BIOS']..."
    ):

        # skip windows 32bit BIOS updates
        if "_WN32_" in elem.attrib["path"]:
            continue

        xml_bios_count += 1

        # do not download file if generated task already exists
        file_exists = False
        # https://stackoverflow.com/questions/3964681/find-all-files-in-a-directory-with-extension-txt-in-python
        for file in os.listdir(BUILD_DIRECTORY):
            if file.endswith(elem.attrib["vendorVersion"] + ".bes"):
                # https://stackoverflow.com/questions/4940032/how-to-search-for-a-string-in-text-files
                with open(os.path.join(BUILD_DIRECTORY, file)) as f:
                    if elem.attrib["path"] in f.read():
                        file_exists = True
                        # print(os.path.join(BUILD_DIRECTORY, file))
                        break
        # if file found, skip this iteration
        if file_exists:
            # TODO: consider reading the prefetch from the existing file
            #           This would allow updating of the generated items without redownload
            continue

        # skip failed downloads
        try:
            prefetch_dictionary_result = url_to_prefetch(
                "https://downloads.dell.com/" + elem.attrib["path"], True
            )  # noqa: F405
        except urllib.error.HTTPError:
            continue
        # prefetch_dictionary_result = {'file_name': 'Latitude_5495_1.3.4.exe', 'file_size': 6154960, 'file_sha1': '3896f19d84c39d81af9db447043e2b048ab286f0', 'file_sha256': 'ab1ce685ba9c5162fadffca2f2e1d654f4b045334793446d6b1c91c0e62eea23', 'file_md5': '488d59fdd41345213f082bddbcad0be1', 'download_url': 'http://downloads.dell.com/FOLDER06217780M/1/Latitude_5495_1.3.4.exe'}
        # print(prefetch_dictionary_result)
        print(elem.attrib["vendorVersion"])
        # https://stackoverflow.com/a/32621106/861745
        print(
            datetime.datetime.strptime(
                elem.attrib["releaseDate"], "%B %d, %Y"
            ).strftime("%Y-%m-%d")
        )
        print(elem.attrib["size"])
        print(elem.attrib["hashMD5"])
        print("https://downloads.dell.com/" + elem.attrib["path"])

        # Check file size matches:
        if int(prefetch_dictionary_result["file_size"]) != int(elem.attrib["size"]):
            print("ERROR: file size from download doesn't match catalog")
            break
        # Check md5 hash matches:
        if prefetch_dictionary_result["file_md5"] != elem.attrib["hashMD5"]:
            print("ERROR: file md5 hash from download doesn't match catalog")
            break

        template_dict = {
            "template_file_path": "examples/TEMPLATE_BIOS_Update.bes",
            "vendor": "Dell",
            "DellBIOS": True,
            "bios_version": elem.attrib["vendorVersion"],
            "DownloadSize": elem.attrib["size"],
            "SourceReleaseDate": datetime.datetime.strptime(
                elem.attrib["releaseDate"], "%B %d, %Y"
            ).strftime("%Y-%m-%d"),
        }
        template_dict["BIOS_Update_Prefetch"] = (
            "\n"
            + prefetch_from_dictionary.prefetch_from_dictionary(
                prefetch_dictionary_result
            )
        )  # noqa: F405
        template_dict["BIOS_Update_ActionScript"] = (
            "\n"
            + "waithidden __Download\\"
            + prefetch_dictionary_result["file_name"]
            + r' /s{( (" /p=" & it) whose(length of it > 7) of (it as trimmed string) of (parameter "BIOS_Password" | "") | "" )} /l="{ pathname of folder "__BESData\__Global\Logs" of parent folder of client }\install_BIOS_Update.log"'
        )

        bios_dependency = elem.find(
            "./SupportedDevices/Device/Dependency[@componentType='BIOS']"
        )
        if bios_dependency is not None:
            template_dict["bios_version_minimum"] = bios_dependency.attrib["version"]

        # Read the model from the catalog. There can be more than 1 model per BIOS update
        for model_elem in elem.findall("./SupportedSystems/Brand"):
            print(
                model_elem.findtext("./Display")
                + " "
                + model_elem.findtext("./Model/Display")
            )
            # make a task for each model in the model string
            models = model_elem.findtext("./Model/Display").split("/")
            for model in models:
                template_dict["model"] = model_elem.findtext("./Display") + " " + model
                print(
                    BUILD_DIRECTORY
                    + "BIOS_Update_"
                    + template_dict["vendor"]
                    + "_"
                    + template_dict["model"]
                    + "_"
                    + template_dict["bios_version"]
                    + ".bes"
                )
                with open(
                    BUILD_DIRECTORY
                    + "BIOS_Update_"
                    + template_dict["vendor"]
                    + "_"
                    + template_dict["model"]
                    + "_"
                    + template_dict["bios_version"]
                    + ".bes",
                    "w",
                ) as filetowrite:
                    filetowrite.write(
                        generate_bes_from_template.generate_bes_from_template(
                            template_dict
                        )
                    )
        count += 1
    print(
        f"Done generating {count} Dell BIOS Update fixlets of {xml_bios_count} in XML."
    )


# if called directly, then run this example:
if __name__ == "__main__":
    main()
