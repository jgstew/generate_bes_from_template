
import sys

sys.path.append('../')
#sys.path.append('../../')

from generate_bes_from_template import generate_bes_from_template

log_array = ['Security', 'System', 'Application']

for log_name in log_array:
    template_dict = {}
    template_dict['template_file_path'] = "examples/TEMPLATE_Event_Logs_Retain-LOG-Windows.bes"
    template_dict['log_name'] = log_name
    template_dict['prefetch'] = \
"prefetch LGPO.zip sha1:0c74dac83aed569607aaa6df152206c709eef769 size:815660 \
https://download.microsoft.com/download/8/5/C/85C25433-A1B0-4FFA-9429-7E023E7DA8D8/LGPO.zip \
sha256:6ffb6416366652993c992280e29faea3507b5b5aa661c33ba1af31f48acea9c4"
    print(generate_bes_from_template.generate_bes_from_template(template_dict))

    #with open("Event Logs - Retain - " + log_name + " - Windows.bes", 'w') as filetowrite:
        #filetowrite.write(generate_bes_from_template.generate_bes_from_template(template_dict))
