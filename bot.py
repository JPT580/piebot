# -*- coding: utf-8 -*-

import asyncio
import inspect
import logging

import irc

logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.DEBUG, datefmt="%d.%m.%Y %H:%M:%S")
logger = logging.getLogger(__name__)


class ManagedProtocol(asyncio.Protocol):
    """Basic managed protocol handler, registers itself to ConnectionManager.
        Inherit this to overlay the management with actual protocol parsing.
    """

    def __init__(self, config=None, loop=None, connection_manager=None, endpoint=None):
        self._loop = loop
        self._connection_manager = connection_manager
        self._endpoint = endpoint
        self._transport = None
        self._config = config

    def _log(self, msg):
        host, port = self._endpoint
        logger.info("[{}:{}] ".format(host, port)+str(msg))

    def connection_made(self, transport):
        self._connection_manager.register_active_connection(self._endpoint, self)
        self._transport = transport
        self._log("Connection made!")
        host, port = transport.get_extra_info("peername")
        self._log("Connected to: {}:{}".format(host, port))

    def data_received(self, data):
        self._log("[R] "+str(data))

    def eof_received(self):
        self._log("Eof received!")

    def connection_lost(self, exc):
        self._log("Connection lost! ("+str(exc)+")")
        self._connection_manager.unregister_active_connection(self._endpoint)

    def send_data(self, data):
        self._log("[W] "+str(data))
        self._transport.write(data)

    def destroy(self):
        """ Triggered by ConnectionManager.remove_endpoint(). Closes transport. """
        self._transport.close()

    def get_config(self):
        return self._config

class IrcProtocol(ManagedProtocol):
    """Implementation of the IRC protocol.
    """

    def __init__(self, *args, **kwargs):
        super(IrcProtocol, self).__init__(*args, **kwargs)
        self.motd = False
        self.hello = False
        self._config = self.get_config()
        self._buffer = b""

    def encode(self, str):
        return str.encode(self._config["encoding"], "replace")

    def decode(self, bytes):
        return bytes.decode(self._config["encoding"], "replace")

    def connection_made(self, transport):
        super(IrcProtocol, self).connection_made(transport)
        self.send_data(b"USER " + self.encode(self._config["user"]) + b" dummy dummy :"
            + self.encode(self._config["realname"]) + b"\r\n")
        self.send_data(b"NICK " + self.encode(self._config["nick"]) + b"\r\n")

    def data_received(self, data):
        super(IrcProtocol, self).data_received(data)
        self._buffer += data
        self.process_data()

    def process_data(self):
        while b'\r\n' in self._buffer:
            line, self._buffer = self._buffer.split(b'\r\n', 1)
            line = self.decode(line.strip())
            irc_line = irc.IrcLine.from_string(line)
            print(self.encode(str(irc_line)))


class ConnectionManager(object):
    """Takes care of known endpoints that a connections shall be established to.
        Stores configurations for every configuration.
    """

    def __init__(self, loop):
        self._loop = loop
        self._endpoints = []
        self._configs = {}
        self._active_connections = {}
        self._loop.set_exception_handler(self._handle_async_exception)

    def add_endpoint(self, endpoint, config):
        logger.debug("Endpoint added: {}:{}".format(*endpoint))
        self._endpoints.append(endpoint)
        self._configs[endpoint] = config
        self._create_connection(endpoint)

    def _create_connection(self, endpoint):
        protocol = IrcProtocol(config=self._configs[endpoint], loop=self._loop, connection_manager=self, endpoint=endpoint)
        coroutine = self._loop.create_connection(lambda: protocol, *endpoint)
        asyncio.ensure_future(coroutine)

    def remove_endpoint(self, endpoint):
        logger.debug("Endpoint removed: {}:{}".format(*endpoint))
        self._endpoints.remove(endpoint)
        del self._configs[endpoint]
        if endpoint in self._active_connections:
            self._active_connections[endpoint].close()

    def register_active_connection(self, endpoint, protocol):
        self._active_connections[endpoint] = protocol

    def unregister_active_connection(self, endpoint):
        del self._active_connections[endpoint]
        self._create_connection(endpoint)

    def _handle_async_exception(self, loop, context):
        """Trying to take care of connection related exceptions."""
        logger.error("An async exception has been caught: "+str(context["exception"]))
        stack = context["future"].get_stack()
        if len(stack) > 1 and stack[1].f_code.co_name == "create_connection":
            last_stackframe = stack[len(stack)-1]
            call_args = inspect.getargvalues(last_stackframe)
            host = call_args.locals["host"]
            port = call_args.locals["port"]
            logger.error("Bad endpoint: {}:{}".format(host, port))
            self.remove_endpoint((host, port))
        else:
            loop.call_exception_handler(context)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    connection_manager = ConnectionManager(loop)
    connection_manager.add_endpoint(("irc.freenode.net", 6667), {
        "encoding": "utf-8",
        "nick": "Pb42",
        "user": "foobar",
        "realname": "Baz McBatzen",
        "channels": ["#botted"]
    })

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
