var accessToken;
var loginUser = {};
var users = new Array();

//当前会话的uid
var peer = 0;
var msgLocalID=1;

var im;
var imDB = new IMDB();

var observer = {
    handlePeerMessage: function (msg) {

        console.log("msg sender:", msg.sender, " receiver:", msg.receiver, " content:", msg.content, " timestamp:", msg.timestamp);

        try{
            msg.contentObj = JSON.parse(msg.content)
        }catch(e){
            console.log("json parse exception:", e)
            return
        }
        if (msg.sender == peer) {
            addMessage(msg);
        }
        process.msgTip(msg.sender);
        imDB.saveMessage(msg.sender, msg);
        var exists = false;
        for (var i in users) {
            var user = users[i]
            if (user.uid == msg.sender) {
                exists = true;
            }
        }
        if (!exists) {
            user = {uid:msg.sender}
            addUser(user);
            users.push(user)
        }
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
    }
};

im = new IMService("im.yufeng.me", 13890, 0, observer, false);


function onLoginSuccess(result) {
    console.log("login success user id:", result.uid, 
                " access token:", result.access_token,  
                " status code:", status);
    loginUser.uid = result.uid
    accessToken = result.access_token

    im.uid = result.uid
    im.start();

    setName(loginUser.uid);
    showChat();

    getContactList()
}

function getContactList() {
    $.ajax({
	url: "users",
	dataType: 'json',
        headers:{"Authorization":"Bearer " + accessToken},
	success: function(result, status, xhr) {
            users = result
            for (var i in result) {
                contact = result[i]
                addUser(contact);
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
                 console.log("timeout")
             } else {
             }
	 }
    }); 
}
