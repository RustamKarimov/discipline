from django.http import JsonResponse
from django.db.models import Count

from discipline.models import DisciplineAction, Discipline
from users.models import Learner


def get_discipline_action_pie_chart(request):
    merit_count = DisciplineAction.objects.filter(action__discipline_type=Discipline.MERIT).count()
    demerit_count = DisciplineAction.objects.filter(action__discipline_type=Discipline.DEMERIT).count()
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


def get_top_five_discipline_learner_bar_chart(request, discipline_type):
    learner_list = DisciplineAction.objects.values('learner').filter(action__discipline_type=discipline_type).annotate(
        learner_count=Count('learner')
    ).order_by('-learner_count')[:5]

    chart_data = {
        'type': 'bar',

        'data': {
            'labels': [Learner.objects.get(id=item['learner']).user.get_full_name() for item in learner_list],

            'datasets': [{
                'backgroundColor': ['rgb(128, 128, 128)'] * 5,
                'borderColor': 'rgb(255, 99, 132)',
                'data': [item['learner_count'] for item in learner_list]
            }]
        },
        'options': {
            'title': {
                'display': True,
                'text': 'Top 5 Merit Learners'
            },
            'legend': {
                'display': False
            },
            'scales': {
                'yAxes': [{
                    'ticks': {
                        'beginAtZero': True
                    }
                }]
            }
        }
    }
    return JsonResponse(chart_data)


def get_top_five_merit_learner_bar_chart(request):
    return get_top_five_discipline_learner_bar_chart(request, Discipline.MERIT)


def get_top_five_demerit_learner_bar_chart(request):
    return get_top_five_discipline_learner_bar_chart(request, Discipline.DEMERIT)