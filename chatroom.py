import sys
import asyncio
from protocol import Protocol

class ChatRoom:

    def __init__(self, name, port, loop):
        self._name = name
        self._port = port
        self._loop = loop
        self._username_transports = {}

    @property
    def name(self):
        return self._name

    def run(self):
        coro = self._loop.create_server(
            protocol_factory=lambda: Protocol(self),
            host="",
            port=self._port
        )
        return self._loop.run_until_complete(coro)

    def register_user(self, username, transport):
        if username in self.users():
            return False
        self._username_transports[username] = transport
        self._broadcast("User {} arrived".format(username))
        return True

    def deregister_user(self, username):
        del self._username_transports[username]
        self._broadcast("User {} departed".format(username))

    def users(self):
        return self._username_transports.keys()

    def message_from(self, username, message):
        self._broadcast("{}: {}".format(username, message))

    def _broadcast(self, message):
        TELET_EOL = '\r\n'
        for transport in self._username_transports.values():
            transport.write(message.encode('utf-8'))
            transport.write(TELET_EOL.encode('utf-8'))

def main(argv):
    name = argv[1] if len(argv) >= 2 else "Chatterbox"
    port = int(argv[2]) if len(argv) >= 3 else 1234
    loop = asyncio.get_event_loop()
    chat_room = ChatRoom(name, port, loop)
    server = chat_room.run()
    loop.run_forever()

if __name__ == "__main__":
    main(sys.argv)

