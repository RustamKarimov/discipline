from django.urls import path

from . import charts
urlpatterns = [
    path('pie/discipline-actions/', charts.get_discipline_action_pie_chart,  name='pie_chart_discipline_action'),
    path('bar/top-5-merits/', charts.get_top_five_merit_learner_bar_chart, name='bar_top_five_merit_learner_chart'),
    path('bar/top-5-demerits/', charts.get_top_five_demerit_learner_bar_chart, name='bar_top_five_demerit_learner_chart'),
]
