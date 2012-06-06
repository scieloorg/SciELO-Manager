import json
import urllib

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.urlresolvers import resolve
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import loader
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils.functional import curry
from django.utils.html import escape

from django.core.cache import cache

from scielomanager.journalmanager.models import get_user_collections
from scielomanager.journalmanager import models
from scielomanager.journalmanager.forms import *
from scielomanager.tools import get_paginated
from scielomanager.tools import get_referer_view
from scielomanager.tools import handle_uploaded_file
from scielomanager.tools import PendingPostData

MSG_FORM_SAVED = _('Saved.')
MSG_FORM_SAVED_PARTIALLY = _('Saved partially. You can continue to fill in this form later.')
MSG_FORM_MISSING = _('There are some errors or missing data.')
MSG_DELETE_PENDED = _('The pended form has been deleted.')



def section_has_relation(section_id):

    if len(models.Issue.objects.filter(section=section_id)) == 0 :
        return False
    else:
        return True

def index(request):
    template = loader.get_template('journalmanager/home_journal.html')
    if request.user.is_authenticated():
        user_collections = get_user_collections(request.user.id)
        pending_journals = models.PendedForm.objects.filter(user=request.user.id).filter(view_name='journal.add').order_by('-created_at')
    else:
        user_collections = ''
        pending_journals = ''

    context = RequestContext(request,{'user_collections':user_collections,'pending_journals': pending_journals})
    return HttpResponse(template.render(context))

@login_required
def issue_index(request, journal_id):
    user_collections = get_user_collections(request.user.id)
    journal = models.Journal.objects.get(pk=journal_id)
    objects_all = models.Issue.objects.available(request.GET.get('is_available')).filter(journal=journal_id).order_by('-publication_date')

    by_years = OrderedDict()
    for issue in objects_all:
        year_node = by_years.setdefault(issue.publication_date.year, {})
        volume_node = year_node.setdefault(issue.volume, [])

        volume_node.append(issue)

    for year, volume in by_years.items(): #ordering by issue number
        for vol, issues in volume.items():
            issues.sort(key=lambda x: x.number)

    template = loader.get_template('journalmanager/issue_dashboard.html')
    context = RequestContext(request, {
                       'journal': journal,
                       'user_collections': user_collections,
                       'issue_grid': by_years,

                       })
    return HttpResponse(template.render(context))

@login_required
def generic_index_search(request, model, journal_id = None):
    """
    Generic list and search
    """
    user_collections = get_user_collections(request.user.id)
    default_collections = user_collections.filter(is_default=True)

    if journal_id:
        journal = models.Journal.objects.get(pk=journal_id)
        objects_all = model.objects.filter(journal=journal_id)
    else:
        journal = None
        objects_all = model.objects.all_by_user(request.user)

        #filtering by pub_status is only available to Journal instances.
        if model is models.Journal and request.GET.get('jstatus'):
            objects_all = objects_all.filter(pub_status=request.GET['jstatus'])


    if request.GET.get('q'):
        objects_all = model.objects.all_by_user(request.user)

        if issubclass(model, models.Institution):
            objects_all = objects_all.filter(
                name__icontains=request.REQUEST['q']).order_by('name')
        else:
            objects_all = objects_all.filter(
                title__icontains = request.REQUEST['q']).order_by('title')


    objects = get_paginated(objects_all, request.GET.get('page', 1))
    template = loader.get_template('journalmanager/%s_dashboard.html' % model.__name__.lower())
    context = RequestContext(request, {
                       'objects_%s' %  model.__name__.lower(): objects,
                       'journal': journal,
                       'user_collections': user_collections,
                       })
    return HttpResponse(template.render(context))

@login_required
def generic_toggle_availability(request, object_id, model):

  if request.is_ajax():

    model = get_object_or_404(model, pk = object_id)
    model.is_trashed = not model.is_trashed
    model.save()

    response_data = json.dumps({
      "result": str(model.is_trashed),
      "object_id": model.id
      })

    #ajax response json
    return HttpResponse(mimetype="application/json")
  else:
    #bad request
    return HttpResponse(status=400)

