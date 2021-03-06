from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, redirect_to_login
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from hr.models import *
from projectlead.models import *
from employee.models import User
from projectlead.models import Team
from django.db.models import Q
from django.http import HttpResponse
from django.db.models import Case, When
from employee.views import SignUpView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from hrms.decorators import user_is_superuser

# Create your views here.


# HR index
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_superuser, name='dispatch')
class HrDashboard(TemplateView): 
    def get_context_data(self, **kwargs):
        context = super(HrDashboard, self).get_context_data(**kwargs)
        context['project_count'] = Project.objects.count()
        context['task_count'] = Tasks.objects.count()
        context['employee_count'] = User.objects.count()
        return context 
    template_name = 'hr/hr_dashboard.html'
    

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_superuser, name='dispatch')
class ProjectCreate(CreateView):
    model = Project
    fields = '__all__'
    success_url = reverse_lazy('projects')
    template_name = 'hr/projects.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_superuser:
            context['project'] = Project.objects.all()
        else:       
            context['project'] = Team.objects.filter(employee=self.request.user)
            
        context['team'] = Team.objects.all()
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class ProjectDetailView(DetailView):
    model = Project
    fields = '__all__'
    template_name='hr/project-view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employees = User.objects.filter(is_superuser=False)
        context['leader'] = User.objects.filter(is_superuser=False)
        context['assigned'] = Team.objects.filter(project=self.kwargs.get('pk'))
        context['tasks'] = Tasks.objects.filter(project=self.kwargs.get('pk'))

        employee_list = []
        leader_list = []

        for employee in employees:
            if employee.is_staff==True:
                leader_list.append(employee)
            else:
                employee_list.append(employee)
                
        context['employees'] = employee_list
        context['leaders'] = leader_list
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_superuser, name='dispatch')
class ProjectUpdate(UpdateView):
    model = Project
    fields = '__all__'
    template_name = 'hr/project-view.html'
    success_url = reverse_lazy('projects')


@login_required
@user_is_superuser
def project_delete(request, pk):
    project = Project.objects.get(id=pk)
    project.delete()
    return redirect('projects')


@login_required
@staff_member_required
def assign_employee(request, pk, id):
    employee = User.objects.get(id=pk)
    project = Project.objects.get(id=id)

    if  Team.objects.filter(employee=employee, project=project):
        obj = Team.objects.get(employee=employee, project=project)
        obj.delete()
        return JsonResponse('not selected', safe=False)
    else:
        Team.objects.create(employee=employee, project=project)
        return JsonResponse('selected', safe=False)


@login_required
@user_is_superuser
def task_board(request, pk):
    project = Project.objects.get(id=pk)
    project_task = Tasks.objects.filter(project=pk).order_by(Case(When(status='pending', then='status')),Case(When(status='progress', then='status')),Case(When(status='completed', then='status')))

    team = Team.objects.filter(project=pk)
    employees = User.objects.filter(is_superuser=False)
    taskassigned = TaskAssigned.objects.all()

    employee_list = []
    leader_list = []
    status_list = ['pending', 'progress', 'completed']
    for employee in employees:
        if employee.is_staff==True:
            leader_list.append(employee)
        else:
            employee_list.append(employee)

    context = {
        'project_task': project_task, 'team':team, 'employees':employee_list, 'leaders':leader_list,
        'object': pk, 'taskassigned': taskassigned, 'project': project, 'status': status_list}
    return render(request, 'hr/task-board.html', context)


@login_required
def add_new_task(request, pk):
    project = Project.objects.get(id=pk)
    if request.method == 'POST':
        task = request.POST['task']
        priority = request.POST['priority']
        due_date = request.POST['due_date']
        Tasks.objects.create(task=task, task_priority=priority, due_date=due_date, project=project)
        return redirect('task-board', pk=pk)
    else:
        return redirect('task-board')


@login_required
def task_delete(request, pk, id):
   task = Tasks.objects.get(id=pk)
   task.delete()
   return redirect('task-board', pk=id)


@login_required
def edit_task(request, pk, id):
    task = Tasks.objects.get(id=pk)
    if request.method == 'POST':
        task.task = request.POST['task']
        task.task_priority = request.POST['priority']
        task.due_date = request.POST['due_date']
        task.save()
        return redirect('task-board', pk=id)
    else:
        return redirect('task-board', pk=id)


@login_required
def change_task_status(request, pk, st):
    task = Tasks.objects.get(id=pk)
    task.status = st
    task.save()
    return JsonResponse('true', safe=False)


@login_required
@user_is_superuser
def all_employees(request):
    all_employees = User.objects.filter(is_superuser=False)
    context = {
        'employees': all_employees
    }
    return render(request, 'hr/employees.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_superuser, name='dispatch')
class EmployeeCreate(SignUpView):
    template_name = 'hr/employees.html'


@login_required
@user_is_superuser
def employee_profile(request, pk):
    employee = User.objects.get(id=pk)
    context = {
        'employee': employee
    }
    return render(request, 'hr/employee-profile.html', context)