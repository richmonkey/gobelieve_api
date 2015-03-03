var base = 1000;
var increase = 25;

var helper = {
    toTime: function (ts) {
        //时间戳取时间
        var d = ts ? new Date(ts) : new Date();
        var H = d.getHours();
        var m = d.getMinutes();
//            var s = date.getSeconds();
        return H + ':' + (m < 10 ? '0' + m : m);
    },
    getUserName: function (user) {
        if (user.name) {
            return user.name;
        } else {
            var uid = user.uid.toString(),
                i = uid.indexOf("0");
            return uid.substr(i + 1)
        }
    },
    getUserAvatar: function (user) {
        if (user.avatar) {
            var parser = document.createElement('a');
            parser.href = user.avatar;
            return parser.path;
        } else {
            return '';
        }
    },
    getPhone: function (phone) {
        if (phone) {
            return (phone + '').split('860')[1];
        } else {
            return ''
        }
    },
};
var htmlLoyout = {
    buildUser: function (user) {
        var html = [];

        html.push('<li data-uid="' + user.uid + '">');
        if (user.avatar) {
            html.push('    <img src="' + helper.getUserAvatar(user) + '" class="avatar" alt=""/>');
        } else {
            html.push('    <img src="static/images/_avatar.png" class="avatar" alt=""/>');
        }
        if (helper.getUserName(user)) {
            html.push('    <span class="name">' + helper.getUserName(user) + '</span>');
        }else{
            html.push('    <span class="uid">' + helper.getPhone(user.uid) + '</span>');
        }
        html.push('    <span class="num">' + (user.num || '') + '</span>');
        html.push('</li>');
        return html.join('');
    },
    buildText: function (msg) {
        var html = [];
        html.push('<li class="chat-item" data-id="' + msg.id + '">');
        html.push('    <div class="message ' + msg.cls + '">');
        html.push('        <div class="bubble"><p class="pre">' + msg.text + '</p>');
        html.push('           <span class="time">' + helper.toTime(msg.timestamp * 1000) + '</span>');
        html.push('        </div>');
        html.push('    </div>');
        html.push('</li>');
        return html.join('');
    },
    buildImage: function (msg) {
        var html = [];
        html.push('<li class="chat-item"  data-id="' + msg.id + '">');
        html.push('    <div class="message">');
        html.push('        <div class="bubble"><p class="pre"><a href="' + msg.image + '" target="_blank">' +
            '<img class="image-thumb-body" src="' + msg.image + '" /></p></a>');
        html.push('           <span class="time">' + helper.toTime(msg.timestamp * 1000) + '</span>');
        html.push('        </div>');
        html.push('    </div>');
        html.push('</li>');
        return html.join('');
    },
    buildAudio: function (msg) {
        var html = [];
        html.push('<li class="chat-item"  data-id="' + msg.id + '">');
        var audio_url = msg.audio.url + ".mp3";
        html.push('<li class="chat-item">');
        html.push('  <div class="message ' + msg.cls + '">');
        html.push('     <div class="bubble">');
        html.push('       <p class="pre"><audio  controls="controls" src="' + audio_url + '"></audio></p>');
        html.push('       <span class="time">' + helper.toTime(msg.timestamp * 1000) + '</span>');
        html.push('     </div>');
        html.push('  </div>');
        html.push('</li>');
        return html.join('');
    },
    buildACK: function () {
        return '<span class="ack"></span>';
    },
    buildRACK: function () {
        return '<span class="rack"></span>';
    }
};
var node = {
    chatHistory: $("#chatHistory ul"),
    usersList: $('#usersList'),
    exit: $('#exit')
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
    appendImage: function (m) {
        node.chatHistory.append(htmlLoyout.buildImage(m));
    },
    msgTip: function (uid) {
        var userDom = node.usersList.find('li[data-uid="' + uid + '"]'),
            num = '';
        if (userDom) {
            num = userDom.find('.num').text();
            if (!userDom.hasClass('active')) {
                if (num) {
                    num++;
                } else {
                    num = 1;
                }
                userDom.find('.num').text(num);
            }
            node.usersList.prepend(userDom);
        }
    },
    msgACK: function (msgID, uid) {
        node.chatHistory.find('li[data-id="' + msgID + '"] .bubble').append(htmlLoyout.buildACK());
    },
    msgRemoteACK: function (msgID, uid) {
        node.chatHistory.find('li[data-id="' + msgID + '"] .bubble').append(htmlLoyout.buildRACK());
    }
};

function scrollDown() {
    $('#chatHistory').scrollTop($('#chatHistory ul').outerHeight());
    $("#entry").text('').focus();
}

function appendMessage(msg) {
    var time = new Date(),
        m = {};
    m.id = msg.msgLocalID;
    if (msg.timestamp) {
        time.setTime(msg.timestamp * 1000);
        m.timestamp = msg.timestamp;
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
    } else if (msg.contentObj.image) {
        m.image = msg.contentObj.image;
        process.appendImage(m);
    }
    console.log("uid:", im.uid, " sender:", msg.sender, " receiver:", msg.receiver);
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
    node.exit.on('click', function () {
        document.cookie = 'sid=';
        document.cookie = 'token=';
        location.reload();
    });
    node.usersList.on('click', 'li', function () {
        var _this = $(this),
            uid = _this.attr('data-uid'),
            main = $('#main');

        if (peer == uid) {
            return;
        }
        $('#intro').hide();
        $('#to_user').attr('data-uid', uid);
        user = userDB.findUser(uid);
        if (user) {
            $('#to_user').text(helper.getUserName(user));
        } else {
            $('#to_user').text(helper.getPhone(uid));
        }
        if (user.avatar) {
            $('#to_user_avatar').src = helper.getUserAvatar(user);
        }

        main.find('.chat-wrap').removeClass('hide');
        _this.addClass('active').siblings().removeClass('active');
        _this.find('.num').text('');
        ///读取聊天记录添加到列表
        var messages = imDB.loadUserMessage(uid);
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
        if (e.keyCode != 13) return;
        var target = parseInt($("#to_user").attr("data-uid"));
        var msg = $("#entry").val().replace("\n", "");
        if (!util.isBlank(msg)) {
            var now = new Date();
            var obj = {"text": msg};
            var textMsg = JSON.stringify(obj);
            var message = {
                sender: loginUser.uid,
                receiver: target,
                content: textMsg,
                msgLocalID: msgLocalID++,
                timestamp: (now.getTime() / 1000)
            };
            message.contentObj = obj;
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




