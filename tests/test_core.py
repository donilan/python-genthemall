
from genthemall.core import load_config, GTLTemplate
from nose.tools import eq_, ok_

def test_load_config():
    config = load_config('tests/genthemall.cfg')
    ok_(config is not None)
    
def test_find_templates():
    tmpl = GTLTemplate()
    ok_(len(tmpl.sys_templates) > 0)
