#!/usr/bin/env python3
from aiohttp import web


class WSChat:
    def __init__(self, host='0.0.0.0', port=56000):
        self.host = host
        self.port = port
        self.conns = {}

    @staticmethod
    async def main_page(self):
        return web.FileResponse('./index_.html')

    async def connect_user_async(self, request: web.Request):
        id = ''
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        async for packet in ws:
            if packet.data == 'ping':
                await ws.pong()
                continue
            message = packet.json()
            id = message['id']
            if message['mtype'] == "INIT":
                self.conns[id] = ws
                for conId in self.conns.keys():
                    if conId != id:
                        await self.conns[conId].send_json({'mtype': 'USER_ENTER', 'id': id})
            if message['mtype'] == "TEXT":
                text = message['text']
                if message['to'] is None:
                    for conId in self.conns.keys():
                        if conId != id:
                            await self.conns[conId].send_json({'mtype': 'MSG', 'id': id, 'text': text})
                elif message['to'] is not None:
                    recipient = message['to']
                    await self.conns[recipient].send_json({'mtype': 'DM', 'id': id, 'text': text})

        for conId in self.conns.keys():
            if conId != id:
                await self.conns[conId].send_json({'mtype': 'USER_LEAVE', 'id': id})
        del self.conns[id]
        await ws.close()
        return ws

    def run(self):
        app = web.Application()

        app.router.add_get('/', self.main_page)

        app.router.add_get('/chat', self.connect_user_async)

        web.run_app(app, host=self.host, port=self.port)


if __name__ == '__main__':
    WSChat(host='127.0.0.1').run()
