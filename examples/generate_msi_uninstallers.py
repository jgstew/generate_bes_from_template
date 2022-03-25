"""
Generate MSI Uninstallers from template.
"""

import os

import bescli
import generate_bes_from_template

# DisplayNames of MSI Applications - Windows
# - https://bigfix.me/relevance/details/3023371
# (DisplayNames, UninstallStrings) of non-MSI Applications - Windows
# - https://bigfix.me/relevance/details/3023370

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
    template_dict = {}
    template_dict["DownloadSize"] = "0"
    template_dict[
        "template_file_path"
    ] = "examples/Uninstall_ MSI - Windows.bes.mustache"
    template_dict = generate_bes_from_template.generate_bes_from_template.get_missing_bes_values(
        template_dict
    )
    # print(template_dict)
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
