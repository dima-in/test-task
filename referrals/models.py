from django.db import models


class UserProfile(models.Model):
    phone = models.IntegerField(max_length=20, unique=True, null=True, blank=True)
    invite_code = models.CharField(max_length=6, null=True, blank=True)
    inviter = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    authorization_code = models.IntegerField(max_length=4, null=True, blank=True)

