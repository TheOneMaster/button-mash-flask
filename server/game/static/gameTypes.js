class Game {
    /**
     * Base class for game types. Used to store base data and general functions
     * @param  {Number} maxTime Maximum amount of time the game can last for in seconds
     * @param  {Number} freq Update frequency of the game to the server
     */
    constructor(settings, maxTime, freq) {
        this.maxTime = maxTime;
        this.freq = freq;
        this.settings = settings;
        this.start_time = null;
    }

    updateSettings(freq, time) {
        this.freq = freq;
        this.maxTime = time;
    }
}

class TimeGame extends Game {
    /**
     * @param  {String} mashKey String representation of the mashing key
     * @param  {Number} maxTime Total length of the game in seconds
     * @param  {Number} freq Update frequency of the game
     */

    #updateCycle;
    #animationLoop;
    #current_score;

    constructor(settings, maxTime=10, freq=30) {
        super(settings=settings, maxTime=maxTime, freq=freq);

        this.score = 0;
        this.totalPresses = 0;
        this.tick = 0;

        this.start_time = null;
        this.current_time = null;

        this.#updateCycle = null;
        this.#animationLoop = null;
        this.#current_score = null;

        // DOM elements
        this.gameScreen = document.getElementById('lobbyMain');
    }

    initGame(settings) {
        
        document.body.addEventListener("keydown", this.#keypress);
        
        this.mashKey = settings.mashKey;
        this.start_time = Date.now()

        this.#updateCycle = setInterval(() => this.tickLoop(), 1000/this.freq);  // Update frequency of the game
        this.#animationLoop = requestAnimationFrame(() => this.gameLoop());        // Draw the score at 60 FPS
    }

    updateScore(score) {
        this.#current_score = score;
    }

    tickLoop() {
        this.current_time = Date.now();
        this.tick += 1;

        let msg = {
            tick_id: this.tick,
            score: game.totalPress
        };

        socket.emit("game-tick", msg);
    }

    gameLoop() {

        let scores = Object.values(this.#current_score);
        let max_score = Math.max(...scores);

        for (let username in this.#current_score) {
            // DOM elements
            let userDiv = this.gameScreen.querySelector(`[data-username="${username}"]`);
            let output = userDiv.querySelector('output');
            let score_bar = userDiv.querySelector('.score-bar');

            let user_score = this.#current_score[username];

            // Mark winning user as the green bar
            if (user_score === max_score) {
                score_bar.classList.add('score-winner');
            } else if (score_bar.classList.contains('score-winner')) {
                score_bar.classList.remove('score-winner');
            }

            // Calculate height of the score bar
            let cur_height_ratio = (user_score/20);
            let cur_height = cur_height_ratio * 600;

            // If the score of the user is above 20 CPS, make it golden
            if (cur_height_ratio >= 1) {
                score_bar.classList.add('score-damn');
            } else if (score_bar.classList.contains('score-damn')) {
                score_bar.classList.remove('score-damn');
            }

            score_bar.style.height = `${cur_height}px`;
            output.textContent = user_score;
        }

        this.#animationLoop = requestAnimationFrame(() => this.gameLoop())
    }

    endGame() {
        clearInterval(this.#updateCycle);
        cancelAnimationFrame(this.#animationLoop);

        socket.emit('game-end');
        this.resetGame();

        document.body.removeEventListener("keydown", this.#keypress);
    }

    resetGame() {
        this.score = 0;
        this.totalPresses = 0;
        this.tick = 0

        this.start_time = null;
        this.current_time = null;
        this.gameCycle = null;
    }

    #keypress(e) {
        if (e.code === this.mashKey) {
            this.score += 1;
        }
    }
}
