// var config = {
//     apiKey: "AIzaSyCTw5HVSY8nZ7QpRp_gBOUyde_IPU9UfXU",
//     authDomain: "websitebeaver-de9a6.firebaseapp.com",
//     databaseURL: "https://websitebeaver-de9a6.firebaseio.com",
//     storageBucket: "websitebeaver-de9a6.appspot.com",
//     messagingSenderId: "411433309494"
// };

var config = {
    apiKey: "AIzaSyDxU1dbXJhvJ_wFtAuKQiSNbi5rns3DPJs",
    authDomain: "webrtc-test-a172f.firebaseapp.com",
    databaseURL: "https://webrtc-test-a172f.firebaseio.com",
    projectId: "webrtc-test-a172f",
    storageBucket: "",
    messagingSenderId: "22161990912"
};

var database;
var yourVideo;
var friendsVideo;
var callButton;
var yourId;
var servers = {
    'iceServers': [
        {'urls': 'stun:stun.services.mozilla.com'},
        {'urls': 'stun:stun.l.google.com:19302'},
        {'urls': 'turn:numb.viagenie.ca', 'credential': 'websitebeaver', 'username': 'websitebeaver@email.com'}]
};
var pc;

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
}

function showMyFace() {
    navigator.mediaDevices.getUserMedia({audio:true, video:true})
        .then(stream => yourVideo.srcObject = stream)
        .then(stream => pc.addStream(stream));
}

function showFriendsFace() {
    pc.createOffer()
        .then(offer => pc.setLocalDescription(offer))
        .then(() => sendMessage(yourId, JSON.stringify({'sdp': pc.localDescription})));
}

window.onload = function () {

    firebase.initializeApp(config);

    database = firebase.database().ref();
    yourVideo = document.getElementById("yourVideo");
    friendsVideo = document.getElementById("friendsVideo");
    callButton = document.getElementById("callButton");

    yourId = Math.floor(Math.random()*1000000000);

    pc = new RTCPeerConnection(servers);

    pc.onicecandidate = (event => event.candidate ?
        sendMessage(yourId, JSON.stringify({'ice': event.candidate})) :
        console.log("Sent All Ice") );
    pc.onaddstream = (event => friendsVideo.srcObject = event.stream);

    database.on('child_added', readMessage);

    callButton.onclick = showFriendsFace;
    showMyFace();
};
