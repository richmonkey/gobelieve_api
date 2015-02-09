
function applogin() {
    console.log("app login sid:", sid)

    $.ajax({
	 url: "qrcode/login",
	 dataType: 'json',
	 data: {sid:sid},
	 success: function(result, status, xhr) {
             if (status == "success") {
	         console.log("login success user id:", result.uid, 
                             " access token:", result.access_token,  
                             " status code:", status);
                 username = result.uid
                 receiver = 2000
                 addUser(receiver);
                 im.uid = result.uid
                 im.start();

                 setName();
                 showChat();
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
