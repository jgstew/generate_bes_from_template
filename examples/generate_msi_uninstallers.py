"""
Generate MSI Uninstallers from template.

Build into binary:
pyinstaller generate_msi_uninstallers.py --collect-all besapi --noconfirm --add-data "./Uninstall_MSI-Windows.bes.mustache;./" --clean --onefile --noupx
"""

import os

import bescli
import generate_bes_from_template

# DisplayNames of MSI Applications - Windows
# - https://bigfix.me/relevance/details/3023371
# Evaluate Every: 1 day
# if (windows of operating system AND (if exists property whose(it as string contains "in proxy agent context") then NOT in proxy agent context else TRUE)) then ( unique values of (it as trimmed string) of (preceding text of first "%ae" of it | it) of (preceding text of first "Â" of it | it) of (preceding text of first "%a9" of it | it) of (preceding text of first "™" of it | it) of (it as string) of values "DisplayName" of keys whose(exists (values "UninstallString" of it; values "ModifyPath" of it) whose(it as string as lowercase contains "msiexec")) of keys "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" of (x64 registries; x32 registries) ) else NOTHINGS

# DisplayNames of non-MSI Applications - Windows
# - https://bigfix.me/relevance/details/3023370
# Evaluate Every: 1 day
# if (windows of operating system AND (if exists property whose(it as string contains "in proxy agent context") then NOT in proxy agent context else TRUE)) then ( unique values of items 0 of ( (it as trimmed string) of (preceding text of first "%ae" of it | it) of (preceding text of first "Â" of it | it) of (preceding text of first "%a9" of it | it) of (preceding text of first "™" of it | it) of (it as string)  of values "DisplayName" of it, value "UninstallString_Hidden" of it | value "QuietUninstallString" of it | value "UninstallString" of it) whose(item 1 of it as string as trimmed string != "") of keys whose(exists (values "UninstallString" of it; values "QuietUninstallString" of it; values "UninstallString_Hidden" of it) AND not exists (values "UninstallString" of it; values "ModifyPath" of it) whose(it as string as lowercase contains "msiexec")) of keys "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" of (x64 registries; x32 registries) ) else NOTHINGS

# get property name:
# unique value of names of bes properties whose(custom flag of it AND name of it contains "DisplayName" AND definition of it contains "ModifyPath")

# get unique property values: (where the property is named `DisplayNames of MSI Applications - Windows`)
# unique values of values of results of bes property "DisplayNames of MSI Applications - Windows"


# this function will be moved within BESAPI itself in the future:
def save_item_to_besfile(
    xml_string, export_folder="./", name_trim=100,
):
    """save an xml string to bes file"""
    item_folder = export_folder
    if not os.path.exists(item_folder):
        os.makedirs(item_folder)

    content_obj = bescli.bescli.besapi.RESTResult.objectify_text(None, xml_string)
    # get first tag in XML that is the Type
    content_type_tag = list(content_obj.__dict__.keys())[0]
    item = content_obj[content_type_tag]
    item_path = item_folder + "/%s.bes" % bescli.bescli.besapi.sanitize_txt(
        item.Title.text[:name_trim],
    )
    item_path = item_path.replace("//", "/")
    with open(item_path, "wb",) as bes_file:
        bes_file.write(xml_string.encode("utf-8"))
    return item_path


def main():
    """run this by default"""
    bigfix_cli = bescli.bescli.BESCLInterface()
    bigfix_cli.do_conf()
    # generate MSI uninstallers
    # use session relevance to get the name of the property to get the values from:
    property_name = bigfix_cli.bes_conn.session_relevance_array(
        'unique value of names of bes properties whose(custom flag of it AND name of it contains "DisplayName" AND definition of it contains "ModifyPath")'
    )[0]
    # print help messages if property not found:
    if "ERROR:" in property_name:
        print("ERROR: Property not found!", property_name)
        print("You may need to create the property that this script uses")
        print(
            "- Recommended Property Name: `DisplayNames of MSI Applications - Windows`"
        )
        print("- Recommended Property Evaluation Period: Once a day")
        print(
            "- Recommended Property Relevance found here: https://bigfix.me/relevance/details/3023371"
        )
        raise ValueError("ERROR: Property not found!", property_name)
    # get the unique set of property results to generate the MSI installers for:
    property_results = bigfix_cli.bes_conn.session_relevance_array(
        f'unique values of values of results of bes property "{property_name}"'
    )
    # print(property_results)
    template_dict = {}
    template_dict["DownloadSize"] = "0"
    template_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "Uninstall_MSI-Windows.bes.mustache"
    )

    template_dict["template_file_path"] = template_file_path
    template_dict = generate_bes_from_template.generate_bes_from_template.get_missing_bes_values(
        template_dict
    )
    # print(template_dict)

    for result in property_results:
        # print(result)
        # generate the uninstallers:
        template_dict["DisplayName"] = result

        generated_task = generate_bes_from_template.generate_bes_from_template.generate_content_from_template(
            template_dict
        )
        print(save_item_to_besfile(generated_task))

    # generate EXE uninstallers:
    template_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "Uninstall_EXE-Windows.bes.mustache"
    )
    template_dict["template_file_path"] = template_file_path
    property_name = bigfix_cli.bes_conn.session_relevance_array(
        'unique value of names of bes properties whose(custom flag of it AND name of it contains "DisplayName" AND definition of it contains "QuietUninstallString")'
    )[0]
    # print help messages if property not found:
    if "ERROR:" in property_name:
        print("ERROR: Property not found!", property_name)
        print("You may need to create the property that this script uses")
        print(
            "- Recommended Property Name: `DisplayNames of MSI Applications - Windows`"
        )
        print("- Recommended Property Evaluation Period: Once a day")
        print(
            "- Recommended Property Relevance found here: https://bigfix.me/relevance/details/3023371"
        )
        raise ValueError("ERROR: Property not found!", property_name)
    print(property_name)
    property_results = bigfix_cli.bes_conn.session_relevance_array(
        f'unique values of values of results of bes property "{property_name}"'
    )
    # print(property_results)
    for result in property_results:
        # print(result)
        # generate the uninstallers:
        template_dict["DisplayName"] = result

        generated_task = generate_bes_from_template.generate_bes_from_template.generate_content_from_template(
            template_dict
        )
        print(save_item_to_besfile(generated_task))


# if called directly, then run this example:
if __name__ == "__main__":
    main()
