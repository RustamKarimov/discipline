from django.shortcuts import render
from django.db.models import Q

from grades.models import Grade
from users.models import Learner


def load_learners_per_grade(request):
    grade_id = request.GET.get('grade')
    name = request.GET.get('name')
    if grade_id:
        grade = Grade.objects.get(id=grade_id)
        learners = Learner.objects.filter(grades=grade, user__current_user=True)
    else:
        learners = Learner.objects.filter(user__current_user=True)

    if name:
        learners = learners.filter(Q(user__first_name__icontains=name) | Q(user__last_name__icontains=name))
    return render(request, 'learners/learners_per_grade_table.html', {'learner_list': learners})