$(document).ready(function(){
	var periodCount = 1;
	$('#id_status').attr('readonly','readonly');
	
	$('#link-add-period').click(function(e){
		e.preventDefault();
		var period_temp='<div class="period">'+
						'From:<input id="id-start-date" class="vDateField notdatewidget" type="text" size="11" name="start_date'+periodCount+'" />\n'+
						'<select id="id_start_time" class="timeOptions" name="start_time'+periodCount+'">'+
							'<option value="9" selected="selected">AM</option>'+
							'<option value="13">PM</option>'+
						'</select>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\n'+
						'To:<input id="id-end-date" class="vDateField notdatewidget" type="text" size="11" name="end_date'+periodCount+'" />\n'+
						'<select id="id_end_time" class="timeOptions" name="end_time'+periodCount+'">'+
							'<option value="9">AM</option>'+
							'<option value="13" selected="selected">PM</option>'+
						'</select>\n'+
						'<input class="btn-delete-period" type="image" src="/static/admin/img/admin/icon_deletelink.gif" alt="" />'+
						'</div>';
		$(this).parent().before(period_temp);
		periodCount = periodCount + 1;
		bindDeletePeriod();
		bindChangePeriodTime();
		DateTimeShortcuts.init();
	});
	
	function bindDeletePeriod(){
		$('.btn-delete-period').click(function(e){
			e.preventDefault();
			$(this).parent().remove();
			DateTimeShortcuts.showDays();
		});
	}
	bindDeletePeriod();
	
	function show_waiting_icon(){
		$('#leave-request-submit').css('cursor', 'default').attr('disabled', 'disabled');
		$('.waiting_icon').show();
	}
	function hide_waiting_icon(){
		$('#leave-request-submit').css('cursor', 'pointer').attr('disabled', '');
		$('.waiting_icon').hide();
	}
	
	$('#leave-request-submit').click(function(e){
		e.preventDefault();
		
		show_waiting_icon();
		if (validation())
		{
			if (is_modify_status())
			{
				$('#id_leave_type').removeAttr('disabled');
				submitReuest();
			}
			else
			{
				check_if_periods_repeated_and_expired(get_periods(), handle_repeat_and_expire_result);
			}
		}
		else
		{
			hide_waiting_icon();
		}
		
	});
	
	function convert_AM_PM_Hour(s){
		if (s == 'AM') return ' 9:00'
		else return ' 13:00'
	}
	
	function validation(){
		var empty = false;
		
		var leave_type = $('#id_leave_type option:selected').val();
		if (leave_type == '')
		{
			$('#leave_type_error').text('You must select a Leave Type to submit!').show();
			empty = true;
		}
		
		var dates = $('.period input.vDateField');
		if (dates.length > 0)
		{
			for(var i=0; i<dates.length; i=i+1){
				if ($(dates[i]).val() != "")
					continue;
				empty = true;
			}
		}
		else
		{
			empty = true;
		}
		
		if (empty){
			$('#period_errors').text('You must select a period to submit!');
			$('.errorlist').show();
			return false;
		}
		else{
			var valid = true;
			$('.period').each(function(){
				var dateString = $(this).find('#id-start-date').val();
				var start_time_str = ' ' + $(this).find('#id_start_time').val() + ':00';
				var start_date = new Date(dateString.replace('-','/').replace('-','/')+start_time_str);
				
				var e_dateString = $(this).find('#id-end-date').val();
				var end_time_str = ' ' + $(this).find('#id_end_time').val() + ':00'
				var end_date = new Date(e_dateString.replace('-','/').replace('-','/')+end_time_str);
				
				if (start_date > end_date){
					$('#period_errors').text("'From date' cannot be greater than 'to date'!");
					$('.errorlist').show();
					valid = false;
				}
			});
			
			var leave_type = $('#id_leave_type option:selected').text();
			var available_days_id = leave_type.toLowerCase().replace(' ', '_');
            var available_days = new Number($('#'+available_days_id+'_available_days').text());

			if (is_modify_status())
			{
				var need_approval_days = new Number($('#'+available_days_id+'_need_approval').text());
				available_days += need_approval_days;
			}
			if (leave_type != 'Annual Leave'){
				total_days = DateTimeShortcuts.getTotalDays();
				if (total_days > available_days){
					$('#period_errors').text("The days you selected for "+ leave_type + " have exceeded your available days, please use annual leave for exceeded days.");
					$('.errorlist').show();
					valid = false;
				}
			}
			
			if (valid)
				$('.errorlist').empty().hide();
			return valid;
		}
	}
	
	function check_if_marriage_leave_expired(periods, success_callback){
		var leave_type = $('#id_leave_type option:selected').text();
		if (leave_type == 'Marriage Leave')
		{
			var empId = $('input[name="employee"]').val();
			var check_url = "/eleave/leave/expired?id=" + empId + "&periods=" + periods;
			$.ajax({
				url: check_url,
				dataType: 'json',
				async: false,
				success: success_callback
			});
		}
	}	
	
	function handle_expired_result(data){
		var expired = data['expired'];
		if (expired)
		{
			$('#period_errors').text('Your Marriage Leave has expired!');
			$('.errorlist').show();
		}
	}

	function check_if_periods_repeated_and_expired(periods, success_callback){
		var empId = $('input[name="employee"]').val();
		var leave_type_id = $('#id_leave_type option:selected').val();
		var check_url = "/eleave/leave/checkrequest?id=" + empId + "&periods=" + periods + "&leave_type_id=" + leave_type_id;
		$.ajax({
			url: check_url,
			dataType: 'json',
			success: success_callback
		});
	}
	
	function handle_repeat_and_expire_result(data){
		var repeated = data['repeated'];
		var expired = data['expired'];
		if (repeated)
		{
			$('.errorlist').append('<li>'+data['message']+'</li>');
			$('.errorlist').show();
			hide_waiting_icon();
		}
		if (expired)
		{
			$('.errorlist').append('<li>Your Marriage Leave has expired!</li>');
			$('.errorlist').show();
			hide_waiting_icon();
		}
		if (!expired && !repeated)
		{
			$('.errorlist').empty().hide();
			submitReuest();
		}
	}
	
	function get_periods(){
		var periods = ''
		$('.period').each(function(){
			var start = $(this).find('#id-start-date').val()+'-'+$(this).find('#id_start_time').val();
			var end = $(this).find('#id-end-date').val()+'-'+$(this).find('#id_end_time').val();
			periods = periods+start+','+end+'b';
		});
		return periods;
	}
	
	function submitReuest(){
		periods = get_periods();
		$('#leaveForm').append('<input type="hidden" name="periods" value="'+periods+'" />');
		var days = $('#days').text();
		$('#leaveForm').append('<input type="hidden" name="days" value="'+days+'" />');
		$('#leaveForm').submit()
	}
	
	$('#id_leave_type').bind('change', function(e){
		$('.leave_type_help').hide();
		var sel_opt = $(this).find('option:selected');
		if (sel_opt.val() == '')
			$('#leave_type_error').show();
		else
			$('#leave_type_error').hide();
			
		var selected_lt = sel_opt.text();
		var help_text_id = String(selected_lt).toLocaleLowerCase().replace(' ', '_');
		$('#'+help_text_id+'_help').show();
		$('#leave_type_helps').show()
		DateTimeShortcuts.showDays();
	});
	$('#id_leave_type').trigger('change');
	
	function bindChangePeriodTime(){
		$('.timeOptions').change(function(){ DateTimeShortcuts.showDays();});
		$('#id-start-date').change(function(){ DateTimeShortcuts.showDays();});
		$('#id-end-date').change(function(){ DateTimeShortcuts.showDays();});
	}
	bindChangePeriodTime();
});