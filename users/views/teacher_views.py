from django.views import generic
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy

from rolepermissions.roles import assign_role
from rolepermissions.mixins import HasPermissionsMixin

from school_discipline.roles import TeacherRole

from ..models import Teacher
from ..forms import UserForm


class TeacherList(HasPermissionsMixin, generic.ListView):
    required_permission = 'admin'
    model = Teacher
    template_name = 'teachers/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'teachers'
        return context


class TeacherAdd(HasPermissionsMixin, generic.CreateView):
    required_permission = 'admin'
    model = Teacher
    form_class = UserForm
    template_name = 'teachers/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'teachers'
        context['action'] = 'Add New Teacher'
        return context

    def form_valid(self, form):
        with transaction.atomic():
            password = form.cleaned_data['user_id']
            user = form.save(commit=False)
            user.is_teacher = True
            user.set_password(password)
            user.save()

            assign_role(user, TeacherRole)

            teacher = Teacher.objects.create(
                user=user
            )

            return redirect('teachers:details', teacher.slug)


class TeacherDetails(generic.DetailView):
    model = Teacher
    template_name = 'teachers/details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'teachers'
        return context


class TeacherEdit(HasPermissionsMixin, generic.UpdateView):
    required_permission = 'admin'
    model = Teacher
    form_class = UserForm
    template_name = 'teachers/form.html'

    def get_context_data(self, **kwargs):
        teacher = self.get_object()
        context = super().get_context_data(**kwargs)
        context['active'] = 'teachers'
        context['action'] = f'Edit {teacher}'
        return context

    def get_object(self, queryset=None):
        teacher = super().get_object(queryset)
        return teacher.user

    def form_valid(self, form):
        with transaction.atomic():
            user = form.save()
            teacher = user.teacher
            teacher.save()
            return redirect('teachers:details', teacher.slug)


class TeacherDelete(HasPermissionsMixin, generic.DeleteView):
    required_permission = 'admin'
    model = Teacher
    template_name = 'teachers/delete.html'
    success_url = reverse_lazy('teachers:list')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['active'] = 'teachers'
        return context

    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            teacher = self.get_object()
            user = teacher.user
            teacher.delete()
            user.delete()
            return redirect('teachers:list')