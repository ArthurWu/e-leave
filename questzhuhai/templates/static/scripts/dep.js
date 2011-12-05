$(function(){

	$('#btn-add-dep').click(function(e){
		e.preventDefault();
		var dep_name = $('#dep_name').val();
		var addUrl = '/main/dep/add?name=' + dep_name;
		
		$.ajax({
			url: addUrl,
			dataType: 'json',
			success: function(data){
				if (data['error'].length != 0)
				{
					$('#dep-error').html('<img src="/static/images/error_big.gif" width="16" height="16" alt=""/>'+data['error']);
					$('#dep-error').slideDown('slow');
				}
				else
				{
					$('#deps').append(data['html']);
					$('#teams_list').append('<div id="vtabs-content-'+data['data']+'"></div>');
					$('#dep-error').slideUp('slow');
					
					$('#btn-delete-dep-' + data['data']).click(deleteDep);
					$('#dep_name').val('');
					$("#vtabs1").jVertTabs();
				}
			}
		});
	});
	
	if ( $("#deps").has('li').length > 0){	$("#vtabs1").jVertTabs({selected:0}); }
	
	$("input[id^=btn-delete-dep]").click(deleteDep);
	
	function deleteDep(e){
		e.preventDefault();
		var deleteBtn = $(this);
		var dep_id = deleteBtn.attr('name');
		var deleteUrl = '/main/dep/delete?id=' + dep_id;
		
		$.ajax({
			url: deleteUrl,
			dataType: 'json',
			success: function(data){
				if (data['error'].length != 0)
				{
					$('#dep-error').html('<img src="/static/images/error_big.gif" width="16" height="16" alt=""/>'+data['error']);
					$('#dep-error').slideDown('slow');
				}
				else
				{
					deleteBtn.parent().remove();
					$('#vtabs-content-' + dep_id).remove();
					$('#dep-error').slideUp('slow');
					$("#vtabs1").jVertTabs({selected: 0});
				}
			}
		});
	}
});