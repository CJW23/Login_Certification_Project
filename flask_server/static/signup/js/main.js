var flag1 = false;

$(function() {
    $('#submit').hide();
    $("#alert-success").hide();
    $("#alert-danger").hide();
    $("input").keyup(function() {
        var pwd1 = $("#pwd1").val();
        var pwd2 = $("#pwd2").val();
        if (pwd1 != "" || pwd2 != "") {
            if (pwd1 == pwd2) {
                $("#alert-success").show();
                $("#alert-danger").hide();
                flag1 = true;
            } else {
                $("#alert-success").hide();
                $("#alert-danger").show();
                flag1 = false;
            }
        }
    });
});


//이메일 인증 클릭
$('#certification').on("click", function() {
    if (!email_validate_check()) {
        return 0;
    }
    $.ajax({
        type: "GET",
        url: "/email",
        async: false,
        data: { address: $("#email").val() },
        success: function(data) {
            if (data['check'] == 'true') {
                alert('이메일로 인증을 진행해주세요');
                $('#certification').hide();
                $('#email').attr("readonly", true);
                emailCompleteCheck($("email").val());
            } else {
                alert('다른 이메일을 사용해주세요');
            }
        },

    })
})

$("#submit").on("click", function() {
    return checkValidate();
})

$(window).on('beforeunload', function() {
    alert("ascascac");
    $.ajax({
        url: "/logout",
        success: function(data) {
            return 0;
        }
    });
});

//이메일 인증 timeout 체크
function emailCompleteCheck(email) {
    $.ajax({
        type: "GET",
        url: "/emailcheck",
        data: { address: $("#email").val() },
        timeout: 180000,
        success: function(data) {
            if (data['complete'] == 'true') {
                alert('인증 완료');
                $('#submit').show();
            } else {
                alert("다시 이메일 인증 해주세요");
                $('#certification').show();
                $('#email').attr("readonly", false);
            }
        }
    })
}

function pwValidate(pwd) {
    var check = /^(?=.*[a-zA-Z])(?=.*[^a-zA-Z0-9])(?=.*[0-9]).{8,16}$/;
    if ((pwd.length < 8 || pwd.length > 16) || !check.test(pwd)) {
        alert("8~16자의 영문, 숫자, 특수문자 조합 비밀번호를 입력하세요");
        return false;
    }
    return true;
}

function checkValidate() {
    if (flag1 == true) {
        if (pwValidate($("#pwd1").val())) {
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

function email_validate_check() {
    var email = document.getElementById("email").value;
    var exptext = /^[A-Za-z0-9_\.\-]+@[A-Za-z0-9\-]+\.[A-Za-z0-9\-]+/;
    if (exptext.test(email) == false) {
        alert("이 메일형식이 올바르지 않습니다.");
        return false;
    }
    return true;
}