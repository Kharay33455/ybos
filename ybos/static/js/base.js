// loading screen function. Handles showing and hiding of loading screen if needed
function loadingScreen(type) {
    // get loading screen element
    const loadingScreen = document.getElementById('loadingScreen');
    // hide or show as eneded
    loadingScreen.style.zIndex = type === 'show' ? '5' : '1';
};

function animateAuth(_authBox, _type){
    if(_type === 'show'){
        _authBox.classList.add('authAnimation')
        _authBox.style.top = '0vh';
        setTimeout(()=>{
            _authBox.classList.remove('authAnimation');
        }, 1000);
    }
    else{
        _authBox.classList.add('authAnimationReverse')
        _authBox.style.top = '100vh';
        setTimeout(()=>{
            _authBox.classList.remove('authAnimationReverse');
        }, 1000);  
    }
}

function callAuth(){
    const authBox = document.getElementById('authCont');
    const pos =  authBox.style.top;
    pos === '100vh' ? animateAuth(authBox, 'show') : animateAuth(authBox, 'hide');

}
// only run this after all HTML, CSS and JS are loading
window.onload = () => {
    // show fully loaded page
    document.getElementById('mainBody').style.opacity = 1;

    // get all links that involve load time
    const links = document.getElementsByClassName('loadTimeLink');
    // make array from DOM list received
    const linkList = Array.from(links);
    // lood through them and add an event listener to show loading screen when element is clicked
    linkList.forEach((item) => {
        item.addEventListener('click', function () {
            loadingScreen('show');
        });
    });
}