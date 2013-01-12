# coding: utf-8
try:
    from hashlib import md5
except:
    from md5 import new as md5
import re

from django.http import QueryDict
from django.db.models.sql.datastructures import EmptyResultSet
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator

from scielomanager import settings
from scielomanager.journalmanager import models as journalmanager_models


class NullPaginator(object):
    """
    A null object implementation for a Paginator.
    http://en.wikipedia.org/wiki/Null_Object_pattern
    """
    def __getattr__(self, name):
        return None


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
    except EmptyResultSet:
        paginated = NullPaginator()

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


# Taken from Pyramid framework
# https://github.com/Pylons/pyramid/blob/master/pyramid/settings.py
truthy = frozenset(('t', 'true', 'y', 'yes', 'on', '1'))


def asbool(s):
    """ Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is any of ``t``, ``true``, ``y``, ``on``, or ``1``, otherwise
    return the boolean value ``False``. If ``s`` is the value ``None``,
    return ``False``. If ``s`` is already one of the boolean values ``True``
    or ``False``, return it."""
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy
