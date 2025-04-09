let ws = undefined;

const transId = document.getElementById('tId').innerHTML;

console.log(transId)
const transWS = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + transId
    + '/'
);

transWS.onmessage = function (e) {
    const resp = JSON.parse(e.data);
    const msgListContainer = document.getElementById('messagesContainer'); // get text container
    msgListContainer.appendChild(appendSingleMessage(resp['fromUser'], resp['image'], resp['message']));  // append the new message to the message box
};

transWS.onclose = function (e) {
    console.log('socket closed');
};
ws = transWS;

