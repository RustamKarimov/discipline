from django.urls import path

from ..views import teacher_charts as charts

urlpatterns = [
    path('pie/merit-demerit/', charts.get_discipline_action_pie_chart, name='merit_demerit_chart'),
    path('line/merit-per-week-last-month/', charts.get_merits_per_week_last_month, name='merit_per_week_last_month'),
    path('line/demerit-per-week-last-month/', charts.get_demerits_per_week_last_month, name='demerit_per_week_last_month'),
]