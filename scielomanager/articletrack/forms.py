# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm, Textarea, TextInput
from articletrack import models
from journalmanager.models import Journal


class CommentMessageForm(ModelForm):
    class Meta:
        model = models.Comment
        fields = ('message',)
        widgets = {
            'message': Textarea(attrs={'class': 'span12'}),
        }


class TicketForm(ModelForm):
    class Meta:
        model = models.Ticket
        fields = ('title', 'message',)
        widgets = {
            'title': TextInput(attrs={'class': 'span12'}),
            'message': Textarea(attrs={'class': 'span12'}),
        }


class CheckinListFilterForm(forms.Form):
    package_name = forms.CharField(max_length=128, required=False)
    journal_title = forms.ChoiceField(required=False)
    article = forms.ModelChoiceField(queryset=None, required=False)
    issue_label = forms.CharField(max_length=64, required=False)

    def __init__(self, *args, **kwargs):
        super(CheckinListFilterForm, self).__init__(*args, **kwargs)
        qs_articles_with_checkins = models.Article.userobjects.filter(checkins__isnull=False).distinct()
        self.fields['journal_title'].choices = [('', '---------'), ] + [(article.pk, article.journal_title) for article in qs_articles_with_checkins]
        self.fields['article'].queryset = qs_articles_with_checkins
