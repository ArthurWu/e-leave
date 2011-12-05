$(function(){
	if ($('#id_department').val() == '')
		$('#id_team').attr('disabled', 'disabled');
	
	$('#id_department').change(get_temas_by_department);
	function get_temas_by_department(){
		var dep_id = $('#id_department').val();
		if(dep_id == '')
		{
			$('#id_team').attr('disabled', 'disabled');
		}
		else
		{
			var request_url = '/main/get_teams_by_department?dep_id=' + dep_id;
			$.ajax({
				url: request_url,
				dataType: 'json',
				success: function(data){
					if (data['html'] != '')
					{
						$('#id_team').html(data['html']);
						$('#id_team').removeAttr('disabled');
					}
				}
			});
		}
	}
});