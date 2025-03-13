let ws = undefined;

// message box to display error and messages.
const msgBox = document.getElementById('msgBox');

// this function shows messages to user. Ok messages in green, others in red
function showMessage(message, type) {
    msgBox.innerHTML = message;
    if (type === 'proceed') {
        // chnge text color to gtreen
        msgBox.style.color = 'green';
    }
    else {
        // change text color to red
        msgBox.style.color = 'red';
    }
}



// 1 dollar = 1500 naira = 7.28
// 1 yuan == 206 naira 

/// _yth = yuanToNaira rates and _dtn is dollar to naira rates && _dty = dollarToYuan
function getDollarToYuan(_ytn, _dtn) {
    const _dty = (_dtn / _ytn);
    return _dty;
}

// takes a number and add commas at thousands to make it user friendly to read
function commalizeNum(number) {
    let numAsStr = number.toString(); // convert num to string

    if (numAsStr.length < 4) {    // if number isnt in thousands, return as is
        return numAsStr;
    }

    let remainder = numAsStr.split('.')[1];// split number into 2 by decimal. remaider is eveythinh after the decimal
    if (remainder !== undefined) {
        remainder = Array.from(remainder)[1]; // get digits in remainder in an array
    }
    else {
        remainder = 0; // if nothing after decimal, remainder is 0.
    }
    const toAdd = remainder > 0 ? 1 : 0; // if remainder at all, add 1
    numAsStr = numAsStr.split('.')[0]; // this eveything before the decimal
    const strLen = numAsStr.length; // number length
    numAsStr = numAsStr + toAdd; // add approximated remainder

    // if whole num is more than 3, add commas where nessasary
    if (strLen > 3) {
        let newStr = '';
        for (let i = 0; i < strLen; i++) {
            newStr = newStr + numAsStr[i];
            if ((strLen - i - 1) % 3 === 0 && i != strLen - 1) {
                newStr = newStr + ',';
            }
            // if decimal encoutered , break.
            if (numAsStr[i] === '.') {
                return newStr;
            }
        }
        // return cnum with comma
        return newStr;
    }
    else {
        // if num was never in the thousands, return as is.
        return numAsStr;
    }
}

// takes a number and remove all that isnt string
function decommalizeNum(num) {
    // take num as str and convert it to an array
    let formToEdit = Array.from(num);
    // make a array of accptables, check and only apppend to new str chars in acceptables
    const acceptableNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    let newStr = ''
    formToEdit.forEach((item) => {
        if (acceptableNumbers.includes(item)) {
            newStr = newStr + item;
        }
    })
    // return as number
    return Number(newStr);
}

// _ctc = currency being inputed
function convertCurrency(_ctc) {
    // get form being inputed
    const parentForm = document.getElementById(_ctc);
    // get value of form and remove all that isnt digit
    let formToEdit = decommalizeNum(parentForm.value);
    // add commma and set as value of field being edited
    parentForm.value = commalizeNum(formToEdit);

    // get rates from servers and online resources
    const rates = document.getElementById('ratesNow').innerHTML;
    const dollarToNaira = 1500;

    // edit other form values according to what input is being edited
    switch (_ctc) {
        case "amountUSD":
            const dollarToYuan = getDollarToYuan(rates, dollarToNaira)
            // set yuan val for that usd amount
            document.getElementById('amountCNY').value = commalizeNum(formToEdit * dollarToYuan);
            // get naira val for that usd amount
            document.getElementById('amountNGN').value = commalizeNum(formToEdit * dollarToNaira);
            break;
        case "amountNGN":
            // set dollar field
            document.getElementById('amountUSD').value = commalizeNum(formToEdit / dollarToNaira);
            // set yuan field
            document.getElementById('amountCNY').value = commalizeNum(formToEdit / rates);
            break;
        case "amountCNY":
            // get usd equivalent    
            document.getElementById('amountUSD').value = commalizeNum(formToEdit / getDollarToYuan(rates, dollarToNaira));
            // get naira equivalent
            document.getElementById('amountNGN').value = commalizeNum(formToEdit * rates);
            break;
    }
}

// this function take all the messages returned from server and displayed them in a styled list.
function appendMessagesToBox(_messages) {
    const msgListContainer = document.getElementById('messages'); // get text container
    _messages.forEach((item) => {   // loop through all
        const new_message = document.createElement("div"); // create new div
        new_message.classList.add('newMessageDiv')
        item['fromUser'] && new_message.classList.add('fromUser'); // add styling send/received
        if (item['image']) {    // only append image if exists
            const newMsgImg = document.createElement('img');// create elem
            newMsgImg.src = item['image'];  // add source
            newMsgImg.classList.add('newMsgImg');   // style image
            new_message.appendChild(newMsgImg); // append to the new message div
        }
        if (item['text']) { // if text in message
            const newMsgTxt = document.createElement('p'); // create new paragraph
            newMsgTxt.innerHTML = item['text']; // append the html to the text
            newMsgTxt.classList.add('newMsgTxt');   // style it up
            new_message.appendChild(newMsgTxt); // append to new message div
        }
        msgListContainer.appendChild(new_message);  // append the new message to the message box
    })
}

async function sendAmount() {
    const form = new FormData();
    const amount = document.getElementById('amountCNY').value;
    // append the amount in yuan
    form.append('amount', amount);
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0];
    console.log(csrf.value);

    const host = (window.location.host).toString();
    resp = await fetch('/buy-yuan',
        {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrf.value
            },
            body: form
        }
    )

    const result = await resp.json();
    if (resp.status === 200) {
        // show transaction chat
        const transBox = document.getElementById('transact');
        transBox.style.opacity = '1';
        transBox.style.zIndex = '8';

        console.log('BAck');
        console.log(commalizeNum(await result['amountInNaira']), result['amountInDollar'], commalizeNum(result['amountInDollar']) + '.' + (result['amountInDollar']).toString().split('.')[1]);
        document.getElementById('amount').innerHTML = commalizeNum(await result['amountInYuan']);
        const messages = result['messages'];
        // append all the mwssages to the message box
        appendMessagesToBox(messages);
        // open new websocket
        const transId = result['transactionId'];
        const transWS = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/'
            + transId
            + '/'
        );

        transWS.onmessage = function (e) {
            console.log(e.data);
        };

        transWS.onclose = function (e) {
            console.log('socket closed');
        };
        loadingScreen('hide');
        ws = transWS;
    }
    else {

        if (result['err']) {
            showMessage(result['err'], 'err');
        }
    }
    loadingScreen('hide');

}

