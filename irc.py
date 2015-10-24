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
    return prefix, subject, command, params, trailing


class IrcLine(object):
    """Handles translation between strings and IrcLines
    """
    def __init__(self):
        self.prefix = ""
        self.subject = ""
        self.command = ""
        self.params = ""
        self.trailing = ""

    @classmethod
    def from_string(cls, string):
        instance = cls()
        data = parse(string)
        print(data)
        instance.prefix = data[0]
        instance.subject = data[1]
        instance.command = data[2]
        instance.params = data[3]
        instance.trailing = data[4]
        return instance

    def __repr__(self):
        e = []
        if self.subject:
            e.append(self.subject)
        if self.command:
            e.append(self.command)
        if self.params:
            e.append(" ".join(self.params))
        if self.trailing:
            e.append(":{}".format(self.trailing))
        result = " ".join(e)
        if self.prefix:
            result = "".join([self.prefix, result])
        return result

    @classmethod
    def kick(cls, channel, user, msg="KICK"):
        instance = cls()
        instance.command = "KICK"
        instance.params = [channel, user]
        instance.trailing = msg
        return instance

if __name__ == "__main__":
    l = IrcLine.from_string(":JPT|NC!~AS@euirc-6f528752.pools.arcor-ip.net JOIN :#euirc")
    print(str(l))
    print()

    l = IrcLine.from_string(":ChanServ!services@euirc.net MODE #Tonari. +ao JPT JPT")
    print(str(l))
    print()

    line = IrcLine.kick("#botted", "JPT", "Du Sack!")
    print(str(line))
    line2 = IrcLine.from_string(str(line))
    print(str(line2))
    exit()


