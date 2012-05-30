try:
    from hashlib import md5
except:
    from md5 import new as md5
import re

from django.http import QueryDict
from django.db import models
from django import forms
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator

from scielomanager import settings
from scielomanager.journalmanager import models as journalmanager_models


def handle_uploaded_file(f):
    upload_suffix = join('img/collections_logos', f.name)
    upload_path = join(settings.MEDIA_ROOT, upload_suffix)
    destination = open(upload_path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return upload_suffix

class MultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple

    def __init__(self, *args, **kwargs):
        self.max_choices = kwargs.pop('max_choices', 0)
        super(MultiSelectFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        if value and self.max_choices and len(value) > self.max_choices:
            raise forms.ValidationError('You must select a maximum of %s choice%s.'
                    % (apnumber(self.max_choices), pluralize(self.max_choices)))
        return value

class MultiSelectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def get_choices_default(self):
        return self.get_choices(include_blank=False)

    def _get_FIELD_display(self, field):
        value = getattr(self, field.attname)
        choicedict = dict(field.choices)

    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank, 'label': capfirst(self.verbose_name),
                    'help_text': self.help_text, 'choices':self.choices}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)

    def get_db_prep_value(self, value):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ",".join(value)

    def to_python(self, value):
        if isinstance(value, list):
            return value
        return value.split(",")

    def contribute_to_class(self, cls, name):
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            func = lambda self, fieldname = name, choicedict = dict(self.choices):",".join([choicedict.get(value,value) for value in getattr(self,fieldname)])
            setattr(cls, 'get_%s_display' % self.name, func)

def get_paginated(items, page_num, items_per_page=settings.PAGINATION__ITEMS_PER_PAGE):
    """
    Wraps django core pagination object
    """
    paginator = Paginator(items, items_per_page)

    try:
        page_num = int(page_num)
    except ValueError:
        raise TypeError('page_num must be integer')

    try:
      paginated = paginator.page(page_num)
    except EmptyPage:
      paginated = paginator.page(paginator.num_pages)

    return paginated

# Copyright (c) 2009 Arthur Furlan <arthur.furlan@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# On Debian systems, you can find the full text of the license in
# /usr/share/common-licenses/GPL-2

def get_referer_view(request, default=None):
    '''
    Return the referer view of the current request

    Example:

        def some_view(request):
            ...
            referer_view = get_referer_view(request)
            return HttpResponseRedirect(referer_view, '/accounts/login/')
    '''

    # if the user typed the url directly in the browser's address bar
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return default

    # remove the protocol and split the url at the slashes
    referer = re.sub('^https?:\/\/', '', referer).split('/')
    #if referer[0] != request.META.get('SERVER_NAME'):
        #return default

    # add the slash at the relative path's view and finished
    referer = u'/' + u'/'.join(referer[1:])
    return referer

class PendingPostData(object):

    def __init__(self, data):
        """
        data is the request.POST QueryDict.
        """
        self.data = data

    def hash_data(self):
        content = ','.join('%s:%s' % (k.encode('utf-8'), v.encode('utf-8')) for k, v in self.data.items())
        return md5(content).hexdigest()

    def pend(self, view_name, user):

        form_hash = self.hash_data()

        pended_form = journalmanager_models.PendedForm.objects.get_or_create(view_name=view_name,
            form_hash=form_hash, user=user)[0]

        for name, values in self.data.lists():
            for value in values:
                pended_form.data.get_or_create(name=name, value=value)

        if self.data.get('form_hash', None) and self.data['form_hash'] != 'None':
            journalmanager_models.PendedForm.objects.get(form_hash=self.data['form_hash']).delete()

        return form_hash
    @classmethod
    def resume(self, form_hash):
        form = journalmanager_models.PendedForm.objects.get(form_hash=form_hash)

        post_dict = QueryDict('', mutable=True)
        for d in form.data.all():
            i = post_dict.setlistdefault(d.name, [])
            i.append(d.value)

        return post_dict