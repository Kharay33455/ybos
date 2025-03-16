# python imports
import base64
import json
import random

# django imports
from django.core.files.base import ContentFile

# custom imports from project
from base.models import Transaction, ErrorLog, TransactionMessage

# channels imports
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
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
        message = str(text_data_json["text"]).strip()
        image = str(text_data_json["image"]).strip()
        if image == "" and message == "":
            pass
        else:
            # create and save the new message
            if sync_to_async(checkMessageUser)(self.scope['url_route']['kwargs']['room_name'], self.scope['user']): #Check that this user is the same user that originally initiated this transaction
                if await sync_to_async (createNewMessage)(self, image, message):
                    await self.send(text_data=json.dumps({"message": message, "image" : image, "fromUser" : True}))


def checkMessageUser(_transId, _user):
    transaction = Transaction.objects.get(transactionId = self.scope['url_route']['kwargs']['room_name'])
    if _user == transaction.customer.user:
        return True
    else:
        return False

def createNewMessage(self, _image, _message):
    try:
        # prep image
        if _image == "":
            _image = None
        else:
            if _image.startswith('data:image'): # get image if it contains header in encoding, if not, use as is.
                _image = _image.split(',')[1]
            randVal = random.randint(10000000, 999999999999)
            _image = ContentFile(base64.b64decode(_image), name = str(self.scope['user'].username) + str(randVal) +".jpg")
        # prep message
        if _message == "":
            _message = None
            
        # get transaction
        transaction = Transaction.objects.get(transactionId = self.scope['url_route']['kwargs']['room_name'])
        if transaction.customer.user == self.scope['user']:
            _fromUser = True
        else:
            _fromUser = False
        TransactionMessage.objects.create(transaction = transaction, text = _message, image = _image, fromUser = _fromUser)
        return True
    except Exception as e:
        print(e)
        ErrorLog.objects.create(error = e, user = self.scope['user'])
        return False
