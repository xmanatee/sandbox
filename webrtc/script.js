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

var videoBox = null;
var yourVideo = null;
var friendsVideo = null;

var sessionIdInput = null;
var callButton = null;

var yourId = null;
var sessionId = null;

var pc = null;

function setupIds() {
    var hash_id = window.location.href.indexOf('#');
    if (hash_id !== -1) {
        sessionId = window.location.href.substring(hash_id + 1);
    } else if (localStorage.getItem("session_id")) {
        sessionId = localStorage.getItem("session_id");
    } else {
        // console.log("session_id from random");
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
        if (msg.ice != undefined) {
            console.log("1");
            pc.addIceCandidate(new RTCIceCandidate(msg.ice));
            console.log("1");
        } else if (msg.sdp.type == "offer") {
            console.log("2");
            pc.setRemoteDescription(new RTCSessionDescription(msg.sdp))
                .then(() => pc.createAnswer())
                .then(answer => pc.setLocalDescription(answer))
                .then(() => sendMessage(yourId, JSON.stringify({'sdp': pc.localDescription})));
            console.log("2");
        } else if (msg.sdp.type == "answer") {
            console.log("3");
            pc.setRemoteDescription(new RTCSessionDescription(msg.sdp));
            console.log("3");
        }
    }
};

function showMyFace() {
    navigator.mediaDevices.getUserMedia({audio:true, video:true})
        .then(stream => yourVideo.srcObject = stream)
        .then(stream => pc.addStream(stream));
}

function callClick() {
    console.log("callClick()");
    sessionId = sessionIdInput.value;
    localStorage.setItem("session_id", sessionId);

    var hash_id = window.location.href.indexOf('#');
    window.location.href = window.location.href.substring(0, hash_id) + "#" + sessionId;

    callButton.disabled = true;
    callButton.innerHTML = "Waddup...";
    sessionIdInput.style.display = 'none'; // .visibility='hidden';
    videoBox.style.height = '90%';

    database = firebase.database().ref(sessionId);
    database.on('child_added', readMessage);

    pc.createOffer()
        .then(offer => pc.setLocalDescription(offer))
        .then(() => sendMessage(yourId, JSON.stringify({'sdp': pc.localDescription})));
}

function startCall(event) {
    callButton.innerHTML = "Rock";

    console.log("startCall()");

    friendsVideo.srcObject = event.stream;
}

window.onload = function () {
    videoBox = document.getElementById("video_box")
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