
from genthemall.core import GTLTemplateHolder, GTLGenerator
from nose.tools import eq_, ok_

def test_gtl_generator():
    g = GTLGenerator('tests/genthemall.cfg')
    ok_(g.config is not None)

def test_find_templates():
    tmpl = GTLTemplateHolder('genthemall')
    ok_(len(tmpl.sys_templates) > 0)
    ok_(len(tmpl.user_templates) == 0)
