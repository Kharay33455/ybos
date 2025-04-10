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





// append single new meessage to box

const appendSingleMessage = (_fromUser, _image, _text) => {
    const new_message = document.createElement("div"); // create new div
    new_message.classList.add('newMessageDiv')
    _fromUser && new_message.classList.add('fromUser'); // add styling send/received

    if (_image) {    // only append image if exists
        const newMsgImg = document.createElement('img');// create elem
        newMsgImg.src = _image;  // add source
        newMsgImg.classList.add('newMsgImg');   // style image
        new_message.appendChild(newMsgImg); // append to the new message div
    }

    if (_text) { // if text in message
        const newMsgTxt = document.createElement('p'); // create new paragraph
        newMsgTxt.innerHTML = _text; // append the html to the text
        newMsgTxt.classList.add('newMsgTxt');   // style it up
        new_message.appendChild(newMsgTxt); // append to new message div
    }
    return new_message

}



// takes an image and converts it to base64
const convertImageToBase64 = (_imageFile) => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = function () {
            resolve(reader.result);
        };
        reader.onerror = function () {
            reject("Error reading file");
        };
        reader.readAsDataURL(_imageFile);

    })
}

const sendMessage = async () => {
    const textBox = document.getElementById('textBox'); // get text box
    const imageField = document.getElementById('imageToSend');  // get image field
    let base64Img = "";  // stores image in encoded format.. stores an empty string if no image is provided
    if (imageField.files[0]) {  // encode image if it exists
        base64Img = await convertImageToBase64(imageField.files[0]);
    }
    if (ws) {
        ws.send(JSON.stringify({ "text": textBox.value, "image": base64Img, "type" : "newMessage" }));
        textBox.value = "";
        imageField.value = "";
        document.getElementById('selectedImg').src = "";
    }
}

// append image to form when user has seleceted an image. makes them aware an imiage has been selecetd
const doStuff = async () => {
    const valueOfImage = document.getElementById('imageToSend');
    if (valueOfImage.files[0]) {
        const showTempImage = document.getElementById('selectedImg');
        showTempImage.src = await convertImageToBase64(valueOfImage.files[0]);
    }

}