# -*- coding: utf-8 -*-

def parse(line):
    if line[0:1] == ':':
        prefix, line = line.split(None, 1)
        prefix = prefix[1:]
    else:
        prefix = ""
    if ' :' in line:
        tmp_str, trailing = line.split(' :', 1)
        tmp_args = tmp_str.split()
    else:
        trailing = ""
        tmp_args = line.split()
    command, *middle = tmp_args
    params = middle[:]
    return prefix, command, params, trailing


class IrcLine(object):
    """Handles translation between strings and IrcLines
    """
    def __init__(self):
        self.prefix = ""
        self.command = ""
        self.params = ""
        self.trailing = ""

    @classmethod
    def from_string(cls, string):
        instance = cls()
        data = parse(string)
        print(data)
        instance.prefix = data[0]
        instance.command = data[1]
        instance.params = data[2]
        instance.trailing = data[3]
        return instance

    def __repr__(self):
        e = []
        if self.prefix:
            e.append(self.prefix)
        if self.command:
            e.append(self.command)
        if self.params:
            e.append(" ".join(self.params))
        if self.trailing:
            e.append(":{}".format(self.trailing))
        result = " ".join(e)
        return result

    @classmethod
    def kick(cls, channel, user, msg="KICK"):
        instance = cls()
        instance.command = "KICK"
        instance.params = [channel, user]
        instance.trailing = msg
        return instance

if __name__ == '__main__':
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


