
import sys

sys.path.append('../')
sys.path.append('../../')

from generate_bes_from_template import generate_bes_from_template

log_array = ['Security', 'System', 'Application']

for log_name in log_array:
    template_dict = {}
    template_dict['template_file_path'] = "examples/TEMPLATE_Event_Logs_Retain-LOG-Windows.bes"
    template_dict['log_name'] = log_name
    print(generate_bes_from_template.generate_bes_from_template(template_dict))