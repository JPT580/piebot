# -*- coding: utf-8 -*-

def parse(line):
    prefix = ""
    if line[0:1] == ":":
        prefix = ":"
        subject, line = line.split(None, 1)
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
    return {"prefix": prefix, "subject": subject, "command": command, "params": params, "trailing": trailing}


class Message(object):
    """Handles translation between strings and Message instances
    """
    _command_map = {}

    def __init__(self):
        self.data = {
            "prefix": "",
            "subject": "",
            "command": "",
            "params": "",
            "trailing": ""
        }

    @classmethod
    def from_string(cls, string):
        data = parse(string)
        instance = cls._command_map.get(data["command"].upper(), cls)()
        instance.update(data)
        return instance

    def __repr__(self):
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
    def __init__(self, ident=None, realname=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ident != None and realname != None:
            self.update({
                "command": "USER",
                "params": [ident, "*", "*"],
                "trailing": realname
            })

class Nick(Message, metaclass=register_derivative):
    def __init__(self, nick=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if nick != None:
            self.update({
                "command": "NICK",
                "trailing": nick
            })

class Ping(Message, metaclass=register_derivative):
    def parse(self):
        self.payload = self.get("trailing")

class Pong(Message, metaclass=register_derivative):
    def __init__(self, ping=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ping != None:
            self.update({
                "command": "PONG",
                "trailing": ping.data["trailing"]
            })
    def parse(self):
        self.payload = self.get("trailing")

class Privmsg(Message, metaclass=register_derivative):
    def __init__(self, target=None, message=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if target != None and message != None:
            self.update({
                "command": "PRIVMSG",
                "params": [target],
                "trailing": message
            })
    def parse(self):
        self.source = self.get("subject")
        self.target = self.get("params")[0]
        self.message = self.get("trailing")

class Notice(Message, metaclass=register_derivative):
    def __init__(self, target=None, message=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if target != None and message != None:
            self.update({
                "command": "NOTICE",
                "params": [target],
                "trailing": message
            })
    def parse(self):
        self.source = self.get("subject")
        self.target = self.get("params")[0]
        self.message = self.get("trailing")

class Kick(Message, metaclass=register_derivative):
    def __init__(self, channel=None, user=None, message="KICK", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if channel != None and user != None:
            self.update({
                "command": "KICK",
                "params": [channel, user],
                "trailing": message
            })
    def parse(self):
        self.source = self.get("subject")
        self.target = self.get("params")[0]
        self.message = self.get("trailing")

class Join(Message, metaclass=register_derivative):
    def __init__(self, channel=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if channel != None:
            self.update({
                "command": "JOIN",
                "trailing": channel
            })
    def parse(self):
        self.nick = self.get("subject")
        self.channel = self.get("trailing")

class Part(Message, metaclass=register_derivative):
    def __init__(self, channel=None, message="PART", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if channel != None:
            self.update({
                "command": "PART",
                "params": [channel],
                "trailing": message
            })



if __name__ == "__main__":
    l = Message.from_string(":JPT|NC!~AS@euirc-6f528752.pools.arcor-ip.net JOIN :#euirc")
    print(str(l))
    print()

    l = Message.from_string(":ChanServ!services@euirc.net MODE #Tonari. +ao JPT JPT")
    print(str(l))
    print()

    line3 = Join("#botted")
    print(str(line3))

    exit()
