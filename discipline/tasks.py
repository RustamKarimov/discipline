from __future__ import absolute_import, unicode_literals

import pandas as pd

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import resolve

from celery import shared_task

from .models import Discipline

MERIT_FILENAME = 'static/excel/merits.xlsx'
DEMERIT_FILENAME = 'static/excel/demerits.xlsx'


@shared_task
def read_discipline_from_file(discipline):

    if discipline == 'merit':
        filename = MERIT_FILENAME
        discipline_type = Discipline.MERIT
    else:
        filename = DEMERIT_FILENAME
        discipline_type = Discipline.DEMERIT

    data = pd.read_excel(filename, index_col=None)
    for index, row in data.iterrows():
        code = row['CODE']
        description = row['REASON']
        point = row['POINTS']

        if code and description and point:
            discipline_object, created = Discipline.objects.get_or_create(
                code=code,
                description=description,
                point=point,
                discipline_type=discipline_type,
                slug=code,
            )

    return 'Reading from file has been completed... '

