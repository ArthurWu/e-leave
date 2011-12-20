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
							'<option value="9" selected="selected">AM</option>'+
							'<option value="13">PM</option>'+
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
	
	$('#leave-request-submit').click(function(e){
		e.preventDefault();
		if (validation())
		{
			if (!is_modify_status())
			{
				submitReuest();
			}
			else
			{
				check_if_periods_repeat_and_expired(get_periods(), handle_repeat_and_expire_result);
			}
		}
	});
	
	function validation(){
		var empty = false;
		var dates = $('.period input.vDateField');
		for(var i=0; i<dates.length; i=i+1){
			if ($(dates[i]).val() != "")
				continue;
			empty = true;
		}
		if (empty){
			$('#period_errors').text('The date can not be empty!');
			$('.errorlist').show();
			return false;
		}
		else{
			var valid = true;
			$('.period').each(function(){
				var dateString = $(this).find('#id-start-date').val();
				var start_date = new Date(dateString.replace('-','/').replace('-','/'));
				
				dateString = $(this).find('#id-end-date').val();
				var end_date = new Date(dateString.replace('-','/').replace('-','/'));
				
				if (start_date > end_date){
					$('#period_errors').text("'From date' can not be greater than 'to date'!");
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
					$('#period_errors').text("The days you ask for "+ leave_type + " is more than the max days. Please ask a Annual Leave for the beyond days.");
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
			var check_url = "/leave/expired?id=" + empId + "&periods=" + periods;
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

	function check_if_periods_repeat_and_expired(periods, success_callback){
		var empId = $('input[name="employee"]').val();
		var check_url = "/leave/checkrequest?id=" + empId + "&periods=" + periods;
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
			$('.errorlist').append('<li>Period repeat! Please check!</li>');
			$('.errorlist').show();
		}
		if (expired)
		{
			$('.errorlist').append('<li>Your Marriage Leave has expired!</li>');
			$('.errorlist').show();
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
			periods = periods+start+','+end+';';
		});
		return periods;
	}
	
	function is_modify_status(){
		if (!(typeof($('input[name="modify"]').val()) == 'undefinded' ||
			$('input[name="modify"]').val() == null))
		{
			return false;
		}
		return true;
	}
	
	function submitReuest(){
		periods = get_periods();
		$('#leaveForm').append('<input type="hidden" name="periods" value="'+periods+'" />');
		var days = $('#days').text();
		$('#leaveForm').append('<input type="hidden" name="days" value="'+days+'" />');
		$('#leaveForm').submit()
	}
	
	$('#id_leave_type').change(function(e){
		$('.help').hide();
		var selected_lt = $(this).find('option:selected').text();
		var help_text_id = String(selected_lt).toLocaleLowerCase().replace(' ', '_');
		$('#'+help_text_id+'_help').show();
		$('#leave_type_helps').show()
		DateTimeShortcuts.showDays();
	});
	
	function bindChangePeriodTime(){
		$('.timeOptions').change(function(){ DateTimeShortcuts.showDays();});
		$('#id-start-date').change(function(){ DateTimeShortcuts.showDays();});
		$('#id-end-date').change(function(){ DateTimeShortcuts.showDays();});
	}
	bindChangePeriodTime();
});