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
