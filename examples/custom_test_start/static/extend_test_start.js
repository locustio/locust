//Block of code to post the items of the form to the backend
$('#customize_start_form').submit(function(event) {
    event.preventDefault();
    $.post("./customize-load-test", $(this).serialize(),
        function(response) {
            if (response.success) {
               console.log(response)
            }
        }
    );
    return false;
});

//Block of code to post the items of the form to the backend
$('#customize_edit_form').submit(function(event) {
    event.preventDefault();
    $.post("./customize-load-test", $(this).serialize(),
        function(response) {
            if (response.success) {
               console.log(response)
            }
        }
    );
});