# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from services import signals as gm_signals
import uuid

models.signals.post_save.connect(gm_signals.user_post_save, sender=User);
