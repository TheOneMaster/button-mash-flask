// JS for the HTML
"use strict"

const eventHandlers = {
  settingsToggle: function () {
    let settings = document.getElementById("gameSettings");
    settings.classList.toggle("hidden");
  },

  activeLobby: function () {
    let lobby = document.getElementById('lobbyGrid');
    let rooms = lobby.childNodes;

    let active = 'active-lobby'

    for (let room of rooms) {

      let class_check = room.classList.contains(active);

      if (class_check) room.classList.remove(active);
    }

    this.classList.add(active)
  },

};

function addEventHandlers() {
  let settings_gear = document.getElementById("settingsGear");

  settings_gear.addEventListener("click", eventHandlers.settingsToggle);
}

// Socket IO stuff

const socket = io();

function changeRoom() {
  let room_entry = document.getElementById("roomId");
  let curRoom = document.getElementById("roomId-str");

  curRoom = curRoom.textContent.slice(17);
  let room = room_entry.value;

  if (room && room !== curRoom) {
    socket.emit("room-change", Number(room));
    room_entry.value = "";
  }
}

function changeUsername() {
  let userString = document.getElementById("username-str");
  let username = userString.dataset.str;

  let usernameInp = document.getElementById("usernameInp");
  let inpString = usernameInp.value;

  if (inpString && username !== inpString) {
    socket.emit("username-change", inpString);
    usernameInp.value = "";
  }
}

function startGame() {
  socket.emit('game-ready');
}

let ping = undefined;
let ping_start = undefined;
let ping_loop = undefined;
let pingEl = undefined;

function sendPing() {
  ping_start = new Date().getTime();
  socket.volatile.emit('latency-ping');
}


socket.on("connect", () => {
  ping_loop = setInterval(sendPing, 3000);
  sendPing();
});

socket.on("disconnect", () => {
  console.log("disconnected");

  if (game.gameLoop !== undefined) {
    game.gameEnd()
  }

})

socket.on('latency-pong', () => {
  let current_time = new Date().getTime();

  ping = (current_time - ping_start) / 2;

  if (pingEl === undefined) {
    pingEl = document.getElementById('pingOutput');
  }

  pingEl.textContent = ping;

  console.log(ping)
})


socket.on("error", (msg) => {
  alert(msg);
});

socket.on("client-settings", (json) => {
  let username = json.username;
  let room = json.room;

  let curUserEl = document.getElementById("username-str");
  let curUser = curUserEl.dataset.str;

  if (!curUser || curUser !== username) {
    curUserEl.dataset.str = username;
    curUserEl.textContent = `Username: ${username}`;
  }

  let curRoomEl = document.getElementById("roomId-str");
  let curRoom = curRoomEl.dataset.room;

  if (!curRoom || curRoom !== room) {
    curRoomEl.dataset.room = room;
    curRoomEl.textContent = `Current room ID: ${room}`;
  }

  // console.log("Updated settings");
});

socket.on('room-update', (clients) => {

  let template = document.getElementById('clientMain').content.firstElementChild;
  let client_screen = document.getElementById('lobbyMain');

  let curUserEl = document.getElementById('username-str');
  let curUser = curUserEl.dataset.str;

  let clientList = []
  for (let client in clients) {
    let clone = template.cloneNode(true);
    let name = clone.querySelector("h3");

    let username = clients[client]

    clone.dataset.username = username;

    if (username === curUser) {
      name.textContent = `${username} - (You)`
      name.classList.add("current-user");
    } else{
      name.textContent = username;
    }
    
    clientList.push(clone);
  }

  // console.log(clientList)

  client_screen.replaceChildren(...clientList);

})

socket.on("lobby-update", (rooms) => {

  /* Create the list of lobbies when a change in the lobby is made */

  let template = document.getElementById('roomTemplate').content.firstElementChild;
  let grid = document.getElementById('lobbyGrid');

  // Create list of lobbies from json file
  let rows = []
  for (let room in rooms) {
    let clone = template.cloneNode(true);
    let button = clone.querySelector("h4");
    let circle = clone.querySelector(".circle");

    clone.dataset.num = room;
    button.textContent = room;

    if (rooms[room] <= 3) {
      circle.classList.add("open-lobby");
    } else {
      circle.classList.add("closed-lobby");
    }

    clone.addEventListener('click', eventHandlers.activeLobby)

    rows.push(clone);

  }

  grid.replaceChildren(...rows);



  return
});

// Game events
socket.on("start-game", (settings) => {
  console.log("Starting game");

  let freq = settings.freq;
  let time = settings.time;

  game.updateSettings(freq, time);

  // Hide div in middle of screen
  let buttonsDiv = document.getElementById("gameButtons");
  buttonsDiv.classList.add("removed");

  game.initGame();
});

socket.on("waiting-game", () => {
  console.log("Waiting for other players");

  // Hide start button and show waiting text
  let start_button = document.getElementById('game-start');
  start_button.classList.add("hidden");

  let waitEl = document.getElementById('game-waiting');
  waitEl.classList.remove('hidden');

});

socket.on("game-score", (score) => {
  let gameLobby = document.getElementById('lobbyMain');

  for (let username in score) {
    let userDiv = gameLobby.querySelector(`[data-username="${username}"]`);
    let output = userDiv.querySelector('output');

    output.textContent = score[username];
  }

  console.log(score)
});

socket.on('game-end', () => {
  game.gameEnd()
})

const game = {
  maxTime: 5,
  totalPress: 0,
  score: 0,

  start_time: undefined,
  current_time: undefined,

  mash_key: " ",

  // FPS
  freq: 30,
  tick: 0,

  gameLoop: undefined,

  updateSettings(freq, time) {
    this.freq = freq;
    this.maxTime = time;
  },

  resetGame: function () {
    game.totalPress = 0;
    game.score = 0;

    game.start_time = undefined;
    game.current_time = undefined;

    game.tick = 0;

    game.gameLoop = undefined;
  },

  initGame: function () {
    game.setCallbacks();

    game.start_time = new Date().getTime();

    game.gameLoop = setInterval(game.gameLoop, 1000 / game.freq);
    // setTimeout(() => game.gameEnd(gameloop), 1000 * game.maxTime);
  },

  setCallbacks: function () {
    // let gameContainer = document.getElementById("gameMain");
    document.body.addEventListener("keydown", game.__keypress__);
    // gameContainer.focus();
  },

  gameLoop: function () {
    game.current_time = new Date().getTime();
    game.tick += 1;

    let msg = {
      tick_id: game.tick,
      score: game.totalPress,
    };

    socket.emit("game-tick", msg);
  },

  gameEnd: function () {
    clearInterval(game.gameLoop);
    socket.emit("game-end");
    game.resetGame();

    // let gameContainer = document.getElementById("gameMain");
    document.body.removeEventListener("keydown", game.__keypress__);
  },

  __keypress__: function (e) {
    if (game.mash_key == e.key) {
      game.totalPress += 1;
    }
  },
};
