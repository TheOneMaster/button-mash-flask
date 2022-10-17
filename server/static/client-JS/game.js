"use strict"

class UserSettings {
  /**
   * Storage class for user settings
   * @param  {Socket} socket SocketIO Client Object
   * @param  {String} username Client username
   * @param  {Number} lobby Client room number
   * @param  {String} mashKey String representation of keyboard key to mash
   */
  constructor(socket, username = null, lobby = null, mashKey = "Space") {
    this.socket = socket;
    this.username = username;
    this.room = lobby;
    this.mashKey = mashKey;
  }

  // Set client properties when first connecting to Server
  setUsername(new_name) {
    this._username = new_name
  }

  setRoom(new_room) {
    this._room = new_room;
  }

  // Manipulate Client properties from browser
  get username() {
    return this._username;
  }

  set username(new_name) {
    if (new_name !== null && new_name !== this.username) {
      this.socket.emit('username-change', new_name);
      this._username = new_name;
    }
  }

  get room() {
    return this._room;
  }

  set room(new_room) {
    if (new_room !== null && new_room !== this.room) {
      socket.emit('room-change', new_room);
      this._room = new_room;
    }
  }


}

class Ping {
  constructor() {
    this.pings = []
    this.pingTime = null;
  }

  getPing() {
    let ping_sum = this.pings.reduce((a, b) => a + b, 0);
    let ping_length = this.pings.length;

    return Math.floor(ping_sum / ping_length);
  }

  sendPing = () => {
    this.pingTime = new Date().getTime();
    socket.volatile.emit('latency-ping');
  }

  /**
   * Add a ping value to the list of ping values
   * @param {Number} ping latency value from the most recent ping
   */
  addPing(ping) {
    
    this.pings.push(ping);

    if (this.pings.length > 5) {
      this.pings = this.pings.slice(1, this.pings.length);
    }
  }

  updatePing() {
    let pingEl = document.getElementById('pingOutput');
    pingEl.textContent = `${this.getPing()} ms`;
  }

  disconnected() {
    let pingEl = document.getElementById('pingOutput');
    pingEl.textContent = 'disconnected';
  }
}

const eventHandlers = {
  // Global event handlers for the DOM are stored here

  settingsToggle: function () {
    // Toggle settings menu visibility
    let settings = document.getElementById("gameSettings");
    settings.classList.toggle("hidden");
  },

  activeLobby: function () {
    // Set currently clicked lobby as "active"

    let lobby = document.getElementById('lobbyGrid');
    let rooms = lobby.childNodes;

    let active = 'active-lobby';

    for (let room of rooms) {

      let class_check = room.classList.contains(active);

      if (class_check) room.classList.remove(active);
    }

    this.classList.add(active)
  },

  editUsername: function () {

    // Get current username
    let usernameEl = document.getElementById("username");
    let username = USER_SETTINGS.username;

    // Replace span with input
    let inputEl = document.createElement("input");
    inputEl.id = "usernameInput";
    inputEl.value = username;                       // Add current username to the input element text

    usernameEl.replaceWith(inputEl);

    inputEl.addEventListener("keypress", (e) => {
      if (e.key === 'Enter') {
        eventHandlers.saveUsername();
      }
    })

    inputEl.focus()

    let editUserEl = document.getElementById('editUsername');
    editUserEl.removeEventListener("click", eventHandlers.editUsername);
    editUserEl.addEventListener("click", eventHandlers.saveUsername);
  },

  saveUsername: function () {

    let inputEl = document.getElementById("usernameInput");
    let newUsername = inputEl.value.trim()

    let newUsernameEl = document.createElement("span");
    newUsernameEl.id = "username";

    newUsernameEl.textContent = newUsername;
    inputEl.replaceWith(newUsernameEl);

    // Set new username
    USER_SETTINGS.username(newUsername);

    let editUserEl = document.getElementById('editUsername');
    editUserEl.removeEventListener("click", eventHandlers.saveUsername);
    editUserEl.addEventListener("click", eventHandlers.editUsername);
  },

  editRoom: function () {
    let roomEl = document.getElementById("room");
    let roomNum = Number(roomEl.textContent);

    let roomInput = document.createElement("input");
    roomInput.id = "roomInput";
    roomInput.value = roomNum;

    roomEl.replaceWith(roomInput);

    roomInput.addEventListener("keypress", (e) => {
      if (e.key === 'Enter') {
        eventHandlers.saveRoom();
      }
    })

    roomInput.focus();

    let editRoomEl = document.getElementById("editRoom");
    editRoomEl.removeEventListener("click", eventHandlers.editRoom);
    editRoomEl.addEventListener("click", eventHandlers.saveRoom);

  },

  saveRoom: function () {
    let inputEl = document.getElementById("roomInput");
    let newRoom = inputEl.value.trim();

    let newRoomEl = document.createElement("span");
    newRoomEl.id = "room";

    newRoomEl.textContent = newRoom;
    inputEl.replaceWith(newRoomEl);

    newRoom = Number(newRoom)
    USER_SETTINGS.room = newRoom;

    let editRoomEl = document.getElementById('editRoom');
    editRoomEl.removeEventListener("click", eventHandlers.saveRoom);
    editRoomEl.addEventListener("click", eventHandlers.editRoom);
  },

  editMashKey: function () {
    let mashKeyEl = document.getElementById('mashKey');
    let editMashKeyEl = document.getElementById('editMashKey');

    let inputMashKey = document.createElement('input');
    inputMashKey.id = "mashKeyInput";

    mashKeyEl.replaceWith(inputMashKey);

    inputMashKey.focus();

    function saveMashKey(e) {
      let key = e.code;
      USER_SETTINGS.mashKey = key;

      let newMashKeyEl = document.createElement("span");
      newMashKeyEl.id = "mashKey";
      newMashKeyEl.textContent = key;

      inputMashKey.replaceWith(newMashKeyEl);

      editMashKeyEl.addEventListener("click", eventHandlers.editMashKey)

    }

    inputMashKey.addEventListener("keypress", saveMashKey)

    editMashKeyEl.removeEventListener("click", eventHandlers.editMashKey);

  }
};

