var base = 1000;
var increase = 25;

function getUserName(user) {
    if (user.name) {
        return user.name;
    } else {
        var uid = user.uid.toString(),
            i = uid.indexOf("0");
        return uid.substr(i + 1)
    }
}

var htmlLoyout = {
    buildUser: function (user) {
        var html = [];
        html.push('<li data-uid="' + user.uid + '">');
        html.push('    <img src="static/images/_avatar.png" class="avatar" alt=""/>');
        html.push('    <span class="name">' + getUserName(user) + '</span>');
        html.push('    <span class="uid">' + user.uid + '</span>');
        html.push('    <span class="num">' + (user.num || '') + '</span>');
        html.push('</li>');
        return html.join('');
    },
    buildText: function (msg) {
        var html = [];
        html.push('<li class="chat-item">');
        html.push('    <div class="message ' + msg.cls + '">');
        html.push('        <div class="bubble">' + msg.text + '</div>');
        html.push('    </div>');
        html.push('</li>');
        return html.join('');
    },
    buildAudio: function (msg) {
        var html = [];
        html.push('<li class="chat-item">');
        html.push('  <div class="message ' + msg.cls + '">');
        html.push('     <div class="bubble">');
        html.push('       <audio  controls="controls" src="' + msg.audio.url + '"></audio>');
        html.push('     </div>');
        html.push('  </div>');
        html.push('</li>');
        return html.join('');
    }
};
var node = {
    chatHistory: $("#chatHistory ul"),
    usersList: $('#usersList')
};
var process = {
    playAudio: function () {

    },
    appendAudio: function (m) {
        node.chatHistory.append(htmlLoyout.buildAudio(m));
    },
    appendText: function (m) {
        node.chatHistory.append(htmlLoyout.buildText(m));
    },
    msgTip: function (uid) {
        console.log(uid,'tip======');
        var userDom= node.usersList.find('li[data-uid="'+uid+'"]'),
            num = userDom.find('.num').text();
        if(!userDom.hasClass('active')){
            if(num){
                num++;
            }else{
                num = 1;
            }
            userDom.find('.num').text(num);
        }
    }
};

function scrollDown() {
    $('#chatHistory').scrollTop($('#chatHistory ul').outerHeight());
    $("#entry").text('').focus();
}

function appendMessage(msg) {
    var time = new Date(),
        m = {};
    if (msg.timestamp) {
        m.time = time.setTime(msg.timestamp * 1000)
    }
    if (im.uid == msg.sender) {
        m.cls = "message-out";
    } else {
        m.cls = "message-in";
    }
    if (msg.contentObj.text) {
        m.text = util.toStaticHTML(msg.contentObj.text);
        process.appendText(m);
    } else if (msg.contentObj.audio) {
        m.audio = msg.contentObj.audio;
        process.appendAudio(m);
    }
    console.log("uid:", im.uid, " sender:", msg.sender);
}

// add message on board
function addMessage(msg) {
    appendMessage(msg);
    scrollDown();
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

function addUser(user) {
    node.usersList.prepend(htmlLoyout.buildUser(user));
}


function setName(username) {
    $("#name").text(username);
}


function showLogin() {
    $("#loginView").removeClass('hide').show();
    $("#chat").addClass('hide').hide();
}


function showChat() {
    $("#loginView").addClass('hide').hide();
    $("#chat").removeClass('hide').show();
    //$("entry").focus();
    scrollDown();
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

    node.usersList.on('click', 'li', function () {
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
        _this.find('.num').text('');

        ///读取聊天记录添加到列表
        messages = imDB.loadUserMessage(uid);
        console.log("load user:", uid);
        node.chatHistory.html("");
        for (var i in messages) {
            var msg = messages[i];
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

            obj = {"text": msg}
            var textMsg = JSON.stringify(obj);

            var message = {
                sender: loginUser.uid,
                receiver: target,
                content: textMsg,
                msgLocalID: msgLocalID++,
                timestamp: (now.getTime() / 1000)
            };
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




