"""
Example python script to generate .bes files for windows msi content
"""
import os.path

# pylint: disable=invalid-name,wrong-import-position
import sys

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)

from generate_bes_from_template import (
    generate_bes_from_template,  # pylint: disable=import-error
)


def main():
    """run this by default"""
    template_dict = {
        "DisplayName": "Slack",
        "version": "4.26.0",
        "DownloadSize": 102719488,
        "file_name": "slack-standalone.msi",
        "prefetch": "prefetch slack-standalone.msi sha1:f811b9c138886a2f05c21b62bf198b94bd0582a9 size:102719488 https://downloads.slack-edge.com/releases/windows/4.26.0/prod/x64/slack-standalone-4.26.0.0.msi sha256:4e3c3403901f1b7b8b39e7c7cb6e1dd124c74a8bd05277d5ca57d0e80280eb91",
    }
    template_dict = generate_bes_from_template.get_missing_bes_values(template_dict)

    print("\ntemplate_dict:", template_dict, "\n")

    # os.path.join(   os.path.dirname(os.path.abspath(__file__)), "Uninstall_MSI-Windows.bes.mustache" )
    templates = {
        "Install": os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "Example-Win-Install-MSI.bes.mustache",
        ),
        "Update": os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "Example-Win-Update-MSI.bes.mustache",
        ),
        "InstallUpdate": os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "Example-Win-InstallUpdate-MSI.bes.mustache",
        ),
        "Uninstall": os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "Uninstall_MSI-Windows.bes.mustache",
        ),
    }

    # print(templates)
    for key, value in templates.items():
        print(key, "template:", value)
        generated_task = generate_bes_from_template.generate_content_from_template(
            template_dict, template_file_path=value
        )
        # print(generated_task)

        # Write output to BES files: (need to implement)
        print(template_dict["DisplayName"] + "-" + key + ".bes")
        with open(
            (template_dict["DisplayName"] + "-" + key + ".bes"),
            "wb",
        ) as bes_file:
            bes_file.write(generated_task.encode("utf-8"))


# if called directly, then run this example:
if __name__ == "__main__":
    main()