@login_required
def toggle_active_collection(request, user_id, collection_id):
    '''
        Redifine the active collection, changing the administrative context to another collection.
    '''

    # Setting up all user collections.is_default to False
    user_collections = get_user_collections(request.user.id)
    user_collections.all().update(is_default = False)

    # Setting up the new default collection
    user_collections.filter(collection__pk = collection_id).update(is_default = True)

    referer = get_referer_view(request)

    return HttpResponseRedirect(referer)

@login_required
def generic_bulk_action(request, model_name, action_name, value = None):
    info_msg = None
    MSG_MOVED = _('The selected documents had been moved to the Trash.')
    MSG_RESTORED = _('The selected documents had been restored.')

    model_refs = {
        'journal': models.Journal,
        'section': models.Section,
        'publisher': models.Publisher,
        'sponsor': models.Sponsor,
    }
    model = model_refs.get(model_name)

    if request.method == 'POST':
        items = request.POST.getlist('action')
        for doc_id in items:
            doc = get_object_or_404(model, pk=doc_id)

            #toggle doc availability
            if action_name == 'is_available':
                if isinstance(doc, models.Journal):
                    doc.is_trashed = True if int(value) == 0 else False
                    doc.save()
                    info_msg = MSG_MOVED if doc.is_trashed else MSG_RESTORED
                elif isinstance(doc, models.Section):
                    if not section_has_relation(doc_id):
                        doc.is_trashed = True if int(value) == 0 else False
                        doc.save()
                        info_msg = MSG_MOVED if doc.is_trashed else MSG_RESTORED
                elif isinstance(doc, models.Institution): #Sponsor and Publisher
                    doc.is_trashed = True if int(value) == 0 else False
                    doc.save()
                    info_msg = MSG_MOVED if doc.is_trashed else MSG_RESTORED

    if info_msg:
        messages.info(request, info_msg)
    return HttpResponseRedirect(get_referer_view(request))

@login_required
def user_index(request):

    user_collections = get_user_collections(request.user.id)
    user_collections_managed = user_collections.filter(is_manager=True)

    # Filtering users manager by the administrator
    all_users = models.User.objects.filter(usercollections__collection__in = ( collection.collection.pk for collection in user_collections_managed )).distinct('username')
    users = get_paginated(all_users, request.GET.get('page', 1))

    t = loader.get_template('journalmanager/user_dashboard.html')

    c = RequestContext(request, {
                       'users': users,
                       'user_collections': user_collections,
                       })
    return HttpResponse(t.render(c))

def user_login(request):

    next = request.GET.get('next', None)

    if request.method == 'POST':
        next = request.POST['next']
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                user_collections = get_user_collections(request.user.id)

                if next != '':
                    return HttpResponseRedirect(next)
                else:
                    t = loader.get_template('journalmanager/home_journal.html')
                c = RequestContext(request, {'active': True,
                                             'user_collections': user_collections,})
                return HttpResponse(t.render(c))
            else: #Login Success User inactive
                t = loader.get_template('journalmanager/home_journal.html')
                c = RequestContext(request, {'active': True,})
                return HttpResponse(t.render(c))
        else: #Login Failed
            t = loader.get_template('journalmanager/home_journal.html')
            c = RequestContext(request, {
                               'invalid': True, 'next': next,})
            return HttpResponse(t.render(c))
    else:
        t = loader.get_template('journalmanager/home_journal.html')
        if next:
            c = RequestContext(request, {'required': True, 'next': next,})
        else:
            c = RequestContext(request, {'required': True})
        return HttpResponse(t.render(c))

@login_required
def user_logout(request):
    logout(request)
    t = loader.get_template('journalmanager/home_journal.html')
    c = RequestContext(request)
    return HttpResponse(t.render(c))

