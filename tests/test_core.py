
from genthemall.core import load_config
from nose.tools import eq_, ok_

def test_load_config():
    config = load_config('tests/genthemall.cfg')
    ok_(config is not None)
    
