from django.core.validators import MaxValueValidator, RegexValidator
from django.db import models


class UserProfile(models.Model):

    phone_number = models.CharField(max_length=17, blank=True)
    invite_code = models.CharField(max_length=6, null=True, blank=True)
    used_foreign_invite = models.BooleanField(default=False)
    authorization_code = models.PositiveIntegerField(validators=[MaxValueValidator(9999)], null=True, blank=True)
    # пользователи, использовавшие мой инвайт-код
    referral_users = models.ManyToManyField('self', blank=True)

