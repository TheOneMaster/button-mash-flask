class Game {
    /**
     * Base class for game types. Used to store base data and general functions
     * @param  {Number} maxTime Maximum amount of time the game can last for in seconds
     * @param  {Number} freq Update frequency of the game to the server
     */
    constructor(maxTime, freq) {
        this.maxTime = maxTime;
        this.freq = freq;
        this.startTime = null;
    }

    updateSettings(freq, time) {
        this.freq = freq;
        this.maxTime = time;
    }
}

class TimeGame extends Game {
    /**
     * @param  {Number} [maxTime=10] Total length of the game in seconds
     * @param  {Number} [freq=30] Update frequency of the game
     */
    constructor(maxTime=10, freq=30) {
        super(maxTime=maxTime, freq=freq);

        this.score = 0
        this.totalPresses = 0
        this.tick = 0

        this.current_time = null;
    }

    initGame() {

    }
}
