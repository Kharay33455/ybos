# django modules
from django.shortcuts import render # to render html
from django.urls import reverse # generate url related to app only
from django.contrib.auth.models import User # user model
from django.contrib.auth import authenticate, login, logout, authenticate # handle auth
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse # responses
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm # Django forms

# python modules
import requests # used to query API
import os # the module to access the operating system
from dotenv import load_dotenv # python evn package
import string # contains all chars in ASCII
from .models import * # Database schema
import random # for randomization of all sorts
from datetime import datetime # get date time

# google auth libraries
import google.oauth2.credentials
import google_auth_oauthlib.flow

# load our environmental variables
load_dotenv()


def stripComma(num):
    newStr = ''
    counter = 0
    for _ in num:
        if _ != ',':
            newStr += num[counter]
        counter +=1
    return newStr

# check when last user requested code. Takes time now, time to compare and the duration period.
def checkHasRequested(time_now, updated, duration):
    if time_now.day != updated.day: # if it't not the same day
        value = False
        return value
    if time_now.hour != updated.hour:# if it's not the same hour
        value = False
        return value
    if time_now.minute - updated.minute < duration: # if day and hour is same, calculate for min
        value = True # 
    else:
        value = False
    return value

def endTransaction(_transaction, _remark):
    try:
        _transaction.completed = datetime.now()
        _transaction.wasSuccessful = False
        _transaction.remark = _remark
        _transaction.save()
    except Exception as e:
        ErrorLog.objects.create(error = e, user = request.user)

def getAllMessages(_transaction):
    messages = TransactionMessage.objects.filter(transaction = _transaction)
    sMessages = []
    for _ in messages:
        _.save()
        if _.image:
            image = _.image.url
        else:
            image = None
        sMessages.append({'text' : _.text, 'image' : image, 'fromUser' : _.fromUser})
    return sMessages

# gets the current time
def getTimeNow():
    timeNow = datetime.now().strftime("%H:%M:%S") # get current time in HH MM SS format
    return timeNow

#gets current rates
def getCurrentRate():
    # takes a value of hours and checks if it's AM or PM, normalize hour if in PM.
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
    
    # test feedback
    feedback = {'success': True, 'terms': 'https://currencylayer.com/terms', 'privacy': 'https://currencylayer.com/privacy', 'timestamp': 1740415631, 'source': 'CNY', 'quotes': {'CNYNGN': 206.807627}}
    
    # extract rates from data. This is the  buy rate. The sell rate is this minus 10
    buyRates = int(feedback['quotes']['CNYNGN'])
    sellRates = buyRates - 10
    # get the timestamp. Comes as HRMMSS
    _time = getTimeNow()
    # run the check time function on current Hour value to check if it's a morning or noon return
    timeHour = checkTime(_time[0:2])
    # construct time
    time = timeHour['time'] + ':' + _time[3:5] + ':'+ _time[6:8] +' ' + timeHour['isPM']
    # construct return dict and return
    return_dict = {'buyRates' : str(buyRates), 'sellRates' : str(sellRates), 'time' : time}
    return return_dict


def googleSignInFunction(request):
    # make secrets.json manually with data from env (see google auth docs)
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


#### see google docs for more explanations
    flow = google_auth_oauthlib.flow.Flow.from_client_config(secrets, scopes=['email']) # start flow to request just email
    host = request.get_host() # get host dynamically
    redirect_url = str(host)+'/sign-in/complete/' # redirect to complete page to allow user choose username after their email has been temporarily verified
    flow.redirect_uri = redirect_url
    authorization_url, state = flow.authorization_url(
    # Recommended, enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type='offline',
    # Optional, enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true',
    # Optional, set prompt to 'consent' will prompt the user for consent
    prompt='consent')
    return authorization_url    # state must be same as state sent to check and ensure requests and responses have not bee tampered with


# this function takes an amount and create a new transaction for that user provided
# they do not have an ongoing transaction
def newTransaction(_request, _amount):
    _amount = int(_amount)
    cus = Customer.objects.get(user = _request.user)
    existing = Transaction.objects.filter(customer = cus, completed = None)
    if existing:
        return existing[0]
    try:
        _transactionId = str(random.randint(1000000000000000, 9999999999999999999))
        new_transaction = Transaction.objects.create(customer = cus, amount = str(_amount), transactionId = _transactionId)
        TransactionMessage.objects.create(transaction = new_transaction, text = f'Requesting address for {_amount} Yuan.', fromUser = True)
        return new_transaction
    except Exception as e:
        ErrorLog.objects.create(error = e, user = _request.user)
        return 2



