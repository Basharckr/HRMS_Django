from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.views import LoginView, redirect_to_login, LogoutView
from django.urls import reverse_lazy
from .forms import SignUpFrom
from hr.models import *
from projectlead.models import *
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
# Create your views here.


#user signUp
class SignUpView(CreateView):
    form_class = SignUpFrom
    success_url = reverse_lazy('login')
    template_name = 'account/register.html'


# user login
class CustomLoginView(LoginView):
    template_name = 'account/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_superuser == True:
            return reverse_lazy('hr_dashboard')
        elif self.request.user.is_staff == True:
            return reverse_lazy('ldr_dashboard')
        elif self.request.user.is_active == True:
            return reverse_lazy('emp_dashboard')


#user logout
@method_decorator(login_required, name='dispatch')
class CustomLogoutView(LogoutView):
    next_page = 'login'


@method_decorator(login_required, name='dispatch')
class EmployeeDashboard(TemplateView):
    template_name = 'employee/emp_dashboard.html'
  

@login_required
def emp_profile(request):

    team = Team.objects.all()

    if request.user.is_superuser:
        project = Project.objects.all()
    else:       
        project = Team.objects.filter(employee=request.user)
    context = {
        'project': project, 'team': team
    }
    if request.user.is_superuser:
        return render(request, 'hr/profile.html', context)
    elif request.user.is_staff:
        return render(request, 'projectlead/profile.html', context)
    else:
        return render(request, 'account/profile.html', context)


@login_required
def profile_update(request):

    if request.method == 'POST':
        edit = User.objects.get(id=request.user.id)
        edit.firstname = request.POST['firstname']
        edit.lastname = request.POST['lastname']
        edit.username = request.POST['username']
        edit.email = request.POST['email']
        edit.designation = request.POST['designation']
        edit.number = request.POST['number']

        edit.image = request.FILES.get('picfield')

        if User.objects.filter(username=edit.username).exclude(id=request.user.id).exists():
                        messages.error(
                            request, 'This username already taken!!')
                        return redirect('profile')
        elif User.objects.filter(email=edit.email).exclude(id=request.user.id).exists():
            messages.error(request, 'The email already taken!!')
            return redirect('profile')
        elif User.objects.filter(number=edit.number).exclude(id=request.user.id).exists():
            messages.error(request, 'The phone number already taken!!')
            return redirect('profile')
        else:
            edit.save()
            messages.success(
                request, 'Profile information updated..')
            return redirect('profile')
    return redirect('profile')



@login_required
def employee_project(request):
    team = Team.objects.all()  
    context = {
        'team': team
    }
    return render(request, 'employee/employee-projects.html', context)


@login_required
def employee_project_veiw(request, pk):
    project = Project.objects.get(id=pk)
    team = Team.objects.filter(project=project)
    task = TaskAssigned.objects.filter(employee=request.user) 
    context = {
        'project': project, 'tasks': task, 'team': team
    }
    return render(request, 'employee/emp-project-view.html', context)


@login_required
def employee_task_board(request, pk):

    project_task = TaskAssigned.objects.filter(project=pk)
    team = Team.objects.filter(project=pk)

    context = {
        'project_task': project_task, 'project': pk, 'team': team
    }
    return render(request, 'employee/employee-task.html', context)


@login_required
def emp_change_task_status(request, pk, st):
    task = TaskAssigned.objects.get(id=pk)
    task.task_status = st
    task.save()
    return JsonResponse('true', safe=False)