from django.contrib import messages
from django.shortcuts import redirect, render

from rolepermissions.mixins import HasPermissionsMixin
from rolepermissions.decorators import has_permission_decorator

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


class LearnerEdit(HasPermissionsMixin, mixins.UserEdit):
    required_permission = 'admin'
    model = Learner
    form_class = UserForm


class LearnerDelete(HasPermissionsMixin, mixins.UserDelete):
    required_permission = 'admin'
    model = Learner

# todo: Change status of learner (will be performed on grade level)


# todo: Assign Learners to grade
@has_permission_decorator('admin')
def assign_grades_to_learners(request):
    form = GradeFilterForm()
    context = {'form': form}
    return render(request, 'learners/grades_to_learners.html', context)

# todo: Change grade of a learner
# todo: Display information on learner detail page


@has_permission_decorator('admin')
def add_learners_from_file(request):
    messages.info(request, 'The reading from file is in progress. You can proceed with your work. '
                           'Once the process completed, learners will be listed in this page.')
    result = read_learners_from_file.delay()

    for message in result.collect():
        messages.info(request, message[1])

    return redirect('learners:list')
