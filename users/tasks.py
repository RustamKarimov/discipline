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


@shared_task
def add(x, y):
    return x + y


@shared_task
def read_teachers_from_file(filename=TEACHERS_FILENAME):
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

        teacher_id = row['SchoolId']
        first_name = row['FirstName']
        last_name = row['LastName']

        user_model = get_user_model()

        user, created = user_model.objects.get_or_create(
            user_id=teacher_id,
            username=teacher_id,
            first_name=first_name,
            last_name=last_name,
        )

        if created:
            user.set_password(teacher_id)
            user.save()
            assign_role(user, 'teacher_role')

            slug_str = f"{teacher_id} {first_name} {last_name}"

            teacher, teacher_created = Teacher.objects.get_or_create(
                user=user,
            )
            if grade:
                teacher.form_class.add(grade)

    return 'Reading teachers from file completed...'
