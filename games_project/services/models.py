# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from services import signals as gm_signals
import uuid

models.signals.post_save.connect(gm_signals.user_post_save, sender=User);

class Product(models.Model):
    name = models.CharField(max_length=30)
    product_type = models.CharField(max_length=50)
    price = models.IntegerField(max_length=20)

    def __str__(self):
        return self.name

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product)

    def __str__(self):
        return self.id

class UserProfile(models.Model):
    """
    A model to store extra information for each user.
    """
    user = models.OneToOneField(User, related_name='profile')
    gender = models.CharField(_("gender"), max_length=10)
    birth_year = models.PositiveIntegerField(_("birth year"))

    def __unicode__(self):
        return self.user.get_full_name()

    # def signals_import():
    #     from tastypie.models import create_api_key
    #     models.signals.post_save.connect(create_api_key, )
