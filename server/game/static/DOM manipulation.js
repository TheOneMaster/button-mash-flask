"use strict"
function settingsToggle() {
    const settings = document.getElementById("gameSettings");
    settings.classList.toggle("hidden");
}

function setActiveLobby() {
    const lobby = document.getElementById("lobbyGrid");
    const rooms = lobby.childNodes;

    const active_class = "active-lobby";

    // Remove active class from currently selected room
    const current_room_active = rooms.querySelector(".active-lobby");
    if (current_room_active) current_room_active.classList.remove("active-lobby");

    // Set selected room as active
    this.classList.add(active_class);
}

