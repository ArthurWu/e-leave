$(function(){

	$('#btn-add-team').click(function(e){
		e.preventDefault();
		var team_name = $('#team_name').val();
		var dep_id = $('.open input').attr('name');
		var addUrl = '/eleave/main/team/add?name=' + team_name + '&dep_id=' + dep_id;
		
		$.ajax({
			url: addUrl,
			dataType: 'json',
			success: function(data){
				if (data['error'].length != 0)
				{
					$('#team-error').html('<img src="/static/images/error_big.gif" width="16" height="16" alt=""/>'+data['error']);
					$('#team-error').slideDown('slow');
				}
				else
				{
					$('#vtabs-content-' + dep_id).append(data['html']);
					$('#team-error').slideUp('slow');
					
					$('#btn-delete-team-' + data['data']).click(deleteTeam);
					$('#team_name').val('');
				}
			}
		});
	});
	
	$("input[id^=btn-delete-team]").click(deleteTeam);
	
	function deleteTeam(e){
		e.preventDefault();
		var deleteBtn = $(this);
		var dep_id = deleteBtn.attr('name');
		var deleteUrl = '/eleave/main/team/delete?id=' + dep_id;
		
		$.ajax({
			url: deleteUrl,
			dataType: 'json',
			success: function(data){
				if (data['error'].length != 0)
				{
					$('#team-error').html('<img src="/static/images/error_big.gif" width="16" height="16" alt=""/>'+data['error']);
					$('#team-error').slideDown('slow');
				}
				else
				{
					deleteBtn.parent().remove()
					$('#team-error').slideUp('slow');
				}
			}
		});
	}
});