# -*- coding: utf-8 -*-

import unittest
from piebot import irc


class Message(unittest.TestCase):

    def test_parse_user(self):
        raw = "USER ident * * :real name"
        msg = irc.Message.from_string(raw)
        self.assertIsInstance(msg, irc.User, msg="Not a User!")
        self.assertEqual(msg.ident, "ident")
        self.assertEqual(msg.realname, "real name")

    def test_construct_user(self):
        msg = irc.User(ident="hans", realname="peter blubber")
        self.assertEqual(str(msg), "USER hans * * :peter blubber")


    def test_parse_nick(self):
        raw = ":oldnick!~somebody@internet.org NICK :newnick"
        msg = irc.Message.from_string(raw)
        self.assertIsInstance(msg, irc.Nick, msg="Not a Nick!")
        self.assertEqual(msg.old_nick, "oldnick")
        self.assertEqual(msg.nick, "newnick")

    def test_construct_nick(self):
        msg = irc.Nick(nick="foobar")
        self.assertEqual(str(msg), "NICK :foobar")


    def test_parse_ping(self):
        raw = "PING :payload"
        msg = irc.Message.from_string(raw)
        self.assertIsInstance(msg, irc.Ping, msg="Not a Ping!")
        self.assertEqual(msg.payload, "payload")

    def test_construct_ping(self):
        msg = irc.Ping("payload")
        self.assertEqual(str(msg), "PING :payload")


    def test_parse_pong(self):
        raw = "PONG :doalyap"
        msg = irc.Message.from_string(raw)
        self.assertIsInstance(msg, irc.Pong, msg="Not a Pong!")
        self.assertEqual(msg.payload, "doalyap")

    def test_construct_pong(self):
        msg = irc.Pong(payload="payload")
        self.assertEqual(str(msg), "PONG :payload")


    def test_parse_privmsg(self):
        raw = ":this!~is@spart.aaa PRIVMSG #target :whoop dee doo!"
        msg = irc.Message.from_string(raw)
        self.assertIsInstance(msg, irc.Privmsg, msg="Not a Privmsg!")
        self.assertEqual(msg.source, "this")
        self.assertEqual(msg.target, "#target")
        self.assertEqual(msg.message, "whoop dee doo!")

    def test_construct_privmsg(self):
        msg = irc.Privmsg(target="#example", message="How dee ho!")
        self.assertEqual(str(msg), "PRIVMSG #example :How dee ho!")


    def test_parse_notice(self):
        raw = ":john!~secret@agents.de NOTICE this_is_you :bleep bleep!"
        msg = irc.Message.from_string(raw)
        self.assertIsInstance(msg, irc.Notice, msg="Not a Notice!")
        self.assertEqual(msg.source, "john")
        self.assertEqual(msg.target, "this_is_you")
        self.assertEqual(msg.message, "bleep bleep!")

    def test_construct_notice(self):
        msg = irc.Notice(target="#somewhere", message="wheee eee!")
        self.assertEqual(str(msg), "NOTICE #somewhere :wheee eee!")

