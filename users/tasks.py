from __future__ import absolute_import, unicode_literals

import pandas as pd

from django.contrib import messages
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from celery import shared_task, Celery, task

from rolepermissions.roles import assign_role

from academic_year.models import AcademicYear
from grades.models import Grade
from settings.models import Settings

from .models import Teacher, Learner

LEARNERS_FILENAME = 'static/excel/learners.xlsx'
TEACHERS_FILENAME = 'static/excel/teachers.xlsx'


def get_user_or_create(model, filename):
    data = pd.read_excel(filename, index_col=False)
    year = AcademicYear.objects.get(active=True)
    division = Settings.objects.first().division
    data = data.fillna(0)

    for index, row in data.iterrows():
        section = row['Section']
        if section:
            branch = row['Branch']
            slug_str = f"{division} {int(section)} {branch} {year}"
            slug = slugify(slug_str)
            grade, created = Grade.objects.get_or_create(
                year=year, section=int(section), branch=branch, active=True, slug=slug
            )
        else:
            grade = None

        user_id = row['SchoolId']
        first_name = row['FirstName']
        last_name = row['LastName']

        user_model = get_user_model()

        user, created = user_model.objects.get_or_create(
            user_id=user_id,
            username=user_id,
            first_name=first_name,
            last_name=last_name,
        )

        if created:
            user.set_password(user_id)
            user.save()

            user_type, user_type_created = model.objects.get_or_create(
                user=user,
            )

            if model == Learner:
                assign_role(user, 'learner_role')
                if grade:
                    user_type.grades.add(grade)
                user.is_learner = True
            else:
                assign_role(user, 'teacher_role')
                if grade:
                    user_type.form_class.add(grade)
                user.is_teacher = True

            user.save()

@shared_task
def read_learners_from_file(filename=LEARNERS_FILENAME):
    get_user_or_create(Learner, filename)
    return 'Reading learners from file completed...'



@shared_task
def read_teachers_from_file(filename=TEACHERS_FILENAME):
    get_user_or_create(Teacher, filename)
    return 'Reading teachers from file completed...'
