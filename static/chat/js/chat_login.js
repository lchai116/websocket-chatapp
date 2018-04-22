var bindEventUsernameSubmit = function(){
    $('#id-button-submit').on('click', function(event){
		var form = {
			username: $('#id-input-username').val()
		}
        if(form.username == ""){
			event.preventDefault()
            swal('username can\'t be empty')
        }
    })
}


$(document).ready(function(){
    bindEventUsernameSubmit()
})