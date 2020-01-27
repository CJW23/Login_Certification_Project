(function($) {
    "use strict";
    var input = $('.validate-input .input100'); //validate안에 input100 클래스

    $('.validate-form').on('submit', function() {
        var check = true;
        for (var i = 0; i < input.length; i++) {
            if (validate(input[i]) == false) {
                showValidate(input[i]);
                check = false;
            }
        }
        return check;
    });

    $('.validate-form .input100').each(function() {
        $(this).focus(function() {
            hideValidate(this);
        });
    });

    function validate(input) {
        if ($(input).attr('type') == 'email' || $(input).attr('name') == 'email') {
            if ($(input).val().trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) == null) {
                return false;
            }
        } else {
            if ($(input).val().trim() == '') {
                return false;
            }
        }
    }

    function showValidate(input) {
        var thisAlert = $(input).parent();
        $(thisAlert).addClass('alert-validate');
    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).removeClass('alert-validate');
    }

})(jQuery);

$('#login').on("click", function() {
    flag = false;
    email = $('#email').val();
    $.ajax({
        type: "POST",
        url: "checklogin",
        async: false,
        data: { email: $('#email').val(), password: $('#password').val() },
        success: function(data) {
            if (data['check'] == 'true') {
                alert("로그인 성공");
                flag = true;
            }
        }
    })
    if (flag == false) {
        alert("로그인 실패");
        return false;
    }
})

$(window).unload(function() {
    $.ajax({
        url: "/logout",
        type: "GET",
        async: false
    });
});