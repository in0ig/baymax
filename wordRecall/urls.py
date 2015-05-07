# -*- coding: utf-8 -*-
__author__ = 'likang'
from django.conf.urls import patterns, url
from django.contrib import admin
import views
admin.autodiscover()

urlpatterns =[
    url(r'^call/?', views.call),
    url(r'^recall/?', views.get_recall_word, name='recall'),
    url(r'^tran/?', views.get_tran_page, name='tran'),
    url(r'^word_translate/?', views.translate_word, name='translate_word'),
    url(r'^set_word_status/?', views.get_word_infos, name='translate_word'),

]

import logging
l = logging.getLogger('django.db.backends')
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())