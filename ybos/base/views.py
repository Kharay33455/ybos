from django.shortcuts import render
# used to query API
import requests
# used to get secrets with os.getenv('SECRETE_VALUE')
import os
# get date time
from datetime import datetime


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
    url = 'http://apilayer.net/api/live?access_key='+str(os.getenv('CURR_KEY'))+'&currencies=NGN&source=CNY'
    # make request and load response to json
    
    rates_data = requests.get(url)
    feedback = rates_data.json()
    
    
    #feedback = {'success': True, 'terms': 'https://currencylayer.com/terms', 'privacy': 'https://currencylayer.com/privacy', 'timestamp': 1740415631, 'source': 'CNY', 'quotes': {'CNYNGN': 206.807627}}
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


# index
def index(request):
    getTimeNow()
    # get current rates
    rates = getCurrentRate()
    # return
    context = {'rates':rates}
    return render(request, 'base/index.html', context)