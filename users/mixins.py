from django.views import generic
from django.db import transaction
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Count

from rolepermissions.roles import assign_role
from rolepermissions.checkers import has_object_permission

from grades.models import Grade
from discipline.models import DisciplineAction, Discipline

from . import utils
from .models import Teacher, Learner

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

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user__current_user=True).select_related('user')
        return qs


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

        context['total_merits'] = self.object.discipline_action.filter(
            action__discipline_type=Discipline.MERIT).count()
        context['total_demerits'] = self.object.discipline_action.filter(
            action__discipline_type=Discipline.DEMERIT).count()

        if context['active'] == 'teachers':
            context['form_classes'] = Grade.active_grades.filter(teachers=self.object).prefetch_related(
                'learners', 'learners__user')

            context['last_5_merits'] = DisciplineAction.objects.select_related('action').filter(
                teacher=self.object, action__discipline_type=Discipline.MERIT)[:5]
            context['last_5_demerits'] = DisciplineAction.objects.select_related('action').filter(
                teacher=self.object, action__discipline_type=Discipline.DEMERIT)[:5]

            context['top_5_merits'] = Discipline.merits.filter(discipline_action__teacher=self.object).annotate(
                merit_count=Count('code')
            ).order_by('-merit_count')[:5]
            context['top_5_demerits'] = Discipline.demerits.filter(discipline_action__teacher=self.object).annotate(
                demerit_count=Count('code')
            ).order_by('-demerit_count')[:5]

        else:
            context['grades'] = Grade.active_grades.filter(learners=self.object).prefetch_related(
                'learners', 'learners__user')

            context['last_5_merits'] = DisciplineAction.objects.select_related('action').filter(
                learner=self.object, action__discipline_type=Discipline.MERIT)[:5]
            context['last_5_demerits'] = DisciplineAction.objects.select_related('action').filter(
                learner=self.object, action__discipline_type=Discipline.DEMERIT)[:5]

            context['top_5_merits'] = Discipline.merits.filter(discipline_action__learner=self.object).annotate(
                merit_count=Count('code')
            ).order_by('-merit_count')[:5]
            context['top_5_demerits'] = Discipline.demerits.filter(discipline_action__learner=self.object).annotate(
                demerit_count=Count('code')
            ).order_by('-demerit_count')[:5]

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

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        return queryset


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