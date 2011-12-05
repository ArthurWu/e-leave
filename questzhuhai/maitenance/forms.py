from django.forms import ModelForm
from maitenance.models import *

class AdminCreateForm(ModelForm):
	class Meta:
		model = Admin
		
class DepartmentForm(ModelForm):
	class Meta:
		model = Department
		
class TeamForm(ModelForm):
	class Meta:
		model = Team
		