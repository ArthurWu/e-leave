from maitenance.models import Employee

def employee(request):
	emp = None
	if hasattr(request, 'employee'):
		emp = request.employee
	else:
		remote_user = request.META['REMOTE_USER']
		emps = Employee.objects.filter(domain_id=remote_user)
		if emps: emp = emps[0]
	return {'employee': emp}