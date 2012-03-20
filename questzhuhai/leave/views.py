from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages
from forms import *
import processe.BaseProcessor as process
import processe.status as Status
import datetime
from common.logger import log
import simplejson

def permission_require(view_func):
	'''
	To use this decorator, the view function must have a "id" parameter
	'''
	def is_have_permission(request, *args, **kwargs):
		emp = request.employee
		leave_request = get_object_or_404(LeaveRequest, id=kwargs['id'])
		if have_can_view_permission(emp, leave_request):
			return view_func(request, *args, **kwargs)
		return render_to_response('can_not_view.html', RequestContext(request, {}))
	return is_have_permission
							  
def have_can_view_permission(emp, leave_request):
	if emp.is_approver_of(leave_request) \
				or emp.is_mine(leave_request) \
				or emp.is_administrative_staff:
		return True
	else:
		return False

def check_period(request):
	periods_str = request.GET.get('periods')
	leave_type_id = int(request.GET.get('leave_type_id'))
	emp_id = request.GET.get('id')
	periods = periods_str.rstrip("b").split('b')
	try:
		from maitenance.models import Employee
		req_emp = Employee.objects.get(id=int(emp_id))
	except:
		log.Except('Can not get Employee with id %s' % id)
	
	repeated, message = has_repeate_period(periods, req_emp, leave_type_id)
	
	try:
		lr = LeaveType.objects.get(id=leave_type_id)
	except:
		lr = None
	
	expired = False
	if lr and lr.name == 'Marriage Leave':
		expired = marriage_leave_expire(periods, req_emp)
		
	return HttpResponse(simplejson.dumps({'repeated': repeated, 'expired': expired, 'message': message}))
	
def marriage_leave_expire(periods, emp):	
	mar_confirm = None
	all_mar_confirm = emp.marriageleaveconfirm_set.all()
	if all_mar_confirm: 
		mar_confirm = all_mar_confirm[0]	
	
	expired = False
	if mar_confirm:
		expire_date = mar_confirm.expire_date
		expire_datetime = datetime.datetime(expire_date.year, expire_date.month, expire_date.day, 17, 30)
		for p in periods:
			start, end = split_periods(p)
			if expire_datetime < end: # or (expire_date < datetime.datetime.today()):
				expired = True

	return expired

def has_repeate_period(periods_str, emp, leave_type_id):	
	from django.db.models import Q
	repeated = period_repeated(periods_str)
	message = ''
	if repeated:
		message = 'The periods you selected are overlapped. Please remove the overlapped period.'
	else:
		checked_status = [status.PENDINGMANAGER, status.WAITINGADMINCONFIRM, status.PENDINGADMIN, status.PENDINGEMPLOYEE, status.ARCHIVED] 
		for p in periods_str:
			start, end = split_periods(p)
			has_existed = Period.objects.filter(
				(
					Q(start__range=(start, end))|
					Q(end__range=(start, end))|
					(Q(start__gte=start)&Q(end__lte=end))|
					(Q(start__lte=start)&Q(end__gte=end))
				)&
				Q(leave_request__employee=emp)&Q(leave_request__status__in=checked_status)
			)
			if has_existed:
				repeated = True
				message = 'The period(%s to %s) has been already existed in other leave request, please check.' % (start.strftime('%Y-%m-%d %p'), end.strftime('%Y-%m-%d %p'))
			
	return repeated, message

def period_repeated(periods_str):
	periods = []
	for p_str in periods_str:
		periods.append(split_periods(p_str))
	
	if len(periods) >=2:
		for p1 in periods:
			index = periods.index(p1)
			for p2 in periods[index+1:]:
				s = max(p1[0], p2[0])
				e = min(p1[1], p2[1])
				if e >= s:
					return True
	return False
				
				
def split_periods(dates_string):
	start_str, end_str = dates_string.split(',')
	start=datetime.datetime.strptime(start_str, '%Y-%m-%d-%H')
	end=datetime.datetime.strptime(end_str, '%Y-%m-%d-%H')
	return start, end

def can_edit_leave_request(request, leave_req):
	emp = request.employee
	result = True
	if leave_req.status == Status.PENDINGADMIN:
		if not emp.is_admin and not emp.is_approver_of(leave_req):
			result = False
			
	if leave_req.status in (Status.ARCHIVED,Status.CANCELED):
		result = False
	if not result: set_warning_msg(request, leave_req)
	return result
			
