import unittest
from piebot import irc

class TestParser(unittest.TestCase):

    def test_test(self):
        source = ":irc.inn.at.euirc.net 001 JPT|NC :Welcome to the euIRCnet IRC Network JPT|NC!~AS@dslc-082-082-091-237.pools.arcor-ip.net"
        msg = irc.Message.from_string(source)
        created = str(msg)
        self.assertEqual(source, created)
