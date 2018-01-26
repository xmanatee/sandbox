//Create an account on Firebase, and use the credentials they give you in place of the following

var config = {
    apiKey: "AIzaSyDxU1dbXJhvJ_wFtAuKQiSNbi5rns3DPJs",
    authDomain: "webrtc-test-a172f.firebaseapp.com",
    databaseURL: "https://webrtc-test-a172f.firebaseio.com",
    projectId: "webrtc-test-a172f",
    storageBucket: "webrtc-test-a172f.appspot.com",
    messagingSenderId: "22161990912"
};

var servers = {'iceServers':[
        {'urls': 'stun:stun.l.google.com:19302'},
        {'urls': 'stun:stun.services.mozilla.com'}
    ]};

firebase.initializeApp(config);

var database = null;
var yourVideo = null;
var friendsVideo = null;

var sessionIdInput = null;
var callButton = null;

var yourId = null;
var sessionId = null;

var pc = null;

function setupIds() {
    var hash_id = window.location.href.indexOf('#');
    console.log(hash_id);
    if (hash_id !== -1) {
        console.log("session_id from link");
        sessionId = window.location.href.substr(hash_id);
    } else if (localStorage.getItem("session_id")) {
        console.log("session_id from cookie");
        sessionId = localStorage.getItem("session_id");
    } else {
        console.log("session_id from random");
        sessionId = Math.random().toString(16).substr(4);
    }
    localStorage.setItem("session_id", sessionId);
    sessionIdInput.value = sessionId;
    yourId = Math.floor(Math.random() * 1000000000);
}

function sendMessage(senderId, data) {
    var msg = database.push({ sender: senderId, message: data });
    msg.remove();
}

function readMessage(data) {
    var msg = JSON.parse(data.val().message);
    var sender = data.val().sender;
    if (sender != yourId) {
        if (msg.ice != undefined)
            pc.addIceCandidate(new RTCIceCandidate(msg.ice));
        else if (msg.sdp.type == "offer")
            pc.setRemoteDescription(new RTCSessionDescription(msg.sdp))
                .then(() => pc.createAnswer())
                .then(answer => pc.setLocalDescription(answer))
                .then(() => sendMessage(yourId, JSON.stringify({'sdp': pc.localDescription})));
        else if (msg.sdp.type == "answer")
            pc.setRemoteDescription(new RTCSessionDescription(msg.sdp));
    }
};

function showMyFace() {
    navigator.mediaDevices.getUserMedia({audio:true, video:true})
        .then(stream => yourVideo.srcObject = stream)
        .then(stream => pc.addStream(stream));
}

function callClick() {
    sessionId = sessionIdInput.value;
    localStorage.setItem("session_id", sessionId);

    var maybeAddHash = window.location.href.indexOf('#') !== -1 ? "" : ("#" + sessionId);
    window.location.href = window.location.href + maybeAddHash;

    database = firebase.database().ref(sessionId);
    database.on('child_added', readMessage);

    pc.createOffer()
        .then(offer => pc.setLocalDescription(offer))
        .then(() => sendMessage(yourId, JSON.stringify({'sdp': pc.localDescription})));
}

function startCall(event) {
    callButton.disabled = true;
    sessionInput.style.visibility='hidden';

    console.log("startCall()");

    friendsVideo.srcObject = event.stream;
}

window.onload = function () {
    yourVideo = document.getElementById("your_video");
    friendsVideo = document.getElementById("friends_video");
    callButton = document.getElementById("call_button");
    sessionIdInput = document.getElementById("session_id");

    setupIds();

    pc = new RTCPeerConnection(servers);
    pc.onicecandidate = (event => event.candidate
        ? sendMessage(yourId, JSON.stringify({'ice': event.candidate}))
        : console.log("Sent All Ice"));
    pc.onaddstream = startCall;

    showMyFace();

    callButton.onclick = callClick;
};