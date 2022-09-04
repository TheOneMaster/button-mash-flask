// JS for the HTML

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

socket.on("connect", () => {
  // console.log(socket.id);
});

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

  let clientList = []
  for (let client in clients) {
    let clone = template.cloneNode(true);
    let name = clone.querySelector("h3");

    clone.dataset.sid = client;

    name.textContent = clients[client];
    
    clientList.push(clone);

  }

  console.log(clientList)

  client_screen.replaceChildren(...clientList);

})

socket.on("lobby-update", (rooms) => {

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

socket.on("start-game", () => {
  console.log("Starting game");
  game.initGame();
});

socket.on("waiting-game", () => {
  console.log("Waiting for other players");
});

socket.on("game-score", (score) => {
  console.log(score);
});

const game = {
  maxTime: 10,
  totalPress: 0,
  score: 0,

  start_time: undefined,
  current_time: undefined,

  mash_key: " ",

  // FPS
  freq: 30,
  tick: 0,

  resetGame: function () {
    game.totalPress = 0;
    game.score = 0;

    game.start_time = undefined;
    game.current_time = undefined;

    game.tick = 0;
  },

  initGame: function () {
    game.setCallbacks();

    game.start_time = new Date().getTime();

    let gameloop = setInterval(game.gameLoop, 1000 / game.freq);
    setTimeout(() => game.gameEnd(gameloop), 1000 * game.maxTime);
  },

  setCallbacks: function () {
    let gameContainer = document.getElementById("gameMain");
    gameContainer.addEventListener("keydown", game.__keypress__);
    gameContainer.focus();
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

  gameEnd: function (loop) {
    clearInterval(loop);
    socket.emit("game-end");
    game.resetGame();

    let gameContainer = document.getElementById("gameMain");
    gameContainer.removeEventListener("keydown", game.__keypress__);
  },

  __keypress__: function (e) {
    if (game.mash_key == e.key) {
      game.totalPress += 1;
    }
  },
};
