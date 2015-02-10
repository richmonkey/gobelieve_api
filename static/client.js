var accessToken;
var refreshToken;
var username;
var users;
var base = 1000;
var msgLocalID=1;
var increase = 25;
var im;
var observer = {
    handlePeerMessage: function (msg) {
        console.log("msg sender:", msg.sender, " receiver:", msg.receiver, " content:", msg.content, " timestamp:", msg.timestamp);
        addMessage(msg.sender, msg.receiver, msg.content);
        $("#chatHistory").show();
    },
    handleMessageACK: function(msgLocalID, receiver) {
        console.log("message ack local id:", msgLocalID, " receiver:", receiver)
    },
    handleMessageFailure: function(msgLocalID, receiver) {
        console.log("message fail local id:", msgLocalID, " receiver:", receiver)
    },
    onConnectState: function(state) {
        if (state == IMService.STATE_CONNECTED) {
            console.log("im connected");
        } else if (state == IMService.STATE_CONNECTING) {
            console.log("im connecting");
        } else if (state == IMService.STATE_CONNECTFAIL) {
            console.log("im connect fail");
        } else if (state == IMService.STATE_UNCONNECTED) {
            console.log("im unconnected");
        }
    },
};

im = new IMService("im.yufeng.me", 13890, 0, observer, false);


function onLoginSuccess(result) {
    console.log("login success user id:", result.uid, 
                " access token:", result.access_token,  
                " status code:", status);
    username = result.uid
    accessToken = result.access_token
    refreshToken = result.refresh_token

    im.uid = result.uid
    im.start();

    setName();
    showChat();

    getContactList()
}

function getContactList() {
    $.ajax({
	url: "users",
	dataType: 'json',
        headers:{"Authorization":"Bearer " + accessToken},
	success: function(result, status, xhr) {
            for (var i in result) {
                contact = result[i]
                addUser(contact.uid)
                console.log("contact:", contact, contact.avatar, contact.name, contact.uid);
            }
	},
	error : function(xhr, err) {
	    console.log("get contact list err:", err, xhr.status)
	}
    }); 
}

function applogin() {
    console.log("app login sid:", sid)

    $.ajax({
	 url: "qrcode/login",
	 dataType: 'json',
	 data: {sid:sid},
	 success: function(result, status, xhr) {
             if (status == "success") {
                 onLoginSuccess(result)
             } else {
                 console.log("login error status:", status);
             }
	 },
	 error : function(xhr, err) {
	     console.log("login err:", err, xhr.status)
             if (xhr.status == 400) {
                 console.log("180s timeout")
             } else {
             }
	 }
    }); 
}