function addEventHandlers() {

  // Add event handlers to the DOM on initial page load

  // Settings wheel click listener
  let settings_gear = document.getElementById("settingsGear");
  settings_gear.addEventListener("click", eventHandlers.settingsToggle);

  // Edit & Save username
  let options = ['editUsername', 'editRoom', 'editMashKey'];

  for (let option of options) {
    let editEl = document.getElementById(option);

    if (editEl !== null) {
      editEl.addEventListener("click", eventHandlers[option]);
    }
  }

  document.getElementById("mashKey").textContent = USER_SETTINGS.mashKey;

}

// Socket IO stuff

const socket = io();
const USER_SETTINGS = new UserSettings(socket);
const PING = new Ping()

function startGame() {
  socket.emit('game-ready');
}

function updateRoomClientsList(clients) {

  let template = document.getElementById('room-client-template').content.firstElementChild;
  let client_list = document.getElementById('room-client-list');

  let client_arr = [];
  for (let client in clients) {
    let clone = template.cloneNode(true);
    clone.dataset.client = client;

    let username = clients[client];
    let name = clone.querySelector('span');
    name.textContent = username;

    if (username === USER_SETTINGS.username) {
      clone.classList.add('current-user');

      let options = clone.querySelector('.room-client-options');
      options.classList.add('hidden');
    }

    client_arr.push(clone);
  }

  client_list.replaceChildren(...client_arr);

}


socket.on("connect", () => {
  setInterval(PING.sendPing, 3000);
});

socket.on("disconnect", () => {
  console.log("disconnected");

  if (game.gameLoop !== undefined) {
    game.gameEnd();
  }

  PING.disconnected();
})

socket.on('latency-pong', () => {
  let current_time = new Date().getTime();
  let ping_start = PING.pingTime;

  let cur_ping = (current_time - ping_start) / 2;

  PING.addPing(cur_ping);
  PING.updatePing();
})


socket.on("error", (msg) => {
  alert(msg);
});

socket.on("client-settings", (json) => {
  let username = json.username;
  let room = json.room;

  USER_SETTINGS.setUsername(username)
  USER_SETTINGS.setRoom(room);

  let usernameEl = document.getElementById("username");
  usernameEl.textContent = username;

  let roomEl = document.getElementById('room');
  roomEl.textContent = room;
});

socket.on('room-update', (clients) => {

  let template = document.getElementById('clientMain').content.firstElementChild;
  let client_screen = document.getElementById('lobbyMain');

  let curUser = USER_SETTINGS.username;

  let clientList = []
  for (let client in clients) {
    let clone = template.cloneNode(true);
    let name = clone.querySelector("h3");

    let username = clients[client]

    clone.dataset.username = username;

    if (username === curUser) {
      name.textContent = `${username} (You)`
      name.classList.add("current-user");
    } else {
      name.textContent = username;
    }

    clientList.push(clone);
  }

  // console.log(clientList)

  client_screen.replaceChildren(...clientList);

  updateRoomClientsList(clients);

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

  let scores = Object.values(score);
  let max_score = Math.max(...scores)

  for (let username in score) {
    let userDiv = gameLobby.querySelector(`[data-username="${username}"]`);
    let output = userDiv.querySelector('output');
    let score_bar = userDiv.querySelector('.score-bar');

    let cur_score = score[username];

    if (cur_score === max_score) {
      score_bar.classList.add('score-winner');
    } else if (score_bar.classList.contains('score-winner')) {
      score_bar.classList.remove('score-winner');
    }

    let cur_height_ratio = (cur_score / 20);    // Goddamn, imagine having more than 20 cps
    let cur_height = cur_height_ratio * 600

    if (cur_height_ratio >= 1) {
      score_bar.classList.add('score-damn');
    } else if (score_bar.classList.contains('score-damn') && cur_height_ratio < 1) {
      score_bar.classList.remove('score-damn');
    }

    score_bar.style.height = `${cur_height}px`;

    output.textContent = score[username];
  }

  console.log(score);
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

  gameInterval: undefined,

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

    game.gameInterval = undefined;
  },

  initGame: function () {
    game.setCallbacks();

    game.mash_key = USER_SETTINGS.mashKey;

    game.start_time = new Date().getTime();

    game.gameInterval = setInterval(game.gameLoop, 1000 / game.freq);
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
    clearInterval(game.gameInterval);
    socket.emit("game-end");
    game.resetGame();

    // let gameContainer = document.getElementById("gameMain");
    document.body.removeEventListener("keydown", game.__keypress__);
  },

  __keypress__: function (e) {
    if (game.mash_key == e.code) {
      game.totalPress += 1;
    }
  },
};

addEventHandlers();
