const errMsg = document.getElementById('err');
const proceedMsg = document.getElementById('msg');

// compare password 1 to passwrd two and make sure they match
function comparePasswords(password1 , password2) {
    if (password1 === password2) {
        errMsg.innerHTML = '';
        proceedMsg.innerHTML = 'Your passwords match. Proceed with sign in.'
        return true;
    }
    else {
        errMsg.innerHTML = 'Your passwords do not match. Check for error and try again.';
        proceedMsg.innerHTML = ''
        return false;
    }
}


// make sure the password is 10 characters long or more
function checkPasswordLength(password1){
    if (password1.length < 10){
        errMsg.innerHTML = 'Your password must be at least 10 characters long.';
        proceedMsg.innerHTML = '';
    }
}

// The form validator
function validateForm(){
    // get the passwords from the two boxes
    const password1 = document.getElementById('id_password1').value;
    const password2 = document.getElementById('id_password2').value;

    // run the functions to validate it
    comparePasswords(password1, password2);
    checkPasswordLength(password1);
}


// fucntion to retrive otp from backend to validate email
async function requestOTP(){
    const email = document.getElementById('exampleFormControlInput1').value;
    if (email === ""){
        errMsg.innerHTML = 'You must provide your email, human.';
        proceedMsg.innerHTML = '';
        return;
    }
    
    const host = (window.location.host).toString();
    
    const resp = await fetch('http://'+host+'/ybos/get-otp/?email='+email);

    const result = await resp.json();
    if (resp.status !== 200){
        errMsg.innerHTML = result['err'];
        proceedMsg.innerHTML = '';
    }
    else
    {
        errMsg.innerHTML = '';
        proceedMsg.innerHTML = 'Enter the 6 digits pin we just sent to you. Check your spam if you cannot find it in your primary mailbox.';
    }
}


// append all event listeners

// retrieve password input boxes
const passwordBox1 = document.getElementById('id_password1');
const passwordBox2 = document.getElementById('id_password2');
// add event listeners to validate passwords
passwordBox1.addEventListener('input', validateForm);
passwordBox2.addEventListener('input', validateForm);