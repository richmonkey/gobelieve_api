
function applogin() {
    console.log("app login")

    $.ajax({
	 url: "qrcode/login",
	 dataType: 'json',
	 data: {sid:sid},
	 success: function(result, status, xhr) {
             if (status == "success") {
	         console.log("login success:", result, " status code:", status);
             } else {
                 console.log("login error status:", status);
             }
	 },
	 error : function(xhr, err) {
	     console.log("login err:", err, xhr.status)
             if (xhr.status == 400) {
                 console.log("180s timeout")
             } else {
                 //todo retry
             }
	 }
    }); 
}

$(document).ready(applogin);
