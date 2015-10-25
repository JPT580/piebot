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


    def test_parse_kick(self):
        raw = ":devil!~evil@guy.nl KICK #mods mike :damn it, mike!"
        msg = irc.Message.from_string(raw)
        self.assertIsInstance(msg, irc.Kick, msg="Not a Kick!")
        self.assertEqual(msg.source, "devil")
        self.assertEqual(msg.channel, "#mods")
        self.assertEqual(msg.target, "mike")
        self.assertEqual(msg.message, "damn it, mike!")

    def test_construct_kick(self):
        msg = irc.Kick(channel="#lobby", user="annoying_guy", message="please leave")
        self.assertEqual(str(msg), "KICK #lobby annoying_guy :please leave")


    def test_parse_join(self):
        raw = ":frank!~that@guy.again JOIN #lounge"
        msg = irc.Message.from_string(raw)
        self.assertIsInstance(msg, irc.Join, msg="Not a Join!")
        self.assertEqual(msg.nick, "frank")
        self.assertEqual(msg.channel, "#lounge")

    def test_construct_join(self):
        msg = irc.Join(channel="#hiking")
        self.assertEqual(str(msg), "JOIN :#hiking")


    def test_parse_part(self):
        raw = ":trump!~rich@billionaire.gold PART #society :suck it up"
        msg = irc.Message.from_string(raw)
        self.assertIsInstance(msg, irc.Part, msg="Not a Part!")
        self.assertEqual(msg.nick, "trump")
        self.assertEqual(msg.channel, "#society")
        self.assertEqual(msg.message, "suck it up")

    def test_construct_part(self):
        msg = irc.Part(channel="#tower", message="don't fall off")
        self.assertEqual(str(msg), "PART #tower :don't fall off")

