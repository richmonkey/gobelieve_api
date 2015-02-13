//always view the most recent message when it is added
var htmlLoyout = {
    buildUser: function (user) {
        var html = [];
        html.push('<li data-uid="' + user + '">');
        html.push('    <img src="static/images/_avatar.png" class="avatar" alt=""/>');
        html.push('    <span class="name">' + user + '</span>');
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

// add message on board
function addMessage(from, target, text, time) {
    var name = (target == '*' ? 'all' : target);
    if (text === null) return;
    if (time == null) {
        // if the time is null or undefined, use the current time.
        time = new Date();
    } else if ((time instanceof Date) === false) {
        // if it's a timestamp, interpret it
        time = new Date(time);
    }
    text = util.toStaticHTML(text);
    var msg = {
        time: time,
        text: text,
        cls:'message-out'

    };
    $("#chatHistory ul").append(htmlLoyout.buildMsg(msg));

    //every message you see is actually a table with 3 cols:
    //  the time,
    //  the person who caused the event,
    //  and the content
//    var messageElement = $(document.createElement("table"));
//    messageElement.addClass("message");
    // sanitize
//    text = util.toStaticHTML(text);
//    var content = '<tr>' + '  <td class="date">' + util.timeString(time) + '</td>' + '  <td class="nick">' + util.toStaticHTML(from) + ' says to ' + name + ': ' + '</td>' + '  <td class="msg-text">' + text + '</td>' + '</tr>';
//    messageElement.html(content);
//    the log is the stream that we view
//    $("#chatHistory").append(messageElement);

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

// add user in user list
function addUser(user) {
//    var slElement = $(document.createElement("option"));
//    slElement.attr("value", user);
//    slElement.text(user);
    $("#usersList").append(htmlLoyout.buildUser(user));
}

// remove user from user list
function removeUser(user) {
    $("#usersList option").each(
        function () {
            if ($(this).val() === user) $(this).remove();
        });
}

// set your name
function setName() {
    $("#name").text(username);
}

// show login panel
function showLogin() {
    $("#loginView").show();
    $("#chatHistory").hide();
    $("#toolbar").hide();
    $("#loginUser").focus();
}

// show chat panel
function showChat() {
    $("#loginView").hide();
    $("#toolbar").show();
    $("#chatHistory").show();
    $("entry").focus();
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
        $('#intro').hide();
        $('#to_user').text(uid);
        main.find('.chat-wrap').removeClass('hide');
        _this.addClass('active').siblings().removeClass('active');

        ///读取聊天记录添加到列表

        $('#chatHistory ul').html(htmlLoyout.buildMsg({time: 1234567891, text: '你好！'+uid, cls: 'message-out'}));
        $('#chatHistory ul').append(htmlLoyout.buildMsg({time: 1234567891, text: 'Hello！', cls: 'message-in'}));


    });

    //deal with chat mode.
    $("#entry").keypress(function (e) {
        var target = parseInt($("#to_user").text());
        if (e.keyCode != 13 /* Return */) return;
        var msg = $("#entry").val().replace("\n", "");
        if (!util.isBlank(msg)) {
            var message = {sender: username, receiver: target, content: msg, msgLocalID: msgLocalID++};
            if (im.connectState == IMService.STATE_CONNECTED) {
                im.sendPeerMessage(message);
                $("#entry").val(""); // clear the entry field.
                if (target != '*' && target != username) {
                    addMessage(username, target, msg);
                    $("#chatHistory").show();
                }
            }
        }
        return false;
    });

    applogin();
});