@login_required
@permission_required('auth.add_user')
def add_user(request, user_id=None):
    """
    Handles new and existing users
    """
    if  user_id == None:
        user = User()
    else:
        user = get_object_or_404(User, id = user_id)

    # Getting Collections from the logged user.
    user_collections = get_user_collections(request.user.id)

    UserProfileFormSet = inlineformset_factory(User, models.UserProfile, )
    UserCollectionsFormSet = inlineformset_factory(User, models.UserCollections,
        form=UserCollectionsForm, extra=1, can_delete=True, formset=FirstFieldRequiredFormSet)

    if request.method == 'POST':
        userform = UserForm(request.POST, instance=user, prefix='user')
        userprofileformset = UserProfileFormSet(request.POST, instance=user, prefix='userprofile',)
        usercollectionsformset = UserCollectionsFormSet(request.POST, instance=user, prefix='usercollections',)

        if userform.is_valid() and userprofileformset.is_valid() and usercollectionsformset.is_valid():
            userform.save()
            userprofileformset.save()
            usercollectionsformset.save()

            messages.info(request, MSG_FORM_SAVED)
            return HttpResponseRedirect(reverse('user.index'))
        else:
            messages.error(request, MSG_FORM_MISSING)
    else:
        userform  = UserForm(instance=user, prefix='user')
        userprofileformset = UserProfileFormSet(instance=user, prefix='userprofile',)
        usercollectionsformset = UserCollectionsFormSet(instance=user, prefix='usercollections',)

    return render_to_response('journalmanager/add_user.html', {
                              'add_form': userform,
                              'mode': 'user_journal',
                              'user_name': request.user.pk,
                              'user_collections': user_collections,
                              'usercollectionsformset': usercollectionsformset,
                              'userprofileformset': userprofileformset
                              },
                              context_instance=RequestContext(request))

@login_required
def edit_journal_status(request, journal_id = None):
    """
    Handles Journal Status.

    Allow user just to update the status history of a specific journal.
    """

    user_collections = get_user_collections(request.user.id)

    # Always a new event. Considering that events must not be deleted or changed.
    journal_history = models.JournalPublicationEvents.objects.filter(journal = journal_id).order_by('-created_at')
    journal = get_object_or_404(models.Journal, id = journal_id)

    if request.method == "POST":
        journaleventform = EventJournalForm(request.POST)
        if journaleventform.is_valid():
            cleaned_data = journaleventform.cleaned_data
            journal.pub_status = cleaned_data["pub_status"]
            journal.pub_status_reason = cleaned_data["pub_status_reason"]
            journal.pub_status_changed_by = request.user
            journal.save()
            messages.info(request, MSG_FORM_SAVED)
            return HttpResponseRedirect(reverse('journal_status.edit', kwargs={'journal_id':journal_id}))
        else:
            messages.error(request, MSG_FORM_MISSING)
    else:
        journaleventform = EventJournalForm()

    return render_to_response('journalmanager/edit_journal_status.html', {
                              'add_form': journaleventform,
                              'user_collections': user_collections,
                              'journal_history': journal_history,
                              'journal': journal,
                              }, context_instance = RequestContext(request))

