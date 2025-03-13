from django.urls import path
from .views import *

app_name = 'base'

urlpatterns = [
    path('', index, name='index'),
    path('sign-in/<slug:method>/', signIn, name = 'signIn'),
    path('ybos/', registrationRequest, name='ybosSignIn'),
    path('completeSignIn/', completeSignIn, name='complete'),
    path('ybos/get-otp/', getOTP, name='getOTP'),
    path('logout/', logout_request, name = 'logout'),
    path('buy-yuan', buyYuan, name = 'buyYuan'),
    path('end-transactions', endChat, name='endChat')
]