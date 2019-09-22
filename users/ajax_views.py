from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.forms import modelformset_factory, BaseModelFormSet
from django.contrib import messages

from academic_year.models import AcademicYear

from grades.models import Grade

from discipline.models import Discipline, DisciplineAction
from discipline.forms import DisciplineGradeForm

from users.models import Learner, Teacher

from .forms import AssignGradesToLearnersForm


def get_learners(request, grade=None):
    if not grade:
        grade_id = request.GET.get('grade_id')
        if grade_id:
            grade = Grade.objects.get(id=grade_id)

    try:
        name = request.GET.get('name')
    except:
        name = None

    if grade:
        learners = Learner.objects.filter(grades=grade, user__current_user=True)
    elif not name:
        learners = Learner.objects.filter(user__current_user=True, grades=None)
    else:
        learners = Learner.objects.filter(user__current_user=True)

    if name:
        learners = learners.filter(Q(user__first_name__icontains=name) | Q(user__last_name__icontains=name))

    return learners


def load_learners_per_grade(request):
    learners = get_learners(request)
    return render(request, 'learners/learners_per_grade_table.html', {'learner_list': learners})


class AssignGradeBaseModelFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Learner.objects.none()


def grade_formset_for_learners(request):
    learners = get_learners(request)
    learner_formset = modelformset_factory(Learner, form=AssignGradesToLearnersForm)

    if request.method == 'POST':
        formset = learner_formset(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.is_valid() and form.cleaned_data:
                    learner = form.cleaned_data['id']

                    grade = form.cleaned_data['grades']

                    if grade:
                        ex_grade = learner.get_active_grade()
                        learner.grades.remove(ex_grade)
                        learner.grades.add(grade)
            messages.info(request, 'Assigning grades to learners been completed...')
            return redirect('learners:assign_grades')
    else:
        formset = learner_formset(queryset=learners)

    context = {
        'learners_formset': zip(learners, formset),
        'formset': formset,
        'learners': learners
    }

    return render(request, 'learners/sub_grades_to_learners.html', context)

    # todo: this will be called by ajax and validate the grades for learners


def load_learners(request):
    grade_id = request.GET.get('grade')
    grade = Grade.objects.get(id=grade_id)
    learners = Learner.objects.filter(grades=grade)
    return render(request, 'teachers/learner_dropdown_options.html', {'learners': learners})


class DisciplineBaseModelFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Discipline.objects.none()


def load_discipline_actions_for_grade(request):
    if request.POST:
        grade_slug = request.POST['grade_slug']
        grade = Grade.objects.get(slug=grade_slug)
        teacher_slug = request.POST['teacher_slug']
        teacher = Teacher.objects.get(slug=teacher_slug)
        discipline_type = request.POST['discipline_type']
        learners = get_learners(request, grade)
    else:
        grade_id = request.GET.get('grade_id')
        grade = Grade.objects.get(id=int(grade_id))
        teacher_slug = request.GET.get('teacher_slug')
        teacher = Teacher.objects.get(slug=teacher_slug)
        discipline_type = request.GET.get('discipline_type')
        learners = get_learners(request)

    year = AcademicYear.objects.get(active=True)

    discipline_formset = modelformset_factory(Discipline, form=DisciplineGradeForm,
                                              formset=DisciplineBaseModelFormset,
                                              extra=len(learners))
    formset = discipline_formset(request.POST or None,
                                 form_kwargs={'discipline_type': discipline_type})

    if formset.is_valid():
        for index, form in enumerate(formset):
            if form.is_valid() and form.cleaned_data:
                action = form.cleaned_data['action']
                time = form.cleaned_data['time']
                if action and time.year == year.year:
                    DisciplineAction.objects.create(
                        action=action,
                        learner=learners[index],
                        teacher=teacher,
                        time=time
                    )
        messages.info(request, f'{discipline_type}s were added to {grade} learners by {teacher} at {time}')
        if discipline_type.lower() == 'merit':
            return redirect('teachers:select_merit_grade', teacher.slug)
        else:
            return redirect('teachers:select_demerit_grade', teacher.slug)

    context = {
        'learners_formset': zip(learners, formset),
        'formset': formset,
        'grade_slug': grade.slug,
        'teacher_slug': teacher.slug,
        'discipline_type': discipline_type
    }

    return render(request, 'teachers/discipline_to_grade_table.html', context)