from rolepermissions.mixins import HasPermissionsMixin

from ..models import Teacher
from ..forms import UserForm
from .. import mixins


class TeacherList(HasPermissionsMixin, mixins.UserList):
    required_permission = 'admin'
    model = Teacher
    paginate_by = 10


class TeacherAdd(HasPermissionsMixin, mixins.UserAdd):
    required_permission = 'admin'
    model = Teacher
    form_class = UserForm


class TeacherDetails(mixins.UserDetails):
    model = Teacher


class TeacherEdit(HasPermissionsMixin, mixins.UserEdit):
    required_permission = 'admin'
    model = Teacher
    form_class = UserForm


class TeacherDelete(HasPermissionsMixin, mixins.UserDelete):
    required_permission = 'admin'
    model = Teacher


# todo: Assign form classes to teacher
# todo: Change form_class of a learner
# todo: Display information on learner detail page
# todo: Read teachers from file
