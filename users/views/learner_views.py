from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import resolve

from rolepermissions.mixins import HasPermissionsMixin
from rolepermissions.decorators import has_permission_decorator

from settings.models import Settings

from ..models import Learner
from ..forms import UserForm, GradeFilterForm
from .. import mixins
from users.tasks import read_learners_from_file


class LearnerList(HasPermissionsMixin, mixins.UserList):
    required_permission = 'admin'
    model = Learner
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        form = GradeFilterForm()
        context['form'] = form
        return context


class LearnerAdd(HasPermissionsMixin, mixins.UserAdd):
    required_permission = 'admin'
    model = Learner
    form_class = UserForm


class LearnerDetails(mixins.UserDetails):
    model = Learner

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        learner = self.get_object()
        if learner.is_transferred:
            status = f'Transferred in {learner.leave_year}'
        elif learner.is_expelled:
            status = f'Expelled in {learner.leave_year}'
        elif learner.is_alumni:
            status = f'Alumni ({learner.leave_year})'
        else:
            status = f'Learner in'

        context['status'] = status

        return context


class LearnerEdit(HasPermissionsMixin, mixins.UserEdit):
    required_permission = 'admin'
    model = Learner
    form_class = UserForm


class LearnerDelete(HasPermissionsMixin, mixins.UserDelete):
    required_permission = 'admin'
    model = Learner


@has_permission_decorator('admin')
def change_learner_status(request, slug):
    learner = get_object_or_404(Learner, slug=slug)

    current_url = resolve(request.path_info).url_name
    if current_url == 'transfer':
        action = 'Transfer'
    else:
        action = 'Expel'

    if request.method == 'POST':
        settings = Settings.objects.first()
        if current_url == 'transfer':
            learner.is_transferred = True
            learner.is_expelled = False
            if not settings.allow_transfers:
                user = learner.user
                user.delete()
                return redirect('learners:list')

        else:
            learner.is_expelled = True
            learner.is_transferred = False
            if not settings.allow_expulsion:
                user = learner.user
                user.delete()
                return redirect('learners:list')

        learner.leave_year = learner.get_active_grade().year.year
        learner.user.current_user = False
        learner.user.save()
        learner.save()
        return redirect('learners:details', learner.slug)

    context = {
        'learner': learner,
        'action': action
    }
    return render(request, 'learners/change_status.html', context)


@has_permission_decorator('admin')
def assign_grades_to_learners(request):
    form = GradeFilterForm()
    context = {'form': form}
    return render(request, 'learners/grades_to_learners.html', context)


@has_permission_decorator('admin')
def add_learners_from_file(request):
    messages.info(request, 'The reading from file is in progress. You can proceed with your work. '
                           'Once the process completed, learners will be listed in this page.')
    result = read_learners_from_file.delay()

    for message in result.collect():
        messages.info(request, message[1])

    return redirect('learners:list')
