$('#submit').on('click', function() {
    var post_url = $('form').attr("action");
    var request_method = $('form').attr("method");
    var form_data = $('form').serialize() + "&token=" + getCookie('token');
    //alert(form_data);
    var pwd1 = $("#password1").val();
    var pwd2 = $("#password2").val();
    if (pwd1 != "" || pwd2 != "") {
        if (pwd1 == pwd2) {
            flag1 = true;
        } else {
            flag1 = false;
        }
    }
    if (checkValidate()) {
        //alert("zczxcxzc");
        $.ajax({
            url: post_url,
            type: request_method,
            data: form_data,
            success: function(data) {
                if (data['flag'] == "true") {
                    window.location.href = "/";
                }
            }
        });

        return false;
    }
    return false;
})

function checkValidate() {
    if (flag1 == true) {
        if (pwValidate($("#password1").val())) {
            flag1 = false;
            return true;
        } else {
            flag1 = false;
            return false;
        }
    } else {
        alert("비밀번호가 정확하지 않습니다.");
        return false;
    }
}

function pwValidate(pwd) {
    var check = /^(?=.*[a-zA-Z])(?=.*[^a-zA-Z0-9])(?=.*[0-9]).{8,16}$/;
    if ((pwd.length < 8 || pwd.length > 16) || !check.test(pwd)) {
        alert("8~16자의 영문, 숫자, 특수문자 조합 비밀번호를 입력하세요");
        return false;
    }
    return true;
}

function getCookie(c_name) {
    var i, x, y, ARRcookies = document.cookie.split(";");
    for (i = 0; i < ARRcookies.length; i++) {
        x = ARRcookies[i].substr(0, ARRcookies[i].indexOf("="));
        y = ARRcookies[i].substr(ARRcookies[i].indexOf("=") + 1);
        x = x.replace(/^\s+|\s+$/g, "");
        if (x == c_name) {
            return unescape(y);
        }
    }
}