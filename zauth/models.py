from django.db import models
from jsonfield import JSONField

class auth_db(models.Model):
    email = models.EmailField(unique=True, null=False, primary_key=True)
    password = models.CharField(max_length=10000, null=False)
    activation = models.BooleanField(default=False)

class tokens_db(models.Model):
    access_token = models.CharField(max_length=10000, unique=True)
    identity = models.EmailField(unique=True, null=False, primary_key=True)

class verificationSystem(models.Model):
    identity = models.EmailField(unique=True, null=False, primary_key=True)
    ActivationCode = models.CharField(max_length=8,null=False)

class userFields(models.Model):
    identity = models.EmailField(unique=True, null=False, primary_key=True)
    fields = JSONField(default=dict)