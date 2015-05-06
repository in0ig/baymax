# -*- coding: utf-8 -*-
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from models import Word, User, WordRememberInfos
from django.forms import ModelForm
from django import forms
import test
import urllib
import models
import translate
from django.http import HttpResponseRedirect

class TransPageForm(forms.Form):
    tran_page = forms.CharField(label='tran_page', max_length=100)



class RecallWordForm(ModelForm):

    class Meta:
        model = WordRememberInfos
        fields = ['word_spelling', 'weight', 'remember', 'recall_counts', 'repeated', 'remarks']
        # fields = '__all__'
        widgets = {
            "remember": forms.RadioSelect()
        }

def call(request):
    if request.method:
        callMethod = request.GET['call']

        if callMethod == 'init':
            init()
        if callMethod == 'init2':
            init2()
        if callMethod == 'init3':
            init3()
        if callMethod == 'init4':
            init4()
        if callMethod == 'init5':
            init5()
        if callMethod == 'init6':
            init6()
        return HttpResponse(callMethod)


def get_recall_word(request):
    return _get_words(request, models.CHOICE_REMEMBER_UNACQUAINTED)

def get_tran_page(request):

    KEY = 'tran_page'
    if request.method == 'POST':
        trans_url = request.POST[KEY]
        return HttpResponseRedirect('/word/tran?tran_page=%s' %trans_url)
    elif request.method == 'GET':
        if request.GET.has_key(KEY):
            trans_url = request.GET[KEY]
            return __get_tran_page(trans_url)
        else:
            form = TransPageForm()
            return render(request, 'recall/tran_page.html', {"form": form} )

def __get_tran_page(trans_url):
    print trans_url
    return HttpResponse( translate.get_translate_page(trans_url) )

def _get_words(request, filter):
    if request.method == 'POST':
        recall_id = request.POST['xid']
        recall_word = WordRememberInfos.objects.get(pk=recall_id)
        form = RecallWordForm(request.POST, instance=recall_word)
        if form.is_valid():
            if request.POST['commitType'] == '1':
                recall_word.remember = 1
            recall_word.recall_once()
            form.save()

    recall_word = WordRememberInfos.objects.filter(remember=filter).order_by('-word__repeated')[0]
    form = RecallWordForm(instance=recall_word)
    return render(request, 'recall/recall.html', {"form": form, "id":recall_word.pk} )

def init():

    Word.objects.all().delete()
    resultFile = r'/Users/lxzMac/pycharmProjects/mycode/python/wordRemember/result.txt'

    lines = open(resultFile).readlines()
    need2create = []
    for line in lines:
        line = line.strip()
        strs = line.split(' ')
        w = Word()
        w.spelling = strs[0]
        w.repeated = strs[1]
        need2create.append(w)
        # w.save()
    Word.objects.bulk_create(need2create)


def init2():
    need2create = []
    WordRememberInfos.objects.all().delete()
    user = User.objects.all()[0]

    for word in Word.objects.all():
        info = WordRememberInfos()
        info.user = user
        info.word = word
        need2create.append(info)
        # info.save()
        # print info.pk
    WordRememberInfos.objects.bulk_create(need2create)


def init3():

    for recall in WordRememberInfos.objects.all():
        recall.word_spelling = recall.word.spelling
        recall.repeated = recall.word.repeated
        recall.save()

def init4():

    for word in Word.objects.all():
        word.meaning = test.get_meaning_of_word(word.spelling)
        print word.meaning
        word.save()

def init5():
    for word in Word.objects.all():
        print word.spelling
        word.type = test.is_complex(word.spelling, word.meaning)
        word.save()

def init6():
    for word in Word.objects.all():

        if word.repeated == 1 and word.type == models.WORD_TYPE_INVALID:
            print word.spelling
            word.delete()
