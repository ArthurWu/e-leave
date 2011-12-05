$(function(){

	$('#btn-add-admin').click(function(e){
		e.preventDefault();
		var admin_id = $('#admin_id').val();
		var addUrl = '/main/admin/add?name=' + admin_id;
		
		$.ajax({
			url: addUrl,
			dataType: 'json',
			success: function(data){
				if (data['error'].length != 0)
				{
					$('#admin-error').html('<img src="/static/images/error_big.gif" width="16" height="16" alt=""/>'+data['error']);
					$('#admin-error').slideDown('slow');
				}
				else
				{
					$('#super-user').append(data['html']);
					$('#admin-error').slideUp('slow');
					
					$('#btn-delete-admin-' + data['data']).click(deleteAdmin);
					$('#admin_id').val('');
				}
			}
		});
	});
	
	$("input[id^=btn-delete-admin]").click(deleteAdmin);
	
	function deleteAdmin(e){
		e.preventDefault();
		var deleteBtn = $(this);
		var admin_id = deleteBtn.attr('name');
		var deleteUrl = '/main/admin/delete?name=' + admin_id;
		
		$.ajax({
			url: deleteUrl,
			dataType: 'json',
			success: function(data){
				if (data['error'].length != 0)
				{
					$('#admin-error').html('<img src="/static/images/error_big.gif" width="16" height="16" alt=""/>'+data['error']);
					$('#admin-error').slideDown('slow');
				}
				else
				{
					deleteBtn.parent().parent().remove()
					$('#admin-error').slideUp('slow');
				}
			}
		});
	}
});