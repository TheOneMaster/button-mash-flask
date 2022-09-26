function profileOptions() {
    let dropdownEl = document.getElementById('profileOptions');
    dropdownEl.classList.toggle('removed');
}

function event_listeners() {
    // Add event listeners
    let profile_image = document.getElementById('profileImage');

    // Only add event if logged in (profile picture is visible)
    if (profile_image !== null) {
        profile_image.addEventListener("click", profileOptions);
    }
}

event_listeners()
