import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # before we accept a socket donnection, we must ensure the following
        # user requesting connection is the same user that owns the transaction or is a superuser

        await self.accept()
        print('Socket open')

    async def disconnect(self, close_code):
        print('socket disconnected...')
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        pass

       # await self.send(text_data=json.dumps({"message": message}))