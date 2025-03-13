from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Customer)
admin.site.register(EmailCode)
admin.site.register(Transaction)
admin.site.register(TransactionMessage)
admin.site.register(ErrorLog)

