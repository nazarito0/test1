// static/script.js
const socket = io();

socket.on('connect', function() {
    console.log('Підключено до сервера');
});

socket.on('new_message', function(data) {
    const messages = document.getElementById('messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message';
    msgDiv.innerHTML = `
        <span class="username">${data.username}:</span>
        <span class="timestamp">${data.timestamp}</span><br>
        ${data.message}
    `;
    messages.appendChild(msgDiv);
    messages.scrollTop = messages.scrollHeight;
});

document.getElementById('form').onsubmit = function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const message = document.getElementById('message').value;
    
    socket.emit('send_message', {
        username: username,
        message: message
    });
    
    document.getElementById('message').value = '';
};