def validateOTP(email, _otp):
    isValid = True
    # does object exist
    try: 
        emailCodeObj = EmailCode.objects.get(email = email)
    except EmailCode.DoesNotExist: # this email has not been submited to us at all
        isValid = False
        return isValid
    
    # has another user claimed this object?
    try:
        cus = Customer.objects.get(email = email)
        isValid = False # someone else has already verified with this email
        return isValid
    except Customer.DoesNotExist:
        pass

    # check if code is valid
    if _otp != emailCodeObj.otp:
        isValid = False # otp doesnt match
        return isValid

    
    # is their otp still valid?
    timeNow = datetime.now()
    if checkHasRequested(timeNow, emailCodeObj.updated, 5): # check otp wasnt sent more than 5 mins ago
        return isValid
    else:
        isValid = False
        return isValid
        

# takes and email and checks for unwanted characters. Return 400 and error message if something is wrong with email, else return 200 and sterilized email
def verifyEmail(_email):
    # if email is empty string, break
    if _email == "":
        return {'err' : 'You must provide your email', 'status' : 400}
    # accept A-Z, a-z, 0-9, '@' , '.' , '_' and '+'
    acceptables = string.ascii_letters + string.digits + '@' + '.'+'_'+'-'+'+'
    # count where first unwanted character was found, if any. Breaks fundtion and return error and character
    counter = 0
    for _ in _email:
        if _ not in acceptables:
            return {'err' : f'You cannot use "{_email[counter]}" in your email.', 'status' : 400}
        counter += 1
    return {'status' : 200, 'email' : _email}





# buy yuan page
def buyYuan(request):
    # handle post
    if request.method == 'POST':
        # state variables
        nairaToYuan = 206
        nairaToDollar = 1500
        # get amount as int, return error if can't
        try:
            amount = stripComma(request.POST['amount'])
            amount = int(amount)
            if amount < 100:
                return JsonResponse({'err' : 'Least tradable amount is 100 CNY.'}, status = 403)
        except:
            return JsonResponse({'err' : 'Invalid amount'}, status = 403)
        # create new transaction
        transaction = newTransaction(request, amount)
        if transaction== 2:
            return JsonResponse({'err' : 'An unexpected error has occured.'}, status = 403)
        amount = transaction.amount # set to amount in case user is completing existing transaction and not startuing new
        # convert to naira
        amountInNaira = int(amount) * int(nairaToYuan)
        # convert to dollar to 2 decimal places
        amountInDollar = round(float(amountInNaira / nairaToDollar), 2)
        # get all messages pertaining to transaction
        messages = getAllMessages(transaction)
        # return values
        return JsonResponse({'amountInNaira' : amountInNaira, 'amountInDollar' : amountInDollar,'amountInYuan' : amount, 'transactionId' : transaction.transactionId, 'messages' : messages} , status = 200)
        
    # get request processing
    rates = getCurrentRate() # get rates
    context = {'rates': rates}  # make return dict and send with html
    return render(request, 'base/buy.html', context)

# index
def index(request):
    # get current rates
    rates = getCurrentRate()
    # return
    context = {'rates':rates}
    return render(request, 'base/index.html', context)

def signIn(request, method):
    # get sign in method
    # call relevant method
    if method == 'google':
        url = googleSignInFunction(request)
        return HttpResponseRedirect(url)
    # if no relevant method
    context = {'err': 'Something went wrong while trying to trigger this authentication method. Try another method.'}
    return render(request, 'base/index.html', context)


def completeSignIn(request):
    context = {}
    return HttpResponseRedirect('Signed in')


