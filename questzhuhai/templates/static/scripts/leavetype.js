$(function(){

	$('#btn-add-leavetype').click(function(e){
		e.preventDefault();
		var leave_name = $('#leavetype_name').val();
		var addUrl = '/main/leavetype/add?name=' + leave_name;
		
		$.ajax({
			url: addUrl,
			dataType: 'json',
			success: function(data){
				if (data['error'].length != 0)
				{
					$('#leavetype-error').html('<img src="/static/images/error_big.gif" width="16" height="16" alt=""/>'+data['error']);
					$('#leavetype-error').slideDown('slow');
				}
				else
				{
					$('#leave-types').append(data['html']);
					$('#leavetype-error').slideUp('slow');
					
					$('#btn-delete-leavetype-' + data['data']).click(deleteLeavetype);
					$('#notify-admin input[id='+data['data']+']').change(setNotityAdmin);
					$('#leavetype_name').val('');
				}
			}
		});
	});
	
	$("input[id^=btn-delete-leavetype]").click(deleteLeavetype);
	
	function deleteLeavetype(e){
		e.preventDefault();
		var deleteBtn = $(this);
		var leavetype_id = deleteBtn.attr('name');
		var deleteUrl = '/main/leavetype/delete?id=' + leavetype_id;
		
		$.ajax({
			url: deleteUrl,
			dataType: 'json',
			success: function(data){
				if (data['error'].length != 0)
				{
					$('#leavetype-error').html('<img src="/static/images/error_big.gif" width="16" height="16" alt=""/>'+data['error']);
					$('#leavetype-error').slideDown('slow');
				}
				else
				{
					deleteBtn.parent().parent().remove()
					$('#leavetype-error').slideUp('slow');
				}
			}
		});
	}
	
	$('#notify-admin input[type=checkbox]').change(setNotityAdmin);
	
	function setNotityAdmin(){
		var leavetype_id = $(this).attr('id');
		var notity_admin = $(this).attr('checked');
		
		var requestUrl = '/main/leavetype/set_notify_admin?id=' + leavetype_id + '&notify_admin=' + notity_admin;
		$.ajax({
			url: requestUrl,
			dataType: 'json',
			success: function(data){
				if (data['error'].length != 0)
				{
					$('#leavetype-error').html('<img src="/static/images/error_big.gif" width="16" height="16" alt=""/>'+data['error']);
					$('#leavetype-error').slideDown('slow');
				}
			}
		});
	}
});