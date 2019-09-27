import datetime
from django.http import JsonResponse
from django.db.models import Count, DateTimeField
from django.db.models.functions import Trunc
from django.shortcuts import get_object_or_404

from dateutil.relativedelta import relativedelta

from discipline.models import DisciplineAction, Discipline
from users.models import Learner, Teacher


def get_discipline_action_pie_chart(request, slug):
    teacher = get_object_or_404(Teacher, slug=slug)
    merit_count = DisciplineAction.objects.filter(
        action__discipline_type=Discipline.MERIT,
        teacher=teacher
    ).select_related('teacher').count()
    demerit_count = DisciplineAction.objects.filter(
        action__discipline_type=Discipline.DEMERIT,
        teacher=teacher
    ).select_related('teacher').count()

    chart_data = {
        'type': 'doughnut',

        'data': {
            'labels': ['Merits', 'Demerits'],

            'datasets': [{
                'label': 'Merit vs Demerit',
                'backgroundColor': ['rgb(128, 128, 128)', 'rgb(211, 211, 211)'],
                'borderColor': 'rgb(255, 99, 132)',
                'data': [merit_count, demerit_count]
            }]
        },
        'options': {
            'title': {
                'display': True,
                'text': 'Merits vs Demerits'
            },
            'cutoutPercentage': 50
        }
    }
    return JsonResponse(chart_data)


def get_discipline_per_week_last_month(request, slug, discipline_type):
    teacher = get_object_or_404(Teacher, slug=slug)

    chart_title = 'Merits per week' if discipline_type == Discipline.MERIT else 'Demerits per week'

    now = datetime.datetime.now()
    one_month_before = now - relativedelta(months=1)

    discipline_per_week = DisciplineAction.objects.filter(
        teacher=teacher, action__discipline_type=discipline_type, time__gte=one_month_before
    ).annotate(week=Trunc('time', 'week')).values('week').annotate(
        discipline_count=Count('id')).order_by('week')

    chart_data = {
        'type': 'line',

        'data': {
            'labels': [f"Week {item['week'].isocalendar()[1]}" for item in discipline_per_week],

            'datasets': [
                {
                    'backgroundColor': ['rgb(211, 211, 211)'],
                    'borderColor': 'rgb(255, 99, 132)',
                    'data': [item['discipline_count'] for item in discipline_per_week]
                },
            ]
        },
        'options': {
            'title': {
                'display': True,
                'text': chart_title
            },
            'legend': {
                'display': False
            }
        }
    }
    return JsonResponse(chart_data)


def get_merits_per_week_last_month(request, slug):
    return get_discipline_per_week_last_month(request, slug, Discipline.MERIT)


def get_demerits_per_week_last_month(request, slug):
    return get_discipline_per_week_last_month(request, slug, Discipline.DEMERIT)