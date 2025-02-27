from django.urls import path
from .views import *

app_name = 'base'

urlpatterns = [
    path('', index, name='index'),
    path('sign-in/<slug:method>/', signIn, name = 'signIn'),
]