def leave_request(request, id=None, edit=False):
	form = periods = leave_request = availableDays = None
	if request.method == 'POST':
		if edit and request.POST.has_key('leave_request_id'):
			lr = get_object_or_404(LeaveRequest, id=request.POST.get('leave_request_id'))
			if not can_edit_leave_request(request, lr): return redirect(lr)
			form = CreateLeaveRequestForm(request.POST, instance=lr)
		else:
			form = CreateLeaveRequestForm(request.POST)			
		
		if form.is_valid():
			current_lr = form.save()
			if current_lr:
				Period.objects.filter(leave_request=current_lr).delete()
				
				periods_str = request.POST.get('periods')
				periods = periods_str.rstrip("b").split('b')
				for p in periods:
					start, end = p.split(',')
					
					Period(leave_request=current_lr,
						   start=datetime.datetime.strptime(start, '%Y-%m-%d-%H'),
						   end=datetime.datetime.strptime(end, '%Y-%m-%d-%H')
						).save()
				
			if not request.POST.has_key('modify'):
				process.get_processor(current_lr, request.employee).submit()
				messages.add_message(request, messages.INFO, 'You leave request has been submitted successfully!')
			else:
				do = 'modified'
				if request.employee.is_mine(current_lr):
					success_resubmit = process.get_processor(current_lr, request.employee).resubmit()
					if success_resubmit:
						messages.add_message(request, messages.INFO, current_lr.employee.display_name + "'s leave request has been modified and resubmitted!")
						do += ' and resubmited'
						LeaveRequestProcesses(leave_request=current_lr,
									  who=request.employee.display_name,
									  do=do).save()
					else:
						set_warning_msg(request, current_lr)
				else:
					success_edit = process.get_processor(current_lr, request.employee).edit()
					if success_edit:
						messages.add_message(request, messages.INFO, current_lr.employee.display_name + "'s leave request has been modified successfully!")
						LeaveRequestProcesses(leave_request=current_lr,
									  who=request.employee.display_name,
									  do=do).save()
					else: set_warning_msg(request, current_lr)
				
			return redirect(current_lr)
	elif id and edit:
		leave_request = get_object_or_404(LeaveRequest, id=id)
		
		if not have_can_view_permission(request.employee, leave_request):
			return render_to_response('can_not_view.html', RequestContext(request, {}))
		
		if not can_edit_leave_request(request, leave_request): return redirect(leave_request)
		
		form = CreateLeaveRequestForm(instance=leave_request)
		periods = Period.objects.filter(leave_request__id=leave_request.id)
		availableDays = leave_request.employee.days_available()
		for k, v in availableDays.items():
			if k == leave_request.leave_type.name.lower().replace(' ', '_'):
				v['available_days'] = v['total_days'] - v['used_days']
				if v['available_days'] < 0: v['available_days'] = 0
	else:
		form = CreateLeaveRequestForm()
		availableDays = request.employee.days_available()
	
	context = {
		'form': form,
		'leaverequest': leave_request,
		'periods': periods,
		'edit': edit,
		'availableDays': availableDays,
		'nav': 'new_leave_request'
	}
	return render_to_response('leave/new_leave_request.html',
							  RequestContext(request, context))

@permission_require
def leave_request_view(request, id):
	leave_request = get_object_or_404(LeaveRequest, id=id)
	
	lrps = LeaveRequestProcesses.objects.filter(leave_request=leave_request).order_by('at')
	actions = process.get_processor(leave_request, request.employee).actions()
		
	context = {
		'leaverequest': leave_request,
		'actions': actions,
		'lrps': lrps,
	}
	return render_to_response('leave/leave_request.html',
							  RequestContext(request, context))


def leave_request_by_emp(request):
	s = request.GET.get('status', 'all')
	queryset = LeaveRequest.objects.by_employee(request.employee)
	title =  'My Leave Requests'
		
	return leave_request_list(request, filter_leave_request(queryset, s), title, s)
	
