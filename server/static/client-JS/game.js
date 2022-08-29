const socket = io();


socket.on('connect', ()=>{
    console.log(socket.id);
    console.log('test')
});

socket.on('settings', (options)=>{
    let room = options['room'];
    let room_str = document.getElementById("roomId-str");

    room_str.textContent = `Room ID: ${room}`;
})