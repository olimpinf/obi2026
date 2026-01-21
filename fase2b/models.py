from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.utils.html import mark_safe

from principal.models import (LANG_SUFFIXES_NAMES, LANGUAGE_CHOICES,
                              LEVEL_CHOICES_INI, LEVEL_CHOICES_PROG, Compet, School)


