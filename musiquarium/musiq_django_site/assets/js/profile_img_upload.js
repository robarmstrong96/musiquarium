(function($) {

  $('#file-upload').submit(function(e){
    e.preventDefault();
    $form = $(this)
    var formData = new FormData(this);
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: formData,
        success: function (response) {
            $('.error').remove();
            console.log(response)
            if(response.error){
                $.each(response.errors, function(name, error){
                    error = '<small class="text-muted error">' + error + '</small>'
                    $form.find('[name=' + name + ']').after(error);
                })
            }
            else{
                alert(response.message)
                window.location = ""
            }
        },
        cache: false,
        contentType: false,
        processData: false
    });
  });

})(jQuery); // End of use strict
