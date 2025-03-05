from django.shortcuts import render
from django.urls import reverse
# used to query API
import requests
# used to get secrets with os.getenv('SECRETE_VALUE')
import os
from dotenv import load_dotenv
import string
from django.contrib.auth.models import User
from .models import *
import random
from django.contrib.auth import authenticate, login, logout

# get date time
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

# import google auth libraries
import google.oauth2.credentials
import google_auth_oauthlib.flow

# user creation
from django.contrib.auth.forms import UserCreationForm



load_dotenv()

# check when last user requested code
def checkHasRequested(time_now, updated, duration):
    value = True
    print(time_now.minute, updated.minute)
    print(time_now.hour, updated.hour)
    # if it't not the same day
    if time_now.day != updated.day:
        value = False
        return value
    if time_now.hour != updated.hour:
        value = False
        return value
    if time_now.minute - updated.minute < duration:
        value = True
    else:
        value = False
    return value
    

# gets the current time
def getTimeNow():
    timeNow = datetime.now().strftime("%H:%M:%S")
    return timeNow

#gets current rates
def getCurrentRate():
    # takes a value of hours and checks if it's AM or PM
    def checkTime(_timeVal):
        timeVal = int(_timeVal)
        if timeVal > 12:
            timeVal = timeVal - 12
            isPm = 'PM'
        else:
            isPm = 'AM'
        return {'time' : str(timeVal), 'isPM' : isPm}
    # get rate from current layer with access token in env file and return string
    url = 'http://apilayer.net/api/live?access_key='+str(os.getenv('API_LAYER_KEY'))+'&currencies=NGN&source=CNY'
    # make request and load response to json
    
    #rates_data = requests.get(url)
    #feedback = rates_data.json()
    
    
    feedback = {'success': True, 'terms': 'https://currencylayer.com/terms', 'privacy': 'https://currencylayer.com/privacy', 'timestamp': 1740415631, 'source': 'CNY', 'quotes': {'CNYNGN': 206.807627}}
    # extract rates from data. This is the  buy rate. The sell rate is this minus 10
    buyRates = int(feedback['quotes']['CNYNGN'])
    sellRates = buyRates - 10
    # get the timestamp. Comes as HRMMSS
    _time = getTimeNow()
    # run the check time function to check if it's a morning or noon return
    timeHour = checkTime(_time[0:2])
    # construct time
    time = timeHour['time'] + ':' + _time[3:5] + ':'+ _time[6:8] +' ' + timeHour['isPM']
    # construct return dict and return
    return_dict = {'buyRates' : str(buyRates), 'sellRates' : str(sellRates), 'time' : time}
    return return_dict


def googleSignInFunction(request):
    secrets = {"web": {"client_id": os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
                        "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_secret": os.getenv('GOOGLE_OAUTH_CLIENT_SECRETE'),
                        "redirect_uris": [
                            "http://localhost:8000/sign-in/complete/",
                            "http://127.0.0.1:8000/sign-in/complete/",
                            "https://ybos.com"
                            ],
                        "javascript_origins": [
                            "http://127.0.0.1:8000",
                            "https://ybos.com",
                            "http://localhost:8000"
                            ]
                        }
                }
    flow = google_auth_oauthlib.flow.Flow.from_client_config(secrets, scopes=['email'])

    host = request.get_host()
    redirect_url = str(host)+'/sign-in/complete/'
    flow.redirect_uri = redirect_url
    authorization_url, state = flow.authorization_url(
    # Recommended, enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type='offline',
    # Optional, enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true',
    # Optional, set prompt to 'consent' will prompt the user for consent
    prompt='consent')
    print(authorization_url)
    print('here')
    return authorization_url



def validateOTP(email, _otp):
    isValid = True
    # does object exist
    try: 
        emailCodeObj = EmailCode.objects.get(email = email)
    except EmailCode.DoesNotExist:
        isValid = False
        return isValid
    
    # has another user claimed this object?
    try:
        cus = Customer.objects.get(email = email)
        isValid = False
        return isValid
    except Customer.DoesNotExist:
        pass

    # check if code is valid
    if _otp != emailCodeObj.otp:
        isValid = False
        return isValid

    
    # is their otp still valid?
    timeNow = datetime.now()
    if checkHasRequested(timeNow, emailCodeObj.updated, 5):
        return isValid
    else:
        isValid = False
        return isValid
        


def verifyEmail(_email):
    if _email == "":
        return {'err' : 'You must provide your email', 'status' : 400}
    acceptables = string.ascii_letters + string.digits + '@' + '.'+'_'+'-'+'+'
    counter = 0
    for _ in _email:
        if _ not in acceptables:
            return {'err' : f'You cannot use "{_email[counter]}" in your email.', 'status' : 400}
        counter += 1
    return {'status' : 200, 'email' : _email}







# index
def index(request):
    getTimeNow()
    # get current rates
    rates = getCurrentRate()
    # return
    context = {'rates':rates}
    return render(request, 'base/index.html', context)

def signIn(request, method):
    # get sign in method
    # call relevant method
    if method == 'google':
        print('google')
        url = googleSignInFunction(request)
        return HttpResponseRedirect(url)

    context = {'err': 'Something went wrong while trying to trigger this authentication method. Try another method.'}
    return render(request, 'base/index.html', context)


def completeSignIn(request):
    context = {}
    return HttpResponseRedirect('Signed in')


def registrationRequest(request):

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        email = str(request.POST['email'])
        # verify otp
        otp_is_valid = validateOTP(email, str(request.POST['otp']))
        if otp_is_valid and form.is_valid():
            user = form.save()
            newCustomer = Customer.objects.create(user = user, email = email)
            login(request, user)
            return HttpResponseRedirect(reverse('base:index'))
        else:
            context = {'err' : 'Invalid email or OTP. Note that OTP is considered invalid after 5 mins.'}
            return render(request, 'base/err.html', context)
    else:
        form = UserCreationForm()
    context = { 'form': form}
    return render(request, 'base/login.html', context)

# get otp and send it back to user
def getOTP(request):
    # validate email
    verified_email = verifyEmail(str(request.GET.get('email')).strip())
    if verified_email['status'] != 200:
        return JsonResponse({'err' : verified_email['err']}, status = verified_email['status'])
    # check for email in db
    try:
        user = User.objects.get(email = verified_email['email'])
        return JsonResponse({'err' : 'A user with this email already exists.'}, status = 403)
    except User.DoesNotExist:
        # generate code
        code = str(random.randint(100000, 999999))
        # get or create email code obj for that email
        emailCode, created = EmailCode.objects.get_or_create(email = verified_email['email'])
        # get current time
        time_now = datetime.now()
        # check if user recently requested a code
        if checkHasRequested(time_now, emailCode.updated, 1):
            return JsonResponse({'err' : f'You must wait {60 - time_now.second} seconds before you request a new OTP.'}, status = 400)
        # if not, update the time of code and save it.
        emailCode.updated = time_now
        emailCode.otp = code
        emailCode.save()
        # mail code to user
        print(code)
        return JsonResponse({'msg' : 'code sent'} , status = 200)

def logout_request(request):
    logout(request)
    return HttpResponseRedirect(reverse('base:index'))