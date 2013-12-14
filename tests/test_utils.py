from genthemall.utils import load_class
from nose.tools import eq_, ok_

def test_load_class():
    ok_(load_class('genthemall.commands.BaseCommand') is not None)
