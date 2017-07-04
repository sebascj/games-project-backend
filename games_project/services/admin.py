# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from services.models import Product, Order, UserProfile

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(UserProfile)

# Register your models here.
