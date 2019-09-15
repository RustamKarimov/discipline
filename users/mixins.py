from django.views import generic
from django.db import transaction
from django.shortcuts import redirect
from django.contrib import messages

from rolepermissions.roles import assign_role
from rolepermissions.checkers import has_object_permission

from . import utils


class UserList(generic.ListView):
    model = None
    template_name = None

    def __init__(self):
        super().__init__()
        directory = utils.get_model_name_as_plural_string(self.model)
        self.template_name = f'{directory}/list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context['active'] = utils.get_model_name_as_plural_string(self.model)
        return context


class UserAdd(generic.CreateView):
    model = None
    template_name = None

    def __init__(self):
        super().__init__()
        directory = utils.get_model_name_as_plural_string(self.model)
        self.template_name = f'{directory}/form.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context['active'] = utils.get_model_name_as_plural_string(self.model)
        context['action'] = f"Add New {self.model.__name__}"
        return context

    def form_valid(self, form):
        with transaction.atomic():
            user_model_name = utils.get_model_name_as_plural_string(self.model)
            password = form.cleaned_data['user_id']
            user = form.save(commit=False)
            user.is_learner = user_model_name == 'learners'
            user.is_teacher = user_model_name == 'teachers'
            user.set_password(password)
            user.save()

            role = f"{self.model.__name__.lower()}_role"

            assign_role(user, role)

            new_user = self.model.objects.create(
                user=user
            )

            return redirect(f'{user_model_name}:details', new_user.slug)


class UserDetails(generic.DetailView):
    model = None
    template_name = None

    def __init__(self):
        super().__init__()
        directory = utils.get_model_name_as_plural_string(self.model)
        self.template_name = f'{directory}/details.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context['active'] = utils.get_model_name_as_plural_string(self.model)
        return context

    def get(self, request, *args, **kwargs):
        user_object = self.get_object()
        permission = f'view_{self.model.__name__.lower()}'
        if has_object_permission(permission, request.user, user_object):
            return super().get(request, *args, **kwargs)
        else:
            messages.warning(request, "You don't have permission to perform this action. "
                             "Please login as another user.")
            return redirect('login')


class UserEdit(generic.UpdateView):
    model = None
    template_name = None

    def __init__(self):
        super().__init__()
        self.directory = utils.get_model_name_as_plural_string(self.model)
        self.template_name = f'{self.directory}/form.html'

    def get_context_data(self, **kwargs):
        user_object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['active'] = self.directory
        context['action'] = f'Edit {user_object}'
        return context

    def get_object(self, queryset=None):
        user_object = super().get_object(queryset)
        return user_object.user

    def form_valid(self, form):
        with transaction.atomic():
            user = form.save()
            if user.is_learner:
                user_object = user.learner
            else:
                user_object = user.teacher
            user_object.save()
            return redirect(f'{self.directory}:details', user_object.slug)


class UserDelete(generic.DeleteView):
    model = None
    template_name = None

    def __init__(self):
        super().__init__()
        self.directory = utils.get_model_name_as_plural_string(self.model)
        self.template_name = f'{self.directory}/delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = utils.get_model_name_as_plural_string(self.model)
        return context

    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            user_object = self.get_object()
            user = user_object.user
            user_object.delete()
            user.delete()
            return redirect(f'{self.directory}:list')