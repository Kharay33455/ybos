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
        # before accepting a socket connections, program must ensure the following
        # user requesting connection is the same user that initiated the transaction
        #   or this user is staff user assigned to task.
        route = self.scope['url_route']['kwargs']['room_name']
        user = self.scope['user']

        # make sure only transaction initiator and admin can access socket
        if not await sync_to_async(checkMessageUser)(self, route, user) and not user.is_superuser:
            await self.close()

        self.room_group_name = f'trans_{route}' # add group name to allow layers
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self, close_code):
        print('socket disconnected...')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        pass

    async def receive(self, text_data): 
        text_data_json = json.loads(text_data)
        sigType = str(text_data_json["type"]).strip()
        reqUser = self.scope['user']
        if sigType == "newMessage":
            message = str(text_data_json["text"]).strip()
            image = str(text_data_json["image"]).strip()
            if image == "" and message == "":
                return
            status = await sync_to_async(createNewMessage)(self, image, message)
            if not status:
                print("Could not create this message...")
                return
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type' : 'newMessage',
                    'message' : message,
                    'image' : image,
                    'fromUser' : status['from_user']
                }
            )
                
                    
                    
    
    async def newMessage(self, event):
        message = event["message"]
        image = event["image"]
        fromUser = event['fromUser']
        # check they should be in this chat
        if self.scope['user'].is_superuser or await sync_to_async(checkMessageUser)(self, self.scope['url_route']['kwargs']['room_name'], self.scope['user']) : #Check that this user is the same user that originally initiated this transaction
            await self.send(text_data=json.dumps({"message": message, "image" : image, "fromUser" : fromUser, 'type' : 'new_message_signal'}))




def checkMessageUser(self, _transId, _user):
    print("cjecking")
    transaction = Transaction.objects.get(transactionId = self.scope['url_route']['kwargs']['room_name'])
    print(_user)
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
        return {'status' : True , 'from_user' : _fromUser}
    except Exception as e:
        print(e)
        ErrorLog.objects.create(error = e, user = self.scope['user'])
        return False