from django.shortcuts import render
from django.urls import reverse
# used to query API
import requests
# used to get secrets with os.getenv('SECRETE_VALUE')
import os
# get date time
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse

# import google auth libraries
import google.oauth2.credentials
import google_auth_oauthlib.flow

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
    secrets = {"web": {"client_id": "229371508083-mls99c3b0295kc1v4hq2njg0us53o5bd.apps.googleusercontent.com",
                        "project_id": "ybos-451917",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_secret": "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",
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
    context = {'err': 'Something went wrong while trying to trigger this authentication method. Try another.'}
    return render(request, 'base/index.html', context)


def completeSignIn(request):
    context = {}
    return HttpResponseRedirect('Signed in')