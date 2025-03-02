// compare password 1 to passwrd two and make sure they match
function comparePasswords(password1 , password2) {
    if (password1 === password2) {
        document.getElementById('passMismatch').innerHTML = '';
        document.getElementById('passMatch').innerHTML = 'Your passwords match. Proceed with sign in.'
        return true;
    }
    else {
        document.getElementById('passMismatch').innerHTML = 'Your passwords do not match. Check for error and try again.';
        document.getElementById('passMatch').innerHTML = ''
        return false;
    }
}


// make sure the password is 10 characters long or more
function checkPasswordLength(password1){
    if (password1.length < 10){
        document.getElementById('passMismatch').innerHTML = 'Your password must be at least 10 characters long.';
        document.getElementById('passMatch').innerHTML = '';
    }
}

// The form validator
function validateForm(){
    // get the passwords from the two boxes
    const password1 = document.getElementById('inputPassword').value;
    const password2 = document.getElementById('inputPassword2').value;

    // run the functions to validate it
    comparePasswords(password1, password2);
    checkPasswordLength(password1);
}


// retrieve password input boxes
const passwordBox1 = document.getElementById('inputPassword');
const passwordBox2 = document.getElementById('inputPassword2');

// add event listeners to validate passwords
passwordBox1.addEventListener('change', validateForm);
passwordBox2.addEventListener('change', validateForm);
