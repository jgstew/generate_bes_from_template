"""
Generate MSI Uninstallers from template.
"""

import bescli

# import generate_bes_from_template


# get property name:
# unique value of names of bes properties whose(custom flag of it AND name of it contains "DisplayName" AND definition of it contains "ModifyPath")

# get unique property values: (where the property is named `DisplayNames of MSI Applications - Windows`)
# unique values of values of results of bes property "DisplayNames of MSI Applications - Windows"


def main():
    """run this by default"""
    print("Not yet implemented!")
    bigfix_cli = bescli.bescli.BESCLInterface()
    bigfix_cli.do_conf()
    property_name = bigfix_cli.bes_conn.session_relevance_array(
        'unique value of names of bes properties whose(custom flag of it AND name of it contains "DisplayName" AND definition of it contains "ModifyPath")'
    )[0]
    # print(property_name)
    property_results = bigfix_cli.bes_conn.session_relevance_array(
        f'unique values of values of results of bes property "{property_name}"'
    )
    # print(property_results)
    for result in property_results:
        print(result)
        # generate the uninstallers:


# if called directly, then run this example:
if __name__ == "__main__":
    main()
