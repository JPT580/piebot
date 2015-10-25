# -*- coding: utf-8 -*-

def parse(line):
    prefix = ""
    subject = ""
    trailing = ""
    command = ""
    params = ""
    if line[0:1] == ":":
        prefix = ":"
        line = line[1:]
        if " " in line:
            subject, line = line.split(" ", 1)
    if " :" in line:
        line, trailing = line.split(" :", 1)
    if " " in line:
        command, *middle = line.split()
        params = middle[:]
    else:
        command = line
    # Now prepare parsing the subject if possible.
    if subject != "" and "!" in subject:
        s_nick, s_identname = subject.split("!", 1)
        if "@" in s_identname:
            s_identname, s_host = s_identname.split("@", 1)
            s_identname = s_identname.strip("~")
    else:
        s_nick = s_identname = s_host = subject
    result = {
        "prefix": prefix,
        "subject": subject,
        "command": command,
        "params": params,
        "trailing": trailing,
        "nick": s_nick,
        "ident": s_identname,
        "host": s_host
    }
    return result


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
        command = data["command"].upper()
        if command.isdigit():
            command = "Numeric{}".format(command).upper()
        instance = cls._command_map.get(command, cls)(data=data)
        return instance

    def __repr__(self):
        items = self.__dict__.copy()
        if len(items) == 1:
            items = items["data"]
            for e in ["prefix", "nick", "host", "ident"]: del items[e]
        e = []
        for key in items:
            if key == "data":
                continue
            e.append(key+"='"+str(items[key])+"'")
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
            result = data["prefix"] + result
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
    def __init__(self, payload="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            self.update({
                "command": "PING",
                "trailing": payload
            })
    def parse(self):
        self.payload = self.get("trailing")

class Pong(Message, metaclass=register_derivative):
    def __init__(self, ping="", payload="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            if ping: payload = ping.data["trailing"]
            self.update({
                "command": "PONG",
                "trailing": payload
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
        self.source = self.get("nick")
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
    def __init__(self, subject="", modes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            self.update({
                "command": "MODE",
            })
    def parse(self):
        #TODO: Implement this in a proper way!
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

class Quit(Message, metaclass=register_derivative):
    def __init__(self, message="QUIT", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" not in kwargs:
            self.update({
                "command": "QUIT",
                "trailing": message
            })
    def parse(self):
        self.nick = self.get("nick")
        self.message = self.get("trailing")

class Numeric005(Message, metaclass=register_derivative):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse(self):
        pass