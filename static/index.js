
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

$(document).ready(applogin);
