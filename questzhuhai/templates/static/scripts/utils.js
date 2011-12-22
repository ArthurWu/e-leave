function is_modify_status(){
	if (typeof($('input[name="modify"]').val()) == 'undefined' ||
		$('input[name="modify"]').val() == null || 
		$('input[name="modify"]') == [])
	{
		return false;
	}
	return true;
}

