from django.views import generic

from rolepermissions.mixins import HasPermissionsMixin

from ..models import Learner, User


class LearnerList(HasPermissionsMixin, generic.ListView):
    required_permission = 'admin'
    model = Learner
    template_name = 'learners/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'learners'
        return context
