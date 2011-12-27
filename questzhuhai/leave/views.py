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

def index(request):
	pass

def check_period(request):
	periods_str = request.GET.get('periods')
	leave_type_id = request.GET.get('leave_type_id')
	emp_id = request.GET.get('id')
	periods = periods_str.rstrip("b").split('b')
	log.Except(periods_str)
	try:
		from maitenance.models import Employee
		req_emp = Employee.objects.get(id=int(emp_id))
	except:
		log.Except('Can not get Employee with id %s' % id)
	
	repeated = has_repeate_period(periods, req_emp, leave_type_id)
	expired = marriage_leave_expire(periods, req_emp)
	return HttpResponse(simplejson.dumps({'repeated': repeated, 'expired': expired}))
	
def marriage_leave_expire(periods, emp):	
	mar_confirm = None
	all_mar_confirm = emp.marriageleaveconfirm_set.all()
	if all_mar_confirm: 
		mar_confirm = all_mar_confirm[0]	
	
	expired = False
	if mar_confirm:
		expire_date = mar_confirm.expire_date
	
		for p in periods:
			start_str, end_str = p.split(',')
			start=datetime.datetime.strptime(start_str, '%Y-%m-%d-%H')
			end=datetime.datetime.strptime(end_str, '%Y-%m-%d-%H')
			if (expire_date < end) or (expire_date < datetime.datetime.today()):
				expired = True

	return expired

def has_repeate_period(periods_str, emp, leave_type_id):	
	repeated = period_repeated(periods_str)
	
	if not repeated:
		for p in periods_str:
			start, end = split_periods(p)
			s_in = Period.objects.filter(start__gte=start, end__lte=start, leave_request__employee = emp, leave_request__leave_type__id = leave_type_id)
			e_in = Period.objects.filter(start__gte=end, end__lte=end, leave_request__employee = emp, leave_request__leave_type__id = leave_type_id)
			
			if s_in or e_in:
				repeated = True
			
	return repeated

def period_repeated(periods_str):
	periods = []
	for p_str in periods_str:
		periods.append(split_periods(p_str))
	log.Except(periods)
	if len(periods) >=2:
		for p1 in periods:
			for p2 in periods:
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
	
def leave_request(request, id=None, edit=False):
	form = periods = leave_request = availableDays = None
	if request.method == 'POST':
		if edit and request.POST.has_key('leave_request_id'):
			lr = get_object_or_404(LeaveRequest, id=request.POST.get('leave_request_id'))
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
				messages.add_message(request, messages.INFO, 'You leave request has been submited successfully!')
			else:
				do = 'modified'
				if request.employee.is_mine(current_lr):
					process.get_processor(current_lr, request.employee).resubmit()
					messages.add_message(request, messages.INFO, current_lr.employee.display_name + "'s leave request has been modified and resubmited!")
					do += ' and resubmited'
				else:
					process.get_processor(current_lr, request.employee).edit()
					messages.add_message(request, messages.INFO, current_lr.employee.display_name + "'s leave request has been modified successfully!")
				LeaveRequestProcesses(leave_request=current_lr,
									  who=request.employee.display_name,
									  do=do).save()
				
			return redirect(current_lr)
	elif id and edit:
		leave_request = get_object_or_404(LeaveRequest, id=id)
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
							  
def leave_request_view(request, id):
	leave_request = get_object_or_404(LeaveRequest, id=id)
	
	if not have_can_view_permission(request.employee, leave_request):
		return render_to_response('can_not_view.html', RequestContext(request, {}))
	
	lrps = LeaveRequestProcesses.objects.filter(leave_request=leave_request).order_by('at')
	actions = process.get_processor(leave_request, request.employee).actions()

	#nav = 'my_leave_requests'
	#if request.employee.is_approver_of(leave_request):
	#	nav = 'to_do_list'
		
	context = {
		'leaverequest': leave_request,
		'actions': actions,
		'lrps': lrps,
	}
	return render_to_response('leave/leave_request.html',
							  RequestContext(request, context))
							  
def have_can_view_permission(emp, leave_request):
	if emp.is_approver_of(leave_request) \
				or emp.is_mine(leave_request) \
				or emp.is_administrative_staff:
		return True
	else:
		return False

def leave_request_by_emp(request):
	s = request.GET.get('status', 'processing')
	queryset = LeaveRequest.objects.by_employee(request.employee)
	title =  'My Leave Request'
		
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
	
	s = request.GET.get('status', 'processing')
	queryset = LeaveRequest.objects.by_approver(request.employee)
	title =  'Leave Requests Need To Approve'
	
	return leave_request_list(request, filter_leave_request(queryset, s), title, s)
	
def leave_request_by_admin(request):
	if not request.employee.is_administrative_staff:
		return render_to_response('auth_error.html', RequestContext(request, {}))
		
	queryset = LeaveRequest.objects.all().order_by('-create_date')
	title =  'All Leave Request'
	return leave_request_list(request, queryset, title)
			
def leave_request_list(request, queryset, title, s="processing"):
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
			
def leave_request_approve(request, id):
	leave_request = get_object_or_404(LeaveRequest, id=id)
	process.get_processor(leave_request, request.employee).approve()
	messages.add_message(request, messages.INFO, "%s's leave request has been approved successfully!" % leave_request.employee.display_name)
	LeaveRequestProcesses(leave_request=leave_request,
						who=request.employee.display_name,
						do='Approved').save()

	return redirect(leave_request)
	
def leave_request_reject(request, id):
	leave_request = get_object_or_404(LeaveRequest, id=id)
	reason = request.POST.get('reason', '')
	LeaveRequestProcesses(leave_request=leave_request,
						who=request.employee.display_name,
						do='Rejected',
						reason=reason).save()
		
	process.get_processor(leave_request, request.employee).reject(reason)
	messages.add_message(request, messages.INFO, "%s's leave request has been rejected successfully!" % leave_request.employee.display_name)
				
	return redirect(leave_request)
	
def leave_request_archive(request, id):
	leave_request = get_object_or_404(LeaveRequest, id=id)
	process.get_processor(leave_request, request.employee).archive()
	messages.add_message(request, messages.INFO, "%s's leave request has been archived successfully!" % leave_request.employee.display_name)
	LeaveRequestProcesses(leave_request=leave_request,
						who=request.employee.display_name,
						do='Archived').save()
	return redirect(leave_request)
	
def leave_request_cancel(request, id):
	leave_request = get_object_or_404(LeaveRequest, id=id)
	process.get_processor(leave_request, request.employee).cancel()
	messages.add_message(request, messages.INFO, "%s's leave request has been canceled successfully!" % leave_request.employee.display_name)
	LeaveRequestProcesses(leave_request=leave_request,
						who=request.employee.display_name,
						do='Canceled').save()
	return redirect(leave_request)