def filter_leave_request(queryset, s):
	if s:
		if s == 'processing':
			queryset = queryset.filter(status__in=[Status.PENDINGMANAGER, Status.WAITINGADMINCONFIRM, status.PENDINGEMPLOYEE])
		elif s == 'finished':
			queryset = queryset.filter(status__in=[Status.PENDINGADMIN, Status.ARCHIVED])
		elif s == 'canceled':
			queryset = queryset.filter(status__in=[Status.CANCELED])
		else: pass
	return queryset
	
def leave_request_by_approver(request):
	if not request.employee.is_approver():
		return render_to_response('auth_error.html', RequestContext(request, {}))
	
	s = request.GET.get('status', 'all')
	queryset = LeaveRequest.objects.by_approver(request.employee)
	title =  'Leave Requests Need To Approve'
	
	return leave_request_list(request, filter_leave_request(queryset, s), title, s)
	
def leave_request_by_admin(request):
	if not request.employee.is_administrative_staff:
		return render_to_response('auth_error.html', RequestContext(request, {}))
		
	queryset = LeaveRequest.objects.all().order_by('-create_date')
	title =  'All Leave Request'
	return leave_request_list(request, queryset, title)
			
def leave_request_list(request, queryset, title, s="all"):
	lr_list = list(queryset)
	paginator = Paginator(lr_list, 20)
	
	# Make sure page request is an int. If not, deliver first page.
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1
		
	# If page request (9999) is out of range, deliver last page of results.
	try:
		lrs = paginator.page(page)
	except (EmptyPage, InvalidPage):
		lrs = paginator.page(paginator.num_pages)
		
	nav = 'my_leave_requests'
	if title == 'Leave Requests Need To Approve':
		nav = 'to_do_list'
		
	return render_to_response('leave/leave_request_list.html',
				RequestContext(request, {
					'leaverequest_list': lrs,
					'title': title,
					'nav': nav,
					'status': s
					})
			)

@permission_require
def leave_request_approve(request, id):
	leave_request = get_object_or_404(LeaveRequest, id=id)
	success = process.get_processor(leave_request, request.employee).approve()
	if success:
		LeaveRequestProcesses(leave_request=leave_request,
						who=request.employee.display_name,
						do='Approved').save()

	shortcut = int(request.GET.get('shortcut', '0'))
	if not shortcut:
		if success:
			messages.add_message(request, messages.SUCCESS, "%s's leave request has been approved successfully!" % leave_request.employee.display_name)
		else:
			set_warning_msg(request, leave_request)
		return redirect(leave_request)
	else:
		return HttpResponse(leave_request.status)

@permission_require
def leave_request_reject(request, id):
	leave_request = get_object_or_404(LeaveRequest, id=id)
	reason = request.POST.get('reason', '')
	success = process.get_processor(leave_request, request.employee).reject(reason)
	if success:
		LeaveRequestProcesses(leave_request=leave_request,
						who=request.employee.display_name,
						do='Rejected',
						reason=reason).save()
		
	
		messages.add_message(request, messages.INFO, "%s's leave request has been rejected successfully!" % leave_request.employee.display_name)
	else:
		set_warning_msg(request, leave_request)
	
	return redirect(leave_request)

@permission_require
def leave_request_archive(request, id):
	leave_request = get_object_or_404(LeaveRequest, id=id)
	success = process.get_processor(leave_request, request.employee).archive()
	if not success:
		set_warning_msg(request, leave_request)
	else:
		messages.add_message(request, messages.INFO, "%s's leave request has been archived successfully!" % leave_request.employee.display_name)
		LeaveRequestProcesses(leave_request=leave_request,
						who=request.employee.display_name,
						do='Archived').save()
	return redirect(leave_request)

@permission_require
def leave_request_cancel(request, id):
	leave_request = get_object_or_404(LeaveRequest, id=id)
	success = process.get_processor(leave_request, request.employee).cancel()
	if not success:
		set_warning_msg(request, leave_request)
	else:
		messages.add_message(request, messages.INFO, "%s's leave request has been canceled successfully!" % leave_request.employee.display_name)
		LeaveRequestProcesses(leave_request=leave_request,
						who=request.employee.display_name,
						do='Canceled').save()
	return redirect(leave_request)
	
def set_warning_msg(request, leave_request):
	messages.add_message(request, messages.WARNING, "%s's leave request has been deal with before, please refresh page to see the result." % leave_request.employee.display_name)
