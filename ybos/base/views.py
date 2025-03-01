from django.shortcuts import render
from django.urls import reverse
# used to query API
import requests
# used to get secrets with os.getenv('SECRETE_VALUE')
import os
from dotenv import load_dotenv

# get date time
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse

# import google auth libraries
import google.oauth2.credentials
import google_auth_oauthlib.flow


load_dotenv()
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

# validator
def validate(request, postData, dataType):
    postData = str(postData).strip()

    # make sure needed data is in list
    acceptableChars = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
    'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
    'W', 'X', 'Y', 'Z','a', 'b', 'c', 'd', 'e', 'f', 'g', 
    'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
    's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 1,2,3,4,5,6,7,8,9,0,'@', '.', ',']
    if dataType != 'Password':
        for char in postData:
            if char not in acceptableChars:
                err = f'You cannot use "{char}" in your {dataType}.'
                return {'status' : -99, 'err' : err}

    # make sure req data is not blank
    if dataType == 'Username' or dataType == 'Password' or dataType == 'Email':
        if postData == "":
            err =  f'{dataType} cannot be blank.'
            return {'status' : -99 , 'err' : err}

    if dataType == 'Password' and len(postData) < 10:
        print('here')
        err =  f'{dataType} must be at least 10 characters.'
        return {'status' : -99 , 'err' : err}

    
    return {'status' : 0 ,'val' : postData}















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


def loginRequest(request):
    nigerian_states = [
        "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno", 
        "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "Gombe", "Imo", "Jigawa", 
        "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", 
        "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara"
    ]
    if request.method == 'POST':
        username = validate(request, request.POST['username'], 'Username')
        
        if username['status'] != 0:
            print(username['status'])
            context = {'err' : username['err'], 'nigerian_states': nigerian_states}
            return render(request, 'base/login.html', context )
        else:
            username = username['val']
        
        email = validate(request, request.POST['email'] , 'Email')
        if email['status'] !=0:

            context = {'err':email['err'], 'nigerian_states': nigerian_states}
            return render(request, 'base/login.html', context )
        else:
            email = email['val']
        print(email)
        password = validate(request, request.POST['password'] , 'Password')
        if password['status'] !=0:
            context = {'err':password['err'], 'nigerian_states': nigerian_states}
            return render(request, 'base/login.html', context )
        else:
            password = password['val']
        address = validate(request, request.POST['address'], 'Address')
        if address['status'] !=0:
            context = {'err':address['err'], 'nigerian_states': nigerian_states}
            return render(request, 'base/login.html', context )
        else:
            address = address['val']
        state = validate(request, request.POST['state'], 'State')
        if state['status'] !=0:
            context = {'err':state['err'], 'nigerian_states': nigerian_states}
            return render(request, 'base/login.html', context )
        else:
            state = state['val']
        zipCode = validate(request, request.POST['zip'], 'Zip')
        if zipCode['status'] !=0:
            context = {'err':zipCode['err'], 'nigerian_states': nigerian_states}
            return render(request, 'base/login.html', context )
        else:
            zipCode = zipCode['val']

    context = {'nigerian_states' : nigerian_states}
    return render(request, 'base/login.html', context)