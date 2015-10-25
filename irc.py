# -*- coding: utf-8 -*-

def parse(line):
    prefix = ""
    if line[0:1] == ":":
        prefix = ":"
        subject, line = line.split(" ", 1)
        subject = subject[1:]
    else:
        subject = ""
    if " :" in line:
        tmp_str, trailing = line.split(" :", 1)
        tmp_args = tmp_str.split()
    else:
        trailing = ""
        tmp_args = line.split()
    command, *middle = tmp_args
    params = middle[:]
    # Now prepare parsing the subject if possible.
    if subject != "" and "!" in subject:
        s_nick, s_identname = subject.split("!", 1)
        if "@" in s_identname:
            s_identname, s_host = s_identname.split("@", 1)
            s_identname = s_identname.strip("~")
    else:
        s_nick = s_identname = s_host = subject
    return {
        "prefix": prefix,
        "subject": subject,
        "command": command,
        "params": params,
        "trailing": trailing,
        "nick": s_nick,
        "ident": s_identname,
        "host": s_host
    }


class Message(object):
    """Handles translation between strings and Message instances
    """
    _command_map = {}

    def __init__(self, data=None, *args, **kwargs):
        if data == None:
            self.data = {
                "prefix": "",
                "subject": "",
                "command": "",
                "params": "",
                "trailing": "",
                "nick": "",
                "ident": "",
                "host": ""
            }
        else:
            self.data = data
            self.parse()

    @classmethod
    def from_string(cls, string):
        data = parse(string)
        instance = cls._command_map.get(data["command"].upper(), cls)(data=data)
        return instance

    def __repr__(self):
        items = self.__dict__.copy()
        e = []
        for key in items:
            if key == "data":
                continue
            e.append(key+"="+str(items[key]))
        return "<" + self.__class__.__name__ + " " + ", ".join(e) + ">"

    def __str__(self):
        data = self.data
        e = []
        if data["subject"]:
            e.append(data["subject"])
        if data["command"]:
            e.append(data["command"])
        if data["params"] and len(data["params"]) > 0:
            e.append(" ".join(data["params"]))
        if data["trailing"]:
            e.append(":{}".format(data["trailing"]))
        result = " ".join(e)
        if data["prefix"]:
            result = "".join([data["prefix"], result])
        return result

    def get(self, attr):
        return self.data[attr]

    def parse(self):
        """Empty parse method to override by subclasses for THEIR CUSTOM FIELDS."""
        pass

    def update(self, data):
        self.data.update(data)
        # Reparse self in order to get consistent data for subclasses
        self.data.update(parse(str(self)))
        # Now have the subclass parse the relevant values out of the self-interpretation
        self.parse()

def register_derivative(name, bases, attr):
    new_cls = type(name, bases, attr)
    for cls in bases:
        cmd_map = getattr(cls, '_command_map', None)
        if cmd_map is not None:
            command = name.upper()
            if command in cmd_map:
                raise KeyError('command {} is already registered to this class'.format(command))
            cmd_map[command] = new_cls
    return new_cls

class User(Message, metaclass=register_derivative):
    def __init__(self, ident="", realname="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            self.update({
                "command": "USER",
                "params": [ident, "*", "*"],
                "trailing": realname
            })
    def parse(self):
        self.ident = self.get("params")[0]
        self.realname = self.get("trailing")

class Nick(Message, metaclass=register_derivative):
    def __init__(self, nick="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            self.update({
                "command": "NICK",
                "trailing": nick
            })
    def parse(self):
        self.old_nick = self.get("nick")
        self.nick = self.get("trailing")

class Ping(Message, metaclass=register_derivative):
    def parse(self):
        self.payload = self.get("trailing")

class Pong(Message, metaclass=register_derivative):
    def __init__(self, ping="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            self.update({
                "command": "PONG",
                "trailing": ping.data["trailing"]
            })
    def parse(self):
        self.payload = self.get("trailing")

class Privmsg(Message, metaclass=register_derivative):
    def __init__(self, target="", message="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            self.update({
                "command": "PRIVMSG",
                "params": [target],
                "trailing": message
            })
    def parse(self):
        self.source = self.get("nick")
        self.target = self.get("params")[0]
        self.message = self.get("trailing")

class Notice(Message, metaclass=register_derivative):
    def __init__(self, target="", message="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            self.update({
                "command": "NOTICE",
                "params": [target],
                "trailing": message
            })
    def parse(self):
        self.source = self.get("nick")
        self.target = self.get("params")[0]
        self.message = self.get("trailing")

