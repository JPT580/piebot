# -*- coding: utf-8 -*-

import unittest
from piebot import irc


class Parser(unittest.TestCase):

    def test_parse_generic_message_one(self):
        raw = ":someserver.net 123 one two three :Let's parse a generic formatted msg!"
        msg = irc.Message.from_string(raw)
        self.assertEqual(str(msg), raw, msg="String representation does not match!")
        self.assertEqual(msg.get("prefix"), ":", msg="Incorrect prefix!")
        self.assertEqual(msg.get("subject"), "someserver.net", msg="Incorrect subject!")
        self.assertEqual(msg.get("command"), "123", msg="Incorrect command!")
        self.assertEqual(msg.get("params"), ["one", "two", "three"], msg="Incorrect params!")
        self.assertEqual(msg.get("trailing"), "Let's parse a generic formatted msg!", msg="Incorrect trailing!")
        self.assertEqual(msg.get("nick"), "someserver.net", msg="Incorrect nick!")
        self.assertEqual(msg.get("ident"), "someserver.net", msg="Incorrect ident!")
        self.assertEqual(msg.get("host"), "someserver.net", msg="Incorrect host!")

    def test_parse_generic_message_two(self):
        raw = ":ralf!~wiggum@simpsons.net PRIVMSG #channel :duck duck duck duck"
        msg = irc.Message.from_string(raw)
        self.assertEqual(str(msg), raw, msg="String representation does not match!")
        self.assertEqual(msg.get("prefix"), ":", msg="Incorrect prefix!")
        self.assertEqual(msg.get("subject"), "ralf!~wiggum@simpsons.net", msg="Incorrect subject!")
        self.assertEqual(msg.get("command"), "PRIVMSG", msg="Incorrect command!")
        self.assertEqual(msg.get("params"), ["#channel"], msg="Incorrect params!")
        self.assertEqual(msg.get("trailing"), "duck duck duck duck", msg="Incorrect trailing!")
        self.assertEqual(msg.get("nick"), "ralf", msg="Incorrect nick!")
        self.assertEqual(msg.get("ident"), "wiggum", msg="Incorrect ident!")
        self.assertEqual(msg.get("host"), "simpsons.net", msg="Incorrect host!")

    def test_parse_generic_message_three(self):
        raw = ":peter!~per@griffin.com MODE peter +ix"
        msg = irc.Message.from_string(raw)
        self.assertEqual(str(msg), raw, msg="String representation does not match!")
        self.assertEqual(msg.get("prefix"), ":", msg="Incorrect prefix!")
        self.assertEqual(msg.get("subject"), "peter!~per@griffin.com", msg="Incorrect subject!")
        self.assertEqual(msg.get("command"), "MODE", msg="Incorrect command!")
        self.assertEqual(msg.get("params"), ["peter", "+ix"], msg="Incorrect params!")
        self.assertEqual(msg.get("trailing"), "", msg="Incorrect trailing!")
        self.assertEqual(msg.get("nick"), "peter", msg="Incorrect nick!")
        self.assertEqual(msg.get("ident"), "per", msg="Incorrect ident!")
        self.assertEqual(msg.get("host"), "griffin.com", msg="Incorrect host!")
