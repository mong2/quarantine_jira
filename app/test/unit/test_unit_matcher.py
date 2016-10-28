import imp
import os
import sys

module_name = 'quarantine'
here_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(here_dir, '../../')
sys.path.append(module_path)
fp, pathname, description = imp.find_module(module_name)
quarantine = imp.load_module(module_name, fp, pathname, description)


class TestMatcher:
    def test_verify_match_list(self):
        fail_1 = ["B@D_one"]
        fail_2 = "BAD_two"
        fail_3 = ["Notasbad", "positively awfulness"]
        pass_1 = ["legal_one", "legalTwo"]
        assert quarantine.Matcher.verify_match_list(fail_1) is False
        assert quarantine.Matcher.verify_match_list(fail_2) is False
        assert quarantine.Matcher.verify_match_list(fail_3) is False
        assert quarantine.Matcher.verify_match_list(pass_1)
