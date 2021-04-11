function CallGetFunction() {
    jQuery.ajax({
    type: "GET",
    url: '/runPython',
    data:'',
    beforeSend: function() {
        // handle request before send
        $(".message_box > .animate_box > .loader_placeholder").addClass('loader')
        $(".message_box > .message").text("Running python script...")
        $(".mainStep_button").attr("disabled", true);
    }
    })
    .fail(function(xhr, status, error) {
        $(".message_box > .animate_box > .loader_placeholder").removeClass('loader')
        $(".message_box > .message").text("Failed, "+error);
        $(".mainStep_button").attr("disabled", false);
    })
    .done(function() {
    // handle request when done
    // window.location.href="/success"
    $(".message_box > .animate_box > .loader_placeholder").removeClass('loader')
    $(".message_box > .message").text("Ran successfully");
    $(".mainStep_button").attr("disabled", false);
    });
}