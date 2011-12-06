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
		submitReuest();
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
			var modify = $('input[name="modify"]');
			if (modify != [])
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
				$('.errorlist').hide();
			return valid;
		}
	}

	function submitReuest(){
		var periods = ''
		$('.period').each(function(){
			var start = $(this).find('#id-start-date').val()+'-'+$(this).find('#id_start_time').val();
			var end = $(this).find('#id-end-date').val()+'-'+$(this).find('#id_end_time').val();
			periods = periods+start+','+end+';';
		});
		$('#leaveForm').append('<input type="hidden" name="periods" value="'+periods+'" />');
		var days = $('#days').text();
		$('#leaveForm').append('<input type="hidden" name="days" value="'+days+'" />');
		
		if ($('input[name="modify"]') != []){
			$('.errorlist').hide();
			if (validation()){
				$('#leaveForm').submit();
			}
		}
		else{
			var check_url = "/leave/checkrequest?periods=" + periods;
			$.ajax({
				url: check_url,
				dataType: 'json',
				success: function(data){
					if (data['data'])
					{
						$('#period_errors').text('Period repeat! Please check!');
						$('.errorlist').show();
					}
					else
					{
						$('.errorlist').hide();
						if (validation()){
							$('#leaveForm').submit();
						}
					}
				}
			});
		}
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