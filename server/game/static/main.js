"use strict"
const socket = io();

const USER_SETTINGS = new UserSettings();
const ping = new Ping();
let game = null;

// Add event listeners

// Open game settings when clicking on settings wheel
document.getElementById('settingsGear').addEventListener("click", settingsToggle);

// Update user settings when client changes them in the UI
document.querySelectorAll("settings-option").forEach((el) => el.addEventListener('setting-update', e => USER_SETTINGS.updateSetting(e.detail)));


// Socket events
socket.on("connect", () => setInterval(ping.sendPing, 3000));
socket.on("disconnect", () => {

    // If game is defined and the gameLoop is currently running
    if (game && game.gameLoop) game.end_game();

    ping.disconnected();
});
socket.on("error", (msg) => alert(msg))

socket.on("latency-pong", () => {
    const current_time = Date.now();
    const ping_start = ping.pingTime;

    const cur_ping = (current_time - ping_start) / 2;

    ping.addPing(cur_ping);
    ping.updatePing();
});

