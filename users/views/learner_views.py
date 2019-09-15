from rolepermissions.mixins import HasPermissionsMixin

from ..models import Learner
from ..forms import UserForm
from .. import mixins


class LearnerList(HasPermissionsMixin, mixins.UserList):
    required_permission = 'admin'
    model = Learner
    paginate_by = 10


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
