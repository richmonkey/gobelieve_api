var base = 1000;
var increase = 25;

function getUserName(user) {
    if (user.name) {
        return user.name
    } else {
        uid = user.uid.toString()
        i = uid.indexOf("0")
        return uid.substr(i+1)
    }
}

//always view the most recent message when it is added
var htmlLoyout = {
    buildUser: function (user) {
        var html = [];
        html.push('<li data-uid="' + user.uid + '">');
        html.push('    <img src="static/images/_avatar.png" class="avatar" alt=""/>');
        html.push('    <span class="name">' + getUserName(user) + '</span>');
        html.push('</li>');
        return html.join('');
    },
    buildMsg: function (msg) {
        var html = [];
        html.push('<li class="chat-item">');
        html.push('    <div class="message ' + msg.cls + '">');
        html.push('        <div class="bubble">' + msg.text + '</div>');
        html.push('    </div>');
        html.push('</li>');
        return html.join('');

    }
};

function scrollDown(base) {
    window.scrollTo(0, base);
    $("#entry").text('').focus();
}

function appendMessage(msg) {
    time = new Date();
    if (msg.contentObj.text) {
        text = util.toStaticHTML(msg.contentObj.text);
    } else {
        console.log("unknow message type")
        return
    }
    if (msg.timestamp) {
        time.setTime(msg.timestamp*1000)
    }

    var m = {
        time: time,
        text: text,
    };
    
    console.log("uid:", im.uid, " sender:", msg.sender);
    if (im.uid == msg.sender) {
        m.cls = "message-out";
    } else {
        m.cls = "message-in";
    }

    $("#chatHistory ul").append(htmlLoyout.buildMsg(m));

}

// add message on board
function addMessage(msg) {
    appendMessage(msg);
    base += increase;
    window.scrollTo(0, base);
    $("#entry").text('').focus();
}

// show tip
function tip(type, name) {
    var tip, title;
    switch (type) {
        case 'online':
            tip = name + ' is online now.';
            title = 'Online Notify';
            break;
        case 'offline':
            tip = name + ' is offline now.';
            title = 'Offline Notify';
            break;
        case 'message':
            tip = name + ' is saying now.';
            title = 'Message Notify';
            break;
    }
    var pop = new Pop(title, tip);
}

// init user list
function initUserList(data) {
    var users = data.users, html = [];
    for (var i = 0; i < users.length; i++) {
        html.push('<li data-uid="' + users[i] + '">');
        html.push('    <img src="static/images/_avatar.png" class="avatar" alt=""/>');
        html.push('    <span class="name">' + users[i] + '</span>');
        html.push('</li>');
    }
    $("#usersList").html(html.join(''));
}


function addUser(user) {
    $("#usersList").append(htmlLoyout.buildUser(user));
}



function setName(username) {
    $("#name").text(username);
}


function showLogin() {
    $("#loginView").show();
    $("#chat").hide();
}


function showChat() {
    $("#loginView").hide();
    $("#chat").show();
    //$("entry").focus();
    scrollDown(base);
}

$(document).ready(function () {
    //when first time into chat room.
    console.log("show login");
    var sid = util.getCookie("sid");
    if (sid) {
        console.log("sid:", sid);
        showChat();
    } else {
        showLogin();
    }

    var usersList = $('#usersList');
    usersList.on('click', 'li', function () {
        var _this = $(this),
            uid = _this.attr('data-uid'),
            main = $('#main');

        if (peer == uid) {
            return;
        }

        $('#intro').hide();
        $('#to_user').text(uid);
        main.find('.chat-wrap').removeClass('hide');
        _this.addClass('active').siblings().removeClass('active');

        ///读取聊天记录添加到列表
        messages = imDB.loadUserMessage(uid)
        console.log("load user:", uid);
        $('#chatHistory ul').html("");
        for (var i in messages) {
            msg = messages[i];
            console.log("message:", msg);
            appendMessage(msg)
        }
        //设置当前会话uid
        peer = uid;
    });

    //deal with chat mode.
    $("#entry").keypress(function (e) {
        var target = parseInt($("#to_user").text());
        if (e.keyCode != 13 /* Return */) return;
        var msg = $("#entry").val().replace("\n", "");
        if (!util.isBlank(msg)) {
            var now = new Date();

            obj = {"text":msg}
            var textMsg = JSON.stringify(obj);

            var message = {sender: loginUser.uid, receiver: target, content: textMsg, msgLocalID: msgLocalID++, timestamp:(now.getTime()/1000)};
            message.contentObj = obj
            if (im.connectState == IMService.STATE_CONNECTED) {
                imDB.saveMessage(target, message);
                im.sendPeerMessage(message);
                $("#entry").val(""); // clear the entry field.
                addMessage(message);
                $("#chatHistory").show();
            }
        }
        return false;
    });

    applogin();
});




