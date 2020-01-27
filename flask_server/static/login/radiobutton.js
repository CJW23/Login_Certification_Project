$.ajax({
    type: "POST",
    url: "/checkmanager",
    data: { email: $('#email').val() },
    success: function(data) {
        if (data['manager'] == 'true') {
            $('#manager').prop('checked', true);
        }
    }
})