from django.views import generic

from .models import Teacher


class TeacherList(generic.ListView):
    model = Teacher
    template_name = 'teachers/list.html'
    paginate_by = 10