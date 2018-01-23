//Create an account on Firebase, and use the credentials they give you in place of the following
// var config = {
//   apiKey: "AIzaSyCTw5HVSY8nZ7QpRp_gBOUyde_IPU9UfXU",
//   authDomain: "websitebeaver-de9a6.firebaseapp.com",
//   databaseURL: "https://websitebeaver-de9a6.firebaseio.com",
//   storageBucket: "websitebeaver-de9a6.appspot.com",
//   messagingSenderId: "411433309494"
// };

var config = {
    apiKey: "AIzaSyDxU1dbXJhvJ_wFtAuKQiSNbi5rns3DPJs",
    authDomain: "webrtc-test-a172f.firebaseapp.com",
    databaseURL: "https://webrtc-test-a172f.firebaseio.com",
    projectId: "webrtc-test-a172f",
    storageBucket: "webrtc-test-a172f.appspot.com",
    messagingSenderId: "22161990912"
};

firebase.initializeApp(config);

var database = firebase.database().ref();
var yourVideo = null;
var friendsVideo = null;
var callButton = null;

var yourId = Math.floor(Math.random()*1000000000);

var servers = {'iceServers':[
    {'urls': 'stun:stun.services.mozilla.com'},
    {'urls': 'stun:stun.l.google.com:19302'},
    {'urls': 'turn:numb.viagenie.ca','credential': 'websitebeaver','username': 'websitebeaver@email.com'}]};

var pc = new RTCPeerConnection(servers);
pc.onicecandidate = (event => event.candidate?sendMessage(yourId, JSON.stringify({'ice': event.candidate})):console.log("Sent All Ice"));
pc.onaddstream = (event => friendsVideo.srcObject = event.stream);

function sendMessage(senderId, data) {
    var msg = database.push({ sender: senderId, message: data });
    console.log("1");
    msg.remove();
}

function readMessage(data) {
    var msg = JSON.parse(data.val().message);
    console.log("2");
    var sender = data.val().sender;
    if (sender != yourId) {
        console.log("3");
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

database.on('child_added', readMessage);

function showMyFace() {
  navigator.mediaDevices.getUserMedia({audio:true, video:true})
    .then(stream => yourVideo.srcObject = stream)
    .then(stream => pc.addStream(stream));
}

function showFriendsFace() {
  pc.createOffer()
    .then(offer => pc.setLocalDescription(offer) )
    .then(() => sendMessage(yourId, JSON.stringify({'sdp': pc.localDescription})) );
}

window.onload = function () {
    yourVideo = document.getElementById("yourVideo");
    showMyFace();
    callButton = document.getElementById("callButton");
    friendsVideo = document.getElementById("friendsVideo");


    callButton.onclick = showFriendsFace;
};