@login_required
def add_journal(request, journal_id = None):
    """
    Handles new and existing journals
    """

    user_collections = get_user_collections(request.user.id)

    if  journal_id is None:
        journal = models.Journal()
    else:
        journal = get_object_or_404(models.Journal, id = journal_id)

    form_hash = None

    JournalTitleFormSet = inlineformset_factory(models.Journal, models.JournalTitle, form=JournalTitleForm, extra=1, can_delete=True)
    JournalStudyAreaFormSet = inlineformset_factory(models.Journal, models.JournalStudyArea, form=JournalStudyAreaForm, extra=1, can_delete=True)
    JournalMissionFormSet = inlineformset_factory(models.Journal, models.JournalMission, form=JournalMissionForm, extra=1, can_delete=True)

    if request.method == "POST":
        journalform = JournalForm(request.POST,  request.FILES, instance=journal, prefix='journal', collections_qset=user_collections)
        studyareaformset = JournalStudyAreaFormSet(request.POST, instance=journal, prefix='studyarea')
        titleformset = JournalTitleFormSet(request.POST, instance=journal, prefix='title')
        missionformset = JournalMissionFormSet(request.POST, instance=journal, prefix='mission')

        if 'pend' in request.POST:
            journal_form_hash = PendingPostData(request.POST).pend(resolve(request.get_full_path()).url_name, request.user)
            form_hash = journal_form_hash
            messages.info(request, MSG_FORM_SAVED_PARTIALLY)
        else:
            if journalform.is_valid() and studyareaformset.is_valid() and titleformset.is_valid() \
                and missionformset.is_valid():
                journalform.save_all(creator = request.user)
                studyareaformset.save()
                titleformset.save()
                missionformset.save()
                messages.info(request, MSG_FORM_SAVED)

                if request.POST.get('form_hash', None) and request.POST['form_hash'] != 'None':
                    models.PendedForm.objects.get(form_hash=request.POST['form_hash']).delete()

                return HttpResponseRedirect(reverse('journal.index'))
            else:
                messages.error(request, MSG_FORM_MISSING)

    else:
        if request.GET.get('resume', None):
            pended_post_data = PendingPostData.resume(request.GET.get('resume'))

            journalform = JournalForm(pended_post_data,  request.FILES, instance=journal, prefix='journal', collections_qset=user_collections)
            studyareaformset = JournalStudyAreaFormSet(pended_post_data, instance=journal, prefix='studyarea')
            titleformset = JournalTitleFormSet(pended_post_data, instance=journal, prefix='title')
            missionformset = JournalMissionFormSet(pended_post_data, instance=journal, prefix='mission')
        else:
            journalform  = JournalForm(instance=journal, prefix='journal', collections_qset=user_collections)
            studyareaformset = JournalStudyAreaFormSet(instance=journal, prefix='studyarea')
            titleformset = JournalTitleFormSet(instance=journal, prefix='title')
            missionformset  = JournalMissionFormSet(instance=journal, prefix='mission')


    # Recovering Journal Cover url.
    try:
        has_cover_url = journal.cover.url
    except ValueError:
        has_cover_url = False

    return render_to_response('journalmanager/add_journal.html', {
                              'add_form': journalform,
                              'studyareaformset': studyareaformset,
                              'titleformset': titleformset,
                              'missionformset': missionformset,
                              'user_collections': user_collections,
                              'has_cover_url': has_cover_url,
                              'form_hash': form_hash if form_hash else request.GET.get('resume', None),
                              'is_new': False if journal_id else True,
                              }, context_instance = RequestContext(request))
@login_required
def del_pended(request, form_hash):
    pended_form = get_object_or_404(models.PendedForm, form_hash=form_hash, user=request.user)
    pended_form.delete()
    messages.info(request, MSG_DELETE_PENDED)
    return HttpResponseRedirect(reverse('index'))

@login_required
def add_sponsor(request, sponsor_id=None):
    """
    Handles new and existing sponsors
    """

    if  sponsor_id is None:
        sponsor = models.Sponsor()
    else:
        sponsor = get_object_or_404(models.Sponsor, id = sponsor_id)

    user_collections = get_user_collections(request.user.id)

    if request.method == "POST":
        sponsorform = SponsorForm(request.POST, instance=sponsor, prefix='sponsor',
            collections_qset=user_collections)

        if sponsorform.is_valid():
            newsponsorform = sponsorform.save()

            if request.POST.get('popup', 0):
                return HttpResponse('<script type="text/javascript">\
                    opener.updateSelect(window, "%s", "%s", "id_journal-sponsor");</script>' % \
                    (escape(newsponsorform.id), escape(newsponsorform)))

            messages.info(request, MSG_FORM_SAVED)
            return HttpResponseRedirect(reverse('sponsor.index'))
        else:
            messages.error(request, MSG_FORM_MISSING)
    else:
        sponsorform  = SponsorForm(instance=sponsor, prefix='sponsor',
            collections_qset=user_collections)

    return render_to_response('journalmanager/add_sponsor.html', {
                              'add_form': sponsorform,
                              'user_name': request.user.pk,
                              'user_collections': user_collections,
                              },
                              context_instance = RequestContext(request))

@login_required
def add_collection(request, collection_id=None):
    """
    Handles existing collections
    """

    user_collections = get_user_collections(request.user.id)

    if  collection_id is None:
        collection = models.Collection()
    else:
        collection = get_object_or_404(models.Collection, id = collection_id)

    if request.method == "POST":
        collectionform = CollectionForm(request.POST, request.FILES, instance=collection, prefix='collection')

        if collectionform.is_valid():
            collectionform.save()
            messages.info(request, MSG_FORM_SAVED)
            return HttpResponseRedirect(reverse('collection.edit',kwargs={'collection_id':collection_id}))
        else:
            messages.error(request, MSG_FORM_MISSING)
    else:
        collectionform  = CollectionForm(instance=collection, prefix='collection')

    try:
        collection_logo = collection.logo.url
    except ValueError:
        collection_logo = False

    return render_to_response('journalmanager/add_collection.html', {
                              'add_form': collectionform,
                              'collection_logo': collection_logo,
                              'user_name': request.user.pk,
                              'user_collections': user_collections,
                              },
                              context_instance = RequestContext(request))

