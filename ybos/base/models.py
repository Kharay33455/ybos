from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import channels.layers
# Create your models here.

# this is a single customer object.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE) # ensure every user can only reg as a customer
    email = models.TextField() # store email encrypted but not one way.

    def __str__(self):
        return self.user.username

# store otp to match an email obj temporaily
class EmailCode(models.Model):
    email = models.EmailField() # the email to be verified
    otp = models.CharField(max_length = 6, default = 000000) # the pending otp
    created = models.DateTimeField(auto_now_add = True) # when was it requested
    updated = models.DateTimeField(default = datetime.now())    # when was it last edited

    def __str__(self):
        return f'{self.email} verification code.'

# stores info about a transaction
class Transaction(models.Model):
    transactionId = models.CharField(max_length = 20) # the id of said transaction
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE)  # the customer who has initated the transaction
    created = models.DateTimeField(auto_now_add = True) # when it was initiated
    completed = models.DateTimeField(default = None, blank = True, null = True) # is it completed, if not, this is none, if yes, this is completion date.
    wasSuccessful = models.BooleanField(blank = True, null = True)
    remark = models.TextField(blank = True, null = True)
    amount = models.CharField(max_length = 20)  # how much is the transaction worth

    def __str__(self):
        return f"Transaction for {self.customer.user.username} at {self.created}."


# store all unexpected errors to be looked at later
class ErrorLog(models.Model):
    error = models.TextField()  # what happened?
    created = models.DateTimeField(auto_now_add= True)  # when did it happen?
    user = models.ForeignKey(User, on_delete = models.CASCADE) # who triggered this error

    def __str__(self):
        return f'Error from user {self.user} on {self.created}.'


# this is a single message related to a transaction
class TransactionMessage(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete = models.CASCADE) # what transaction has this message
    # a messgae must have a text or image or both to be valid. Cannot be midding both
    text = models.TextField(blank = True, null = True) # text, if any
    image = models.ImageField(blank = True, null = True, upload_to = 'transaction') # image, if any.
    fromUser = models.BooleanField(default = True)  # from user or from system

    def __str__(self):
        return f'Message for transaction {self.transaction.transactionId}'