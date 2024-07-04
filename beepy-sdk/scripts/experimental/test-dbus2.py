#!/usr/bin/python

import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

import asyncio
import json

from dbus_fast import Message, MessageType
from dbus_fast.aio import MessageBus


async def main():
    bus = await MessageBus().connect()
    reply = await bus.call(
        Message(
            destination="org.freedesktop.DBus",
            path="/org/bluez/hci0",
            interface="org.freedesktop.DBus",
            member="ListNames",
        )
    )

    if reply.message_type == MessageType.ERROR:
        raise Exception(reply.body[0])

    print(json.dumps(reply.body[0], indent=2))


asyncio.run(main())