@login_required
def add_publisher(request, publisher_id=None):
    """
    Handles new and existing publishers
    """

    if  publisher_id is None:
        publisher = models.Publisher()
    else:
        publisher = get_object_or_404(models.Publisher, id = publisher_id)

    user_collections = get_user_collections(request.user.id)

    if request.method == "POST":
        publisherform = PublisherForm(request.POST, instance=publisher, prefix='publisher',
            collections_qset=user_collections)

        if publisherform.is_valid():
            newpublisherform = publisherform.save()

            if request.POST.get('popup', 0):
                return HttpResponse('<script type="text/javascript">\
                    opener.updateSelect(window, "%s", "%s", "id_journal-publisher");</script>' % \
                    (escape(newpublisherform.id), escape(newpublisherform)))

            messages.info(request, MSG_FORM_SAVED)
            return HttpResponseRedirect(reverse('publisher.index'))
        else:
            messages.error(request, MSG_FORM_MISSING)
    else:
        publisherform  = PublisherForm(instance=publisher, prefix='publisher',
            collections_qset=user_collections)

    return render_to_response('journalmanager/add_publisher.html', {
                              'add_form': publisherform,
                              'user_name': request.user.pk,
                              'user_collections': user_collections,
                              },
                              context_instance = RequestContext(request))


@login_required
def add_issue(request, journal_id, issue_id=None):
    """
    Handles new and existing issues
    """

    user_collections = get_user_collections(request.user.id)
    journal = get_object_or_404(models.Journal, pk=journal_id)

    if issue_id is None:
        data_dict={'use_license': journal.use_license.id, 'editorial_standard': journal.editorial_standard, 'ctrl_vocabulary': journal.ctrl_vocabulary }
        issue = models.Issue()
    else:
        data_dict = None
        issue = models.Issue.objects.get(pk=issue_id)

    IssueTitleFormSet = inlineformset_factory(models.Issue, models.IssueTitle,
        form=IssueTitleForm, extra=1, can_delete=True, formset=FirstFieldRequiredFormSet)

    if request.method == 'POST':
        add_form = IssueForm(request.POST,  request.FILES, journal_id=journal.pk, instance=issue)
        titleformset = IssueTitleFormSet(request.POST, instance=issue, prefix='title')

        if add_form.is_valid() and titleformset.is_valid():
            add_form.save_all(journal)
            titleformset.save()
            messages.info(request, MSG_FORM_SAVED)
            return HttpResponseRedirect(reverse('issue.index', args=[journal_id]))
        else:
            messages.error(request, MSG_FORM_MISSING)
    else:
        add_form = IssueForm(journal_id=journal.pk, instance=issue, initial=data_dict)
        titleformset = IssueTitleFormSet(instance=issue, prefix='title')

    # Recovering Journal Cover url.
    try:
        has_cover_url = issue.cover.url
    except ValueError:
        has_cover_url = False

    return render_to_response('journalmanager/add_issue.html', {
                              'add_form': add_form,
                              'journal': journal,
                              'titleformset': titleformset,
                              'user_name': request.user.pk,
                              'user_collections': user_collections,
                              'has_cover_url': has_cover_url,
                              },
                              context_instance = RequestContext(request))

@login_required
def publisher_index(request):
    user_collections = get_user_collections(request.user.id)
    default_collections = user_collections.filter(is_default = True)

    all_publishers = models.Publisher.objects.available(request.GET.get('is_available', 1))
    publishers = get_paginated(all_publishers, request.GET.get('page', 1))

    t = loader.get_template('journalmanager/publisher_dashboard.html')
    c = RequestContext(request, {
                       'objects_publisher': publishers,
                       'user_collections': user_collections,
                       })
    return HttpResponse(t.render(c))

