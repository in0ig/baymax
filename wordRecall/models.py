# -*- coding: utf-8 -*-
from django.db import models
import datetime
from django.contrib.auth.models import User
import urllib

from django.utils import timezone
WORD_TYPE_COMMON = 0
WORD_TYPE_INVALID = 500

WORD_TYPE_CHOICES = [
    (WORD_TYPE_COMMON, "普通"),
    (WORD_TYPE_INVALID, "无效"),
]


class Word(models.Model):
    CHOICES_REPEATED = []
    for i in range(11):
        CHOICES_REPEATED.append((i, '%s' %i))

    spelling = models.CharField("拼写", max_length=100, null=False)
    repeated = models.IntegerField("复现率", default=0);
    type = models.IntegerField("类型", choices=WORD_TYPE_CHOICES, default=WORD_TYPE_COMMON)
    meaning = models.CharField("翻译", max_length=1024*8)
    google_meaning = models.CharField("Google翻译", max_length=1024, default='')

    def add_repeated(self, number=1):
        self.repeated = self.repeated + number
        self.save()

    def get_meaning(self):
        return self.google_meaning

    def get_meaning_from_baidu(self):
        if not self.meaning:
            try:
                params = urllib.urlencode({'query': self.spelling, 'from': 'en', 'to': 'zh'})
                f = urllib.urlopen("http://apistore.baidu.com/microservice/dictionary?%s" % params)
                self.meaning = f.read()
                self.save()
            except:
                pass
        return self.meaning

    def __str__(self):
        return self.spelling

CHOICE_REMEMBER_CONVERSANT = 1
CHOICE_REMEMBER_UNACQUAINTED = 3

class WordRememberInfos(models.Model):

    CHOICE_REMEMBER_CONVERSANT = 1
    CHOICE_REMEMBER_UNACQUAINTED = 3

    word = models.ForeignKey(Word)
    user = models.ForeignKey(User)

    CHOICES_REMEMBER = [(CHOICE_REMEMBER_CONVERSANT, "熟词,不再复现"),
                        (2, "似曾相识，下次还要提问"),
                        (CHOICE_REMEMBER_UNACQUAINTED, "生词，未掌握"),
                        (4, "未分类"),
   ]

    CHOICES_WEIGHT = [(1, "非常重要"),
        (2, "比较重要"),
        (3, "一般"),
        (4, "不重要"),
        (5, "完全不用记"),
   ]

    word_spelling = models.CharField("拼写", max_length=100)
    weight = models.IntegerField("重要度", default=3, choices=CHOICES_WEIGHT)
    remember = models.IntegerField("记住程度", default=4, choices=CHOICES_REMEMBER)
    recall_counts = models.IntegerField("记忆次数", default=0);
    repeated = models.IntegerField("复现率", default=0);
    remarks = models.CharField("备注", max_length=100, null=True)
    change_time = models.DateTimeField("上次修改时间")

    def get_repeated(self):
        return self.word.repeated
    get_repeated.admin_order_field = 'word__spelling'
    get_repeated.integer = True

    def recall_once(self):
        self.recall_counts = self.recall_counts + 1
        self.save()
        recallInfo = RecallInfo()
        recallInfo.word_recall = self
        recallInfo.recall_time = datetime.datetime.now()
        recallInfo.save()

    def to_dict(self):
        return {"spelling": self.word_spelling, "status": self.remember}

    def save(self, *args, **kwargs):
        self.change_time = timezone.now()
        return super(WordRememberInfos, self).save(*args, **kwargs)

    def __str__(self):
        return '%s_%s' % (self.user.pk, self.word_spelling)


class RequestUrl(models.Model):
    title = models.CharField("标题", max_length=500, default="")
    url = models.CharField("访问链接", max_length=500)


class RequestHistory(models.Model):
    url = models.ForeignKey(RequestUrl)
    user = models.ForeignKey(User)
    url_info = models.CharField("访问链接", max_length=500)

    request_number = models.IntegerField("请求次数", default=0)


class RecallInfo(models.Model):
    CHOICES_REMEMBER = []
    for i in range(11):
        CHOICES_REMEMBER.append((i, '记住%s成' %i))
    word_recall = models.ForeignKey(WordRememberInfos)
    recall_time = models.DateTimeField()
    remember = models.IntegerField("记住程度", default=0, choices=CHOICES_REMEMBER)


class IgnoreUrl(models.Model):
    user = models.ForeignKey(User, related_name='ignore_urls')
    url = models.CharField(max_length=100, default='', null=True)

    class Meta:
        unique_together = ('user', 'url')

