from django.shortcuts import render, redirect
from django.db.models import Q
from django.forms import modelformset_factory, BaseModelFormSet
from django.contrib import messages

from grades.models import Grade
from users.models import Learner
from .forms import AssignGradesToLearnersForm


def get_learners(request):
    grade_id = request.GET.get('grade')
    try:
        name = request.GET.get('name')
    except:
        name = None

    if grade_id:
        grade = Grade.objects.get(id=grade_id)
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
                    print(grade, learner)

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