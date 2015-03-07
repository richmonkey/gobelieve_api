var accessToken;
var loginUser = {};

//当前会话的uid
var peer = 0;
var msgLocalID = 1;

var im;
var imDB = new IMDB();
var QRCODE_EXPIRE = 3 * 60 * 1000;
var startup = new Date();

var userDB = {
    users : new Array(),
    addUser : function(newUser) {
        var exists = false;
        for (var i in this.users) {
            var user = this.users[i];
            if (user.uid == newUser.uid) {
                exists = true;
            }
        }
        if (!exists) {
            this.users.push(newUser);
        }    
        return !exists;
    },
    findUser : function(uid) {
        for (var i in this.users) {
            var user = this.users[i];
            if (user.uid == uid) {
                return user;
            }
        }
        return null;
    }
}


var observer = {
    handlePeerMessage: function (msg) {
        console.log("msg sender:", msg.sender, " receiver:", msg.receiver, " content:", msg.content, " timestamp:", msg.timestamp);

        try {
            msg.contentObj = JSON.parse(msg.content)
        } catch (e) {
            console.log("json parse exception:", e);
            return
        }
        if (msg.sender == peer) {
            addMessage(msg);
        }
        imDB.saveMessage(msg.sender, msg);
        user = {uid : msg.sender};
        var inserted = userDB.addUser(user);
        if (inserted) {
            addUser(user);
        }
        process.msgTip(msg.sender);
    },
    handleMessageACK: function (msgLocalID, uid) {
        process.msgACK(msgLocalID,uid);
        console.log("message ack local id:", msgLocalID, " uid:", uid);
    },
    handleMessageRemoteACK: function (msgLocalID, uid) {
        process.msgRemoteACK(msgLocalID,uid);
        console.log("message remote ack local id:", msgLocalID, " uid:", uid);
    },
    handleMessageFailure: function (msgLocalID, uid) {
        console.log("message fail local id:", msgLocalID, " uid:", uid);
    },
    onConnectState: function (state) {
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
    loginUser.uid = result.uid;
    accessToken = result.access_token;

    im.uid = result.uid;
    im.start();

    setName(loginUser.name || helper.getPhone(loginUser.uid));
    showChat();

    getContactList()
}

function getContactList() {
    $.ajax({
        url: "users",
        dataType: 'json',
        headers: {"Authorization": "Bearer " + accessToken},
        success: function (result, status, xhr) {
            for (var i in result) {
                contact = result[i];
                userDB.addUser(contact);
                addUser(contact);
                console.log("contact:", contact, contact.avatar, contact.name, contact.uid);
            }
        },
        error: function (xhr, err) {
            console.log("get contact list err:", err, xhr.status)
        }
    });
}

function applogin() {
    console.log("app login sid:", sid);

    $.ajax({
        url: "qrcode/login",
        dataType: 'json',
        data: {sid: sid},
        success: function (result, status, xhr) {
            if (status == "success") {
                onLoginSuccess(result)
            } else {
                console.log("login error status:", status);
            }
        },
        error: function (xhr, err) {
            console.log("login err:", err, xhr.status);
            if (xhr.status == 400) {
                console.log("timeout");
                var now = new Date();
                var t = now.getTime() - startup.getTime();
                if (t > QRCODE_EXPIRE) {
                    //二维码过期
                    //todo隐藏二维
                    console.log("qrcode expires");
                    $('.qrcode-timeout').removeClass('hide');
                } else {
                    applogin();
                }
            } else {
            }
        }
    });
}
