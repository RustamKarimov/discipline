import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse

# from settings.models import Settings


def current_year():
    return datetime.datetime.now().year


def validate_year(value):
    if value < current_year():
        raise ValidationError(f'Year must be greater than or equal to {current_year()}')
    if len(str(value)) != 4:
        raise ValidationError('Year must consist of 4 digits.')


class AcademicYear(models.Model):
    year = models.PositiveIntegerField(
        validators=[validate_year],
        verbose_name='academic year',
        help_text=f'Add new academic year greater than {current_year()} in 4-digit format.',
        default=current_year(),
        unique=True
    )
    active = models.BooleanField(default=True)
    slug = models.SlugField()

    class Meta:
        ordering = ['-year']

    def __str__(self):
        return str(self.year)

    def save(self, *args, **kwargs):
        self.slug = str(self.year)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('years:details', args=[self.slug])

    def get_update_url(self):
        return reverse('years:edit', args=[self.slug])
    #
    def get_delete_url(self):
        return reverse('years:delete', args=[self.slug])