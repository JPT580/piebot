import asyncio
from piebot import ConnectionManager

loop = asyncio.get_event_loop()

# TODO: Move configuration into a config file!
connection_manager = ConnectionManager(loop)
connection_manager.add_endpoint(("irc.euirc.net", 6667), {
    "encoding": "utf-8",
    "nick": "Pb42",
    "ident": "foobar2000",
    "realname": "Baz McBatzen",
    "channels": ["#botted"]
})
connection_manager.add_endpoint(("irc.freenode.net", 6667), {
    "encoding": "utf-8",
    "nick": "Pb42",
    "ident": "foobar2000",
    "realname": "Baz McBatzen",
    "channels": ["#botted"]
})

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.close()

