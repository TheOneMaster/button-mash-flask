"use strict"

class UserSettings {

  constructor(socket, username = "", lobby = "", mashKey = "Space") {
    this.socket = socket;
    this._username = username;
    this._room = lobby;
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
    if (new_name !== "" && new_name !== this.username) {
      this.socket.emit('username-change', new_name);
      this._username = new_name;
    }
  }

  get room() {
    return this._room;
  }

  set room(new_room) {
    if (new_room !== "" && new_room !== this.room) {
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

class EventHandlers {

  settingsToggle() {
    const settings = document.getElementById("gameSettings");
    settings.classList.toggle("hidden");
  }

  setActiveLobby() {
    const lobby = document.getElementById("lobbyGrid");
    const rooms = lobby.childNodes;

    const active_class = "active-lobby";

    // Remove active class from currently selected room
    const current_room_active = rooms.querySelector(".active-lobby");
    if (current_room_active) current_room_active.classList.remove("active-lobby");

    // Set selected room as active
    this.classList.add(active_class);
  }
}
