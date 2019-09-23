from django.db import models
from django.shortcuts import reverse
from django.core.validators import ValidationError
from django.utils.text import slugify

from academic_year.models import AcademicYear
from settings.models import Settings


def get_maximum_section(value):
    settings = Settings.objects.first()
    if value > settings.last_section:
        raise ValidationError(f'Maximum section for grade must be less than or equal to {settings.last_section}')


def get_division_name():
    return Settings.objects.first().division


class ActiveGradeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True).select_related('year')


class Grade(models.Model):
    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='grades')
    division = models.CharField(max_length=25, default=get_division_name)
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
        return f"{self.division} {self.section} {self.branch}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        slug_str = f"{self.division} {self.section} {self.branch} {self.year}"
        self.slug = slugify(slug_str)
        return super().save()


    def get_absolute_url(self):
        return reverse('grades:details', args=[self.slug])

    def get_update_url(self):
        return reverse('grades:edit', args=[self.slug])

    def get_delete_url(self):
        return reverse('grades:delete', args=[self.slug])