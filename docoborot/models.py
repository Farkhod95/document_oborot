from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from directory.models import Region, District, Country
from restapp.models import BaseModel
User = settings.AUTH_USER_MODEL

