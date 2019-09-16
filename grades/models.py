from django.db import models
from django.shortcuts import reverse
from django.core.validators import ValidationError

from academic_year.models import AcademicYear
from settings.models import Settings


def get_maximum_section(value):
    settings = Settings.objects.first()
    if value > settings.last_section:
        raise ValidationError(f'Maximum section for grade must be less than or equal to {settings.last_section}')


class ActiveGradeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class Grade(models.Model):
    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='grades')
    section = models.PositiveIntegerField(validators=[get_maximum_section])
    branch = models.CharField(max_length=5)
    active = models.BooleanField(default=True)
    slug = models.SlugField()

    objects = models.Manager()
    active_grades = ActiveGradeManager()

    class Meta:
        unique_together = ('year', 'section', 'branch')
        ordering = ('year', 'section', 'branch')

    def __str__(self):
        division = Settings.objects.first().division
        return f"{division} {self.section} {self.branch}"

    def get_absolute_url(self):
        return reverse('grades:details', args=[self.slug])

    # def get_update_url(self):
    #     return reverse('grades:update', args=[self.slug])
    #
    # def get_delete_url(self):
    #     return reverse('grades:delete', args=[self.slug])