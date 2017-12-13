const createKey = function(node, clickHandler) {
    var key = document.createElement('div');
    key.className = "key";
    key.onclick = clickHandler;
    node.appendChild(key);
};

// a, b, c, d, e, f, g
// la, si, do, re, mi, fa, sol

const NOTES = ["C", "D", "E", "F", "G", "A", "B"];
const OCTAVES = [3];

const player = function(instrument, note, octave, duration) {
    return function() {
        instrument.play(note, octave, duration);
    };
};

const createKeyboard = function(node, instrument, duration) {
    for (var i = 0; i < OCTAVES.length; ++i) {
        for (var j = 0; j < NOTES.length; ++j) {
            createKey(node, player(instrument, NOTES[j], OCTAVES[i], duration));
        }
    }
};

window.onload = function() {
    var piano = Synth.createInstrument('piano');
    var keyboard = document.getElementById("keyboard");

    createKeyboard(keyboard, piano, 2);
};