from django.shortcuts import render, redirect,reverse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm

from school_discipline.roles import TeacherRole, LearnerRole
from rolepermissions.checkers import has_role
from rolepermissions.decorators import has_permission_decorator

from settings.models import Settings
from academic_year.models import AcademicYear
from grades.models import Grade
from discipline.models import Discipline, DisciplineAction
from users.models import Teacher, Learner


class Login(LoginView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        url = self.get_redirect_url()

        if url:
            return url

        if user.is_superuser:
            return reverse('dashboard')

        if has_role(user, TeacherRole):
            return reverse('teachers:details', args=[user.teacher.slug])

        if has_role(user, LearnerRole):
            return reverse('learners:details', args=[user.learner.slug])


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required
@has_permission_decorator('admin')
def dashboard(request):

    if not Settings.objects.first():
        Settings.objects.create()

    # Statistics
    year_count = AcademicYear.objects.count()
    grade_count = Grade.active_grades.count()
    teacher_count = Teacher.objects.count()
    learner_count = Learner.objects.count()
    merit_count = Discipline.merits.count()
    demerit_count = Discipline.demerits.count()
    merit_action_count = DisciplineAction.objects.filter(action__discipline_type=Discipline.MERIT).count()
    demerit_action_count = DisciplineAction.objects.filter(action__discipline_type=Discipline.DEMERIT).count()

    # Last Merits and Demerits
    last_5_merits = DisciplineAction.objects.select_related('action').filter(
        action__discipline_type=Discipline.MERIT)[:5]
    last_5_demerits = DisciplineAction.objects.select_related('action').filter(
        action__discipline_type=Discipline.DEMERIT)[:5]

    context = {
        'active': 'dashboard',
        'year_count': year_count,
        'grade_count': grade_count,
        'teacher_count': teacher_count,
        'learner_count': learner_count,
        'merit_count': merit_count,
        'demerit_count': demerit_count,
        'merit_action_count': merit_action_count,
        'demerit_action_count': demerit_action_count,

        'last_5_merits': last_5_merits,
        'last_5_demerits': last_5_demerits,
    }
    return render(request, 'dashboard.html', context)

# todo: Read from file must be done through select file form
# todo: Generate reports for specific learner or for all learners
# todo: Generate reports for specific teacher or for all teachers
# todo: Generate statistics about teachers
# todo: Generate statistics about learners
# todo: Generate graphs
# todo: Send emails