@login_required
def add_section(request, journal_id, section_id=None):
    """
    Handles new and existing sections
    """

    if section_id is None:
        section = models.Section()
        has_relation = False
    else:
        section = get_object_or_404(models.Section, pk=section_id)
        has_relation = section_has_relation(section.id)

    journal = get_object_or_404(models.Journal, pk=journal_id)
    SectionTitleFormSet = inlineformset_factory(models.Section, models.SectionTitle,
        form=SectionTitleForm, extra=2, can_delete=False, formset=FirstFieldRequiredFormSet)

    SectionTitleFormSet.form = staticmethod(curry(SectionTitleForm, journal=journal))

    if request.method == 'POST':

        add_form = SectionForm(request.POST, instance=section)
        section_title_formset = SectionTitleFormSet(request.POST, instance=section, prefix='titles')

        if add_form.is_valid() and section_title_formset.is_valid():
            add_form.save_all(journal)
            section_title_formset.save()
            messages.info(request, MSG_FORM_SAVED)
            return HttpResponseRedirect(reverse('section.index', args=[journal_id]))
        else:
            messages.error(request, MSG_FORM_MISSING)

    else:
        add_form = SectionForm(instance=section)
        section_title_formset = SectionTitleFormSet(instance=section, prefix='titles')

    return render_to_response('journalmanager/add_section.html', {
                              'add_form': add_form,
                              'section_title_formset': section_title_formset,
                              'user_name': request.user.pk,
                              'journal': journal,
                              'has_relation': has_relation,
                              },
                              context_instance = RequestContext(request))

@login_required
def del_section(request, journal_id, section_id):

    journal = get_object_or_404(models.Journal, pk=journal_id)

    if not section_has_relation(section_id):
        sec = models.Section.objects.get(pk=section_id)
        sec.is_trashed = True
        sec.save()
        messages.success(request, MSG_FORM_SAVED)
        return HttpResponseRedirect(reverse('section.index', args=[journal_id]))
    else:
        messages.info(request, _('Cant\'t delete, some issues are using this Section'))
        return HttpResponseRedirect(reverse('section.index', args=[journal_id]))

@login_required
def toggle_user_availability(request, user_id):

  if request.is_ajax():

    user = get_object_or_404(models.User, pk = user_id)
    user.is_active = not user.is_active
    user.save()

    response_data = json.dumps({
      "result": str(user.is_active),
      "object_id": user.id
      })

    #ajax response json
    return HttpResponse(response_data, mimetype="application/json")
  else:
    #bad request
    return HttpResponse(status=400)

@login_required
def my_account(request):
    t = loader.get_template('journalmanager/my_account.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

@login_required
def password_change(request):

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            if cleaned_data['new_password'] != cleaned_data['new_password_again']:
                messages.error(request, _('Your new password and new password confirmation must match.'))
                return HttpResponseRedirect(reverse('journalmanager.password_change'))

            auth_user = authenticate(username=request.user.username,
                                     password=cleaned_data['password'])
            if auth_user:
                auth_user.set_password(cleaned_data['new_password'])
                auth_user.save()
            else:
                messages.error(request, _('Your current password does not match. Please try again.'))
                return HttpResponseRedirect(reverse('journalmanager.password_change'))

            messages.info(request, _('Your new password has been set.'))
            return HttpResponseRedirect(reverse('journalmanager.my_account'))
    else:
        form = PasswordChangeForm()

    return render_to_response(
        'journalmanager/password_change.html',
        {'form': form},
        context_instance = RequestContext(request))

@login_required
def trash_listing(request):
    user_collections = get_user_collections(request.user.id)

    listing_ref = {
        'journal': models.Journal,
        'section': models.Section,
        'sponsor': models.Sponsor,
        'publisher': models.Publisher,
    }

    if request.GET.get('show', None) in listing_ref:
        doc_entity = listing_ref[request.GET['show']]
    else:
        doc_entity = models.Journal

    try:
        trashed_docs = doc_entity.objects.all_by_user(request.user, is_available=False)
    except AttributeError:
        trashed_docs = models.Journal.objects.all_by_user(request.user, is_available=False)
        #log the event

    trashed_docs_paginated = get_paginated(trashed_docs, request.GET.get('page', 1))

    return render_to_response(
        'journalmanager/trash_listing.html',
        {'trashed_docs': trashed_docs_paginated, 'user_collections': user_collections},
        context_instance = RequestContext(request))