class Kick(Message, metaclass=register_derivative):
    def __init__(self, channel="", user="", message="KICK", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            self.update({
                "command": "KICK",
                "params": [channel, user],
                "trailing": message
            })
    def parse(self):
        self.source = self.get("subject")
        self.channel = self.get("params")[0]
        self.target = self.get("params")[1]
        self.message = self.get("trailing")

class Join(Message, metaclass=register_derivative):
    def __init__(self, channel="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            self.update({
                "command": "JOIN",
                "trailing": channel
            })
    def parse(self):
        self.nick = self.get("nick")
        self.channel = self.get("trailing")
        if self.channel.strip() == "":
            self.channel = self.get("params")[0]

class Part(Message, metaclass=register_derivative):
    def __init__(self, channel="", message="PART", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            self.update({
                "command": "PART",
                "params": [channel],
                "trailing": message
            })
    def parse(self):
        self.nick = self.get("nick")
        self.channel = self.get("params")[0]
        self.message = self.get("trailing")

class Mode(Message, metaclass=register_derivative):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            self.update({
                "command": "MODE",
            })
    def parse(self):
        self.usermode = False
        self.source = self.get("nick")
        self.subject = self.get("params")[0]
        if(self.source == self.subject):
            """Parsing user modes here."""
            self.usermode = True
            flags = self.get("trailing")
            flag_modifier = flags[0:1] is "+"
            self.flags = []
            for flag in flags[1:]:
                self.flags.append((flag, flag_modifier))
        elif(len(self.get("params")) == 2):
            """Parsing simple channel modes here."""
            flags = self.get("params")[1]
            flag_modifier = flags[0:1] is "+"
            self.flags = []
            for flag in flags[1:]:
                self.flags.append((flag, flag_modifier))
        else:
            """Parsing parameterized channel modes here."""
            flags = self.get("params")[1]
            flag_modifier = flags[0:1] is "+"
            self.flags = []
            i = 1
            for flag in flags[1:]:
                self.flags.append((flag, flag_modifier, self.get("params")[1+i]))
                i += 1

class Topic(Message, metaclass=register_derivative):
    def __init__(self, channel="", topic="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            self.update({
                "command": "TOPIC",
                "params": [channel],
                "trailing": topic
            })
    def parse(self):
        self.source = self.get("nick")
        self.channel = self.get("params")[0]
        self.topic = self.get("trailing")



if __name__ == "__main__":
    buffer = b":irc.inn.at.euirc.net 001 JPT|NC :Welcome to the euIRCnet IRC Network JPT|NC!~AS@dslc-082-082-091-237.pools.arcor-ip.net\r\n:JPT|NC MODE JPT|NC :+ix\r\n:SpamScanner!service@central.euirc.net PRIVMSG JPT|NC :\x01VERSION\x01\r\n:JPT|NC!~AS@euirc-6f528752.pools.arcor-ip.net JOIN :#Tonari.\r\n:Lunlun!~l00n@euirc-e7be0d00.dip0.t-ipconnect.de JOIN :#Tonari.\r\n:ChanServ!services@euirc.net MODE #Tonari. +ao Lunlun Lunlun\r\n:Nitori!~kappa@chireiden.net PRIVMSG JPT|NC :\x01VERSION\x01\r\nPING :irc.inn.at.euirc.net\r\n:JPT|NC!~ADS@dslc-082-082-091-237.pools.arcor-ip.net JOIN #botted\r\n:JPT|NC!~ADS@dslc-082-082-091-237.pools.arcor-ip.net QUIT :Ping timeout: 272 seconds\r\nERROR :Closing Link: dslc-082-082-091-237.pools.arcor-ip.net (Ping timeout: 272 seconds)\r\n:JPT!~jpt@jpt.lu MODE #botted -h Pb42\r\n:JPT!~jpt@jpt.lu MODE #botted +v Pb42\r\n:JPT!~jpt@jpt.lu MODE #botted +o Pb42\r\n:JPT!~jpt@jpt.lu MODE #botted -vo Pb42 Pb42\r\n:JPT!~jpt@jpt.lu MODE #botted +b *illegal*!*@*\r\n:JPT!~jpt@jpt.lu MODE #botted -b *illegal*!*@*\r\n:JPT!~jpt@jpt.lu TOPIC #botted :#botted - edited\r\nPING :irc.hes.de.euirc.net\r\nPONG :irc.hes.de.euirc.net\r\n:JPT!~jpt@jpt.lu TOPIC #botted :#botted\r\n:JPT!~jpt@jpt.lu MODE #botted +i\r\n:JPT!~jpt@jpt.lu MODE #botted -i\r\n:JPT!~jpt@jpt.lu NICK :whoops\r\n"
    while b"\r\n" in buffer:
        line, buffer = buffer.split(b"\r\n", 1)
        if line == b"":
            continue
        line = line.decode("utf-8")
        msg = Message.from_string(line)
        print(msg.__repr__())
        print(str(msg))
        if msg.__class__.__name__ == 'Message':
            print(msg.__dict__)
        else:
            d = msg.__dict__
            del d["data"]
            print(d)
        print()
    exit()