# register new users without any third party auth
def registrationRequest(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('base:index'))
    if request.method == 'POST': #user submiting form
        form = UserCreationForm(request.POST) # get the form
        email = str(request.POST['email']).strip() # get the email user attempts to reg with and convert to string. remove all trailing whitespaces
        # verify otp
        otp_is_valid = validateOTP(email, str(request.POST['otp'])) # takes email and otp and tries to verify it was the otp sent
        if otp_is_valid and form.is_valid():
            user = form.save() # create user
            newCustomer = Customer.objects.create(user = user, email = email) # create matching customer object
            login(request, user) # login the user
            return HttpResponseRedirect(reverse('base:index')) # send them back home as authenticated user
        else:
            # if user couldn't be created for some reason
            context = {'err' : 'Invalid email or OTP. Note that OTP is considered invalid after 5 mins.'}
            return render(request, 'base/err.html', context)
    else: # user requesting form
        form = UserCreationForm() # django form for creating new users.
        context = { 'form': form} 
        return render(request, 'base/reg.html', context) # see login form

# get otp and send it back to user
def getOTP(request):
    # validate email
    verified_email = verifyEmail(str(request.GET.get('email')).strip()) # validate that email doesn't contain any unwanted characters.
    if verified_email['status'] != 200: # if code is not 200, send error message and the unwanted character back to user
        return JsonResponse({'err' : verified_email['err']}, status = verified_email['status'])
    # check if a regstered user has already used this email
    try:
        # if user exist, return error
        user = User.objects.get(email = verified_email['email']) 
        return JsonResponse({'err' : 'A user with this email already exists.'}, status = 403)
    except User.DoesNotExist: # if none, proceed with email verification
        # generate code
        code = str(random.randint(100000, 999999))
        # get email if this isnt their first verification attempt, it it isnt, create new
        emailCode, created = EmailCode.objects.get_or_create(email = verified_email['email'])
        # get current time
        time_now = datetime.now()
        # check if user recently requested a code in the last 1 min
        if checkHasRequested(time_now, emailCode.updated, 1): # see function
            return JsonResponse({'err' : f'You must wait {60 - time_now.second} seconds before you request a new OTP.'}, status = 400) # if time hasnt elapsed, return error and time left to wait
        # if not, update the time of code and the new code and save it.
        emailCode.updated = time_now
        emailCode.otp = code
        emailCode.save()
        # mail code to user
        print(code)
        return JsonResponse({'msg' : 'code sent'} , status = 200)

# logout request
def logout_request(request):
    logout(request) # log out user
    return HttpResponseRedirect(reverse('base:index')) # return them back home. Unauthenticated

def endChat(request):
    # get user customer object
    _cus = Customer.objects.get(user = request.user)
    # end all trnasactions for this user
    transactions = Transaction.objects.filter(customer = _cus, wasSuccessful = None, completed = None)
    for _ in transactions:
        #end transaction
        endTransaction(_, 'Aborted by customer.')
    return HttpResponseRedirect(reverse('base:buyYuan'))
    

# this allows users to log in ad out of their accounts
def login_request(request):
    if request.user.is_authenticated:   # if user is already authenticated, just redirect them home
        return HttpResponseRedirect(reverse('base:index'))
    if request.method == 'POST':    # if user is submiting a new request, clean data and attempt auth
        _username = str(request.POST['username']).strip()
        _password = str(request.POST['password']).strip()
        user = authenticate(username= _username, password = _password)
        if user is not None:    # user exist with these datails?    login and redirect home.
            login(request, user)
            return HttpResponseRedirect(reverse('base:index'))
        else:   # user doesnt?  show form to reattempt login and display incorrect details error message
            form = AuthenticationForm()
            context = {'err' : 'Incorrect username or password.', 'form' : form}
            return render(request, 'base/login.html', context)
    # if user has sent a get request?   get django form to return, style on front end.
    form = AuthenticationForm()
    context = {'form' : form}
    return render(request, 'base/login.html', context)




### ADMINISTRATIVE FUNCTIONALITIES

def adminChat(request):
    if request.user.is_authenticated and request.user.is_superuser:
        trans = Transaction.objects.all()
        context = {'trans' : trans}
        return render(request, 'base/adminChat.html', context)
    else:
        return HttpResponse(status = 404)

def adminMessages(request, transId):
    if request.user.is_authenticated and request.user.is_superuser:
        _transaction = Transaction.objects.get(transactionId = transId)
        messages = TransactionMessage.objects.filter(transaction = _transaction)
        context = {'messages' : messages, 'transaction' : _transaction}
        return render(request, 'base/messages.html', context)
    else:
        return HttpResponse(status = 404)
