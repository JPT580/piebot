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
    """Handles translation between strings and IrcLines
    """
    _command_map = {}

    def __init__(self, data={"prefix": "", "subject": "", "command": "", "params": "", "trailing": ""}):
        self.data = data

    @classmethod
    def from_string(cls, string):
        data = parse(string)
        instance = cls._command_map.get(data["command"].upper(), cls)(data)
        instance.data = data
        return instance

    def __repr__(self):
        data = self.data
        print(data)
        e = []
        if data["subject"]:
            e.append(data["subject"])
        if data["command"]:
            e.append(data["command"])
        if data["params"]:
            e.append(" ".join(data["params"]))
        if data["trailing"]:
            e.append(":{}".format(data["trailing"]))
        result = " ".join(e)
        if data["prefix"]:
            result = "".join([data["prefix"], result])
        return result

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

class Privmsg(Message, metaclass=register_derivative):
    pass

class Kick(Message, metaclass=register_derivative):
    def __init__(self, channel=None, user=None, message="KICK", *args, **kwargs):
        super(Kick, self).__init__(*args, **kwargs)
        self.data.update({
            "command": "KICK",
            "params": [channel, user],
            "trailing": message
        })


if __name__ == "__main__":
    l = Message.from_string(":JPT|NC!~AS@euirc-6f528752.pools.arcor-ip.net JOIN :#euirc")
    print(str(l))
    print()

    l = Message.from_string(":ChanServ!services@euirc.net MODE #Tonari. +ao JPT JPT")
    print(str(l))
    print()

    line = Kick("#botted", "JPT", "Du Sack!")
    print(str(line))

    line2 = Message.from_string(str(line))
    print(str(line2))
    exit()


