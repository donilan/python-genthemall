
from genthemall.core import load_config, find_template_files, \
    find_template_folders, find_templates
from nose.tools import eq_, ok_

def test_load_config():
    config = load_config('tests/genthemall.cfg')
    ok_(config is not None)
    
def test_find_template_files():
    template_files = find_template_files()
    ok_(len(template_files) > 0)

def test_find_template_folders():
    template_folders = find_template_folders()
    ok_(len(template_folders) > 0)

def test_find_templates():
    templates = find_templates()
    ok_(len(templates) > 0)
