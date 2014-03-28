import json
import urlparse
from datetime import datetime

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.urlresolvers import resolve
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import loader
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils.functional import curry
from django.utils.html import escape
from django.forms.models import inlineformset_factory
from django.conf import settings

from . import models
from .forms import *
from scielomanager.utils.pendingform import PendingPostData
from scielomanager.tools import (
    get_paginated,
    get_referer_view,
    asbool,
)


from waffle.decorators import waffle_flag

AUTHZ_REDIRECT_URL = '/accounts/unauthorized/'
MSG_FORM_SAVED = _('Saved.')
MSG_FORM_SAVED_PARTIALLY = _('Saved partially. You can continue to fill in this form later.')
MSG_FORM_MISSING = _('There are some errors or missing data.')
MSG_DELETE_PENDED = _('The pended form has been deleted.')


def get_first_letter(objects_all):
    """
    Returns a set of first letters from names in `objects_all`
    """
    letters_set = set(unicode(letter)[0].upper().strip() for letter in objects_all)

    return sorted(list(letters_set))


def index(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('journalmanager.user_login'))

    if 'editor' in [i.name.lower() for i in request.user.groups.all()]:
        landing_page = 'journalmanager/home_editor.html'
        editor_journals = request.user.user_editors.all()
        context = {'editor_journals': editor_journals}
    else:
        pending_journals = models.PendedForm.objects.filter(
            user=request.user.id).filter(view_name='journal.add').order_by('-created_at')

        # recent activities
        recent_journals = models.Journal.objects.recents_by_user(request.user)

        context = {
            'pending_journals': pending_journals,
            'recent_activities': recent_journals,
        }

        landing_page = 'journalmanager/home_journal.html'
    return render_to_response(landing_page,
        context, context_instance=RequestContext(request))


def list_search(request, model, journal_id):
    """
    Generic list and search
    """
    if journal_id:
        journal = models.Journal.objects.get(pk=journal_id)
        objects_all = model.objects.filter(journal=journal_id)

        if model is models.Section:
            # order by a non persistent property
            objects_all = model.objects.filter(journal=journal_id, is_trashed=False)
            objects_all = sorted(objects_all, key=lambda x: unicode(x))
    else:
        journal = None
        objects_all = model.objects.all_by_user(request.user)

        #filtering by pub_status is only available to Journal instances.
        if model is models.Journal and request.GET.get('jstatus'):
            objects_all = objects_all.filter(pub_status=request.GET['jstatus'])

        if request.GET.get('letter'):
            if issubclass(model, models.Institution):
                objects_all = objects_all.filter(name__startswith=request.GET.get('letter'))
            else:
                objects_all = objects_all.filter(title__startswith=request.GET.get('letter'))

    if request.GET.get('q'):
        objects_all = model.objects.all_by_user(request.user)

        if issubclass(model, models.Institution):
            objects_all = objects_all.filter(
                name__icontains=request.REQUEST['q']).order_by('name')
        else:
            objects_all = objects_all.filter(
                title__icontains=request.REQUEST['q']).order_by('title')

    objects = get_paginated(objects_all, request.GET.get('page', 1))
    template_name = 'journalmanager/%s_list.html' % model.__name__.lower()

    return render_to_response(
        template_name, {
           'objects_%s' % model.__name__.lower(): objects,
           'journal': journal,
           'letters': get_first_letter(objects_all),
        },
        context_instance=RequestContext(request))


@permission_required('journalmanager.list_article', login_url=AUTHZ_REDIRECT_URL)
def article_index(request, issue_id):

    issue = get_object_or_404(models.Issue, pk=issue_id)

    return render_to_response(
        'journalmanager/article_list.html',
        {
            'journal': issue.journal,
            'issue': issue,
            'articles': issue.articles.all()
        },
        context_instance=RequestContext(request)
    )


@permission_required('journalmanager.list_issue', login_url=AUTHZ_REDIRECT_URL)
def issue_index(request, journal_id):
    journal = get_object_or_404(models.Journal, pk=journal_id)

    current_year = datetime.now().year
    previous_year = current_year - 1

    if request.method == 'POST':
        aheadform = AheadForm(request.POST, instance=journal, prefix='journal')
        if aheadform.is_valid():
            aheadform.save()
        else:
            messages.error(request, MSG_FORM_MISSING)
    else:
        aheadform = AheadForm(instance=journal, prefix='journal')

    return render_to_response(
        'journalmanager/issue_list.html',
        {
            'journal': journal,
            'aheadform': aheadform,
            'current_year': current_year,
            'previous_year': previous_year,
            'issue_grid': journal.issues_as_grid(
                request.GET.get('is_available')
            ),
        },
        context_instance=RequestContext(request)
    )


@permission_required('journalmanager.list_journal', login_url=AUTHZ_REDIRECT_URL)
def journal_index(request, model, journal_id=None):
    """
    Journal list and search
    """
    return list_search(request, model, journal_id)


@permission_required('journalmanager.list_sponsor', login_url=AUTHZ_REDIRECT_URL)
def sponsor_index(request, model, journal_id=None):
    """
    Sponsor list and search
    """
    return list_search(request, model, journal_id)


@permission_required('journalmanager.list_section', login_url=AUTHZ_REDIRECT_URL)
def section_index(request, model, journal_id=None):
    """
    Section list and search
    """
    return list_search(request, model, journal_id)


@permission_required('journalmanager.list_collection', login_url=AUTHZ_REDIRECT_URL)
def collection_index(request, model, journal_id=None):
    """
    Collection list and search
    """
    return list_search(request, model, journal_id)


@permission_required('journalmanager.list_pressrelease', login_url=AUTHZ_REDIRECT_URL)
def pressrelease_index(request, journal_id):
    journal = get_object_or_404(models.Journal, pk=journal_id)

    param_tab = request.GET.get('tab')
    pr_model = models.AheadPressRelease if param_tab == 'ahead' else models.RegularPressRelease

    preleases = pr_model.userobjects.active().journal(journal).select_related()
    objects = get_paginated(preleases, request.GET.get('page', 1))

    return render_to_response(
        'journalmanager/pressrelease_list.html',
        {
           'objects_pr': objects,
           'journal': journal,
        },
        context_instance=RequestContext(request))


@login_required
def generic_toggle_availability(request, object_id, model):

    if request.is_ajax():

        model = get_object_or_404(model, pk=object_id)
        model.is_trashed = not model.is_trashed
        model.save()

        return HttpResponse(mimetype="application/json")
    else:
        return HttpResponse(status=400)


@login_required
def toggle_active_collection(request, user_id, collection_id):
    '''
    Redefine the active collection, changing the administrative context to another collection.
    '''

    # Setting up all user collections.is_default to False
    user_collections = models.get_user_collections(request.user.id)

    # Clear cache when changes in UserCollections
    invalid = [collection for collection in user_collections]
    models.UserCollections.objects.invalidate(*invalid)

    collection = get_object_or_404(models.Collection, pk=collection_id)
    collection.make_default_to_user(request.user)

    referer = get_referer_view(request)

    return HttpResponseRedirect(referer)


@login_required
def generic_bulk_action(request, model_name, action_name, value=None):
    info_msg = None
    MSG_MOVED = _('The selected documents had been moved to the Trash.')
    MSG_RESTORED = _('The selected documents had been restored.')

    model_refs = {
        'journal': models.Journal,
        'section': models.Section,
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
                    if not doc.is_used():
                        doc.is_trashed = True if int(value) == 0 else False
                        doc.save()
                        info_msg = MSG_MOVED if doc.is_trashed else MSG_RESTORED
                elif isinstance(doc, models.Institution):
                    doc.is_trashed = True if int(value) == 0 else False
                    doc.save()
                    info_msg = MSG_MOVED if doc.is_trashed else MSG_RESTORED

    if info_msg:
        messages.info(request, info_msg)
    return HttpResponseRedirect(get_referer_view(request))


@permission_required('auth.change_user', login_url=AUTHZ_REDIRECT_URL)
def user_index(request):

    collection = models.Collection.objects.get_default_by_user(request.user)

    if not collection.is_managed_by_user(request.user):
        return HttpResponseRedirect(AUTHZ_REDIRECT_URL)

    col_users = models.User.objects.filter(
        usercollections__collection__in=[collection]).distinct('username').order_by('username')

    users = get_paginated(col_users, request.GET.get('page', 1))

    t = loader.get_template('journalmanager/user_list.html')
    c = RequestContext(request, {
                       'users': users,
                       })
    return HttpResponse(t.render(c))


@permission_required('auth.change_user', login_url=AUTHZ_REDIRECT_URL)
def add_user(request, user_id=None):
    """
    Handles new and existing users
    """
    collection = models.Collection.objects.get_default_by_user(request.user)

    if not collection.is_managed_by_user(request.user):
        return HttpResponseRedirect(AUTHZ_REDIRECT_URL)

    if user_id == None:
        user = User()
    else:
        user = get_object_or_404(User, id=user_id)

    # Getting Collections from the logged user.
    user_collections = models.get_user_collections(request.user.id)

    UserProfileFormSet = inlineformset_factory(User, models.UserProfile, )
    UserCollectionsFormSet = inlineformset_factory(User, models.UserCollections,
        form=UserCollectionsForm, extra=1, can_delete=True, formset=FirstFieldRequiredFormSet)

    # filter the collections the user is manager.
    UserCollectionsFormSet.form = staticmethod(curry(UserCollectionsForm, user=request.user))

    if request.method == 'POST':
        userform = UserForm(request.POST, instance=user, prefix='user')
        userprofileformset = UserProfileFormSet(request.POST, instance=user, prefix='userprofile',)
        usercollectionsformset = UserCollectionsFormSet(request.POST, instance=user, prefix='usercollections',)

        if userform.is_valid() and userprofileformset.is_valid() and usercollectionsformset.is_valid():
            new_user = userform.save()
            userprofileformset.save()

            # Clear cache when changes in UserCollections
            invalid = [collection for collection in user_collections]
            models.UserCollections.objects.invalidate(*invalid)

            usercollectionsformset.save()

            # if it is a new user, mail him
            # requesting for password change
            if not user_id:
                password_form = auth_forms.PasswordResetForm({'email': new_user.email})
                if password_form.is_valid():
                    opts = {
                        'use_https': request.is_secure(),
                        'request': request,
                    }
                    password_form.save(**opts)

            messages.info(request, MSG_FORM_SAVED)
            return HttpResponseRedirect(reverse('user.index'))
        else:
            messages.error(request, MSG_FORM_MISSING)
    else:
        userform = UserForm(instance=user, prefix='user')
        userprofileformset = UserProfileFormSet(instance=user, prefix='userprofile',)
        usercollectionsformset = UserCollectionsFormSet(instance=user, prefix='usercollections',)

    return render_to_response('journalmanager/add_user.html', {
                              'add_form': userform,
                              'mode': 'user_journal',
                              'user_name': request.user.pk,
                              'usercollectionsformset': usercollectionsformset,
                              'userprofileformset': userprofileformset
                              },
                              context_instance=RequestContext(request))


@permission_required('journalmanager.list_publication_events', login_url=AUTHZ_REDIRECT_URL)
def edit_journal_status(request, journal_id=None):
    """
    Handles Journal Status.

    Allow user just to update the status history of a specific journal.
    """
    # Always a new event. Considering that events must not be deleted or changed.
    journal_history = models.JournalPublicationEvents.objects.filter(journal=journal_id).order_by('-created_at')
    journal = get_object_or_404(models.Journal, id=journal_id)

    if request.method == "POST":
        journaleventform = EventJournalForm(request.POST)

        if journaleventform.is_valid():
            cleaned_data = journaleventform.cleaned_data
            journal.change_publication_status(cleaned_data["pub_status"],
                cleaned_data["pub_status_reason"], request.user)

            messages.info(request, MSG_FORM_SAVED)
            return HttpResponseRedirect(reverse(
                'journal_status.edit', kwargs={'journal_id': journal_id}))
        else:
            messages.error(request, MSG_FORM_MISSING)
    else:
        journaleventform = EventJournalForm()

    return render_to_response('journalmanager/edit_journal_status.html', {
                              'add_form': journaleventform,
                              'journal_history': journal_history,
                              'journal': journal,
                              }, context_instance=RequestContext(request))


@waffle_flag('editor_manager')
@permission_required('journalmanager.list_editor_journal', login_url=AUTHZ_REDIRECT_URL)
def editor_journal(request):
    """
    Initial editor page, containing a list of all journals related to the user.
    """
    editor_journals = request.user.user_editors.all()

    return render_to_response('journalmanager/home_editor.html', {
                              'editor_journals': editor_journals,
                              }, context_instance=RequestContext(request))


@waffle_flag('editor_manager')
@permission_required('journalmanager.list_journal', login_url=AUTHZ_REDIRECT_URL)
def journal_editors(request, journal_id=None):
    """
    Handle the users that have an editor profile for a specific journal
    """

    journal = get_object_or_404(models.Journal, id=journal_id)
    editors = journal.editors.all()

    return render_to_response('journalmanager/journal_editors_list.html', {
                              'journal': journal,
                              'editors': editors,
                              }, context_instance=RequestContext(request))


@waffle_flag('editor_manager')
@permission_required('journalmanager.change_journal', login_url=AUTHZ_REDIRECT_URL)
def journal_editors_add(request, journal_id):

    journal = get_object_or_404(models.Journal, pk=journal_id)

    if request.method == 'POST':
        username = request.POST.get('query')
        try:
            user = User.objects.get(username=username)
            try:
                journal.editors.add(user)
                messages.error(request, _('Now, %s is an editor of this journal.' % user.username))
            except IntegrityError:
                messages.error(request, _('%s is already an editor of this journal.' % user.username))
        except ObjectDoesNotExist:
            messages.error(request, _('User %s does not exists' % username))

    editors = journal.editors.all()

    t = loader.get_template('journalmanager/journal_editors_list.html')
    c = RequestContext(request, {
                       'journal': journal,
                       'editors': editors,
                       })
    return HttpResponse(t.render(c))


@waffle_flag('editor_manager')
@permission_required('journalmanager.change_journal', login_url=AUTHZ_REDIRECT_URL)
def journal_editors_remove(request, journal_id, user_id):

    journal = models.Journal.objects.get(pk=journal_id)
    user2remove = models.User.objects.get(pk=user_id)

    journal.editors.remove(user2remove)

    messages.error(request, _('The user %s was removed from this journal.' % user2remove.username))

    editors = journal.editors.all()

    t = loader.get_template('journalmanager/journal_editors_list.html')
    c = RequestContext(request, {
                       'journal': journal,
                       'editors': editors,
                       })
    return HttpResponse(t.render(c))


@waffle_flag('editor_manager')
@permission_required('journalmanager.list_editor_journal', login_url=AUTHZ_REDIRECT_URL)
def dash_editor_journal(request, journal_id=None):
    """
    Handles new and existing journals
    """

    journal = get_object_or_404(models.Journal, id=journal_id)

    return render_to_response('journalmanager/journal_dash.html', {
                              'journal': journal,
                              }, context_instance=RequestContext(request))


@permission_required('journalmanager.list_journal', login_url=AUTHZ_REDIRECT_URL)
def dash_journal(request, journal_id=None):
    """
    Handles new and existing journals
    """

    journal = get_object_or_404(models.Journal, id=journal_id)

    return render_to_response('journalmanager/journal_dash.html', {
                              'journal': journal,
                              }, context_instance=RequestContext(request))


@permission_required('journalmanager.change_journal', login_url=AUTHZ_REDIRECT_URL)
def add_journal(request, journal_id=None):
    """
    Handles new and existing journals
    """

    user_collections = models.get_user_collections(request.user.id)

    if journal_id is None:
        journal = models.Journal()
    else:
        journal = get_object_or_404(models.Journal, id=journal_id)

    form_hash = None

    JournalTitleFormSet = inlineformset_factory(models.Journal, models.JournalTitle, form=JournalTitleForm, extra=1, can_delete=True)
    JournalMissionFormSet = inlineformset_factory(models.Journal, models.JournalMission, form=JournalMissionForm, extra=1, can_delete=True)

    if request.method == "POST":
        journalform = JournalForm(request.POST,  request.FILES, instance=journal, prefix='journal', collections_qset=user_collections)
        titleformset = JournalTitleFormSet(request.POST, instance=journal, prefix='title')
        missionformset = JournalMissionFormSet(request.POST, instance=journal, prefix='mission')

        if 'pend' in request.POST:
            journal_form_hash = PendingPostData(request.POST).pend(resolve(request.get_full_path()).url_name, request.user)
            form_hash = journal_form_hash
            messages.info(request, MSG_FORM_SAVED_PARTIALLY)
        else:

            if journalform.is_valid() and titleformset.is_valid() and missionformset.is_valid():
                saved_journal = journalform.save_all(creator=request.user)
                titleformset.save()
                missionformset.save()
                messages.info(request, MSG_FORM_SAVED)

                if request.POST.get('form_hash', None) and request.POST['form_hash'] != 'None':
                    models.PendedForm.objects.get(form_hash=request.POST['form_hash']).delete()

                # record the event
                models.DataChangeEvent.objects.create(
                    user=request.user,
                    content_object=saved_journal,
                    collection=models.Collection.objects.get_default_by_user(request.user),
                    event_type='updated' if journal_id else 'added'
                )
                return HttpResponseRedirect(reverse('journal.dash', args=[saved_journal.id]))
            else:
                messages.error(request, MSG_FORM_MISSING)

    else:
        if request.GET.get('resume', None):
            pended_post_data = PendingPostData.resume(request.GET.get('resume'))

            journalform = JournalForm(pended_post_data,  request.FILES, instance=journal, prefix='journal', collections_qset=user_collections)
            titleformset = JournalTitleFormSet(pended_post_data, instance=journal, prefix='title')
            missionformset = JournalMissionFormSet(pended_post_data, instance=journal, prefix='mission')
        else:
            journalform = JournalForm(instance=journal, prefix='journal', collections_qset=user_collections)
            titleformset = JournalTitleFormSet(instance=journal, prefix='title')
            missionformset = JournalMissionFormSet(instance=journal, prefix='mission')

    # Recovering Journal Cover url.
    try:
        has_cover_url = journal.cover.url
    except ValueError:
        has_cover_url = False

    # Recovering Journal Logo url.
    try:
        has_logo_url = journal.logo.url
    except ValueError:
        has_logo_url = False

    return render_to_response('journalmanager/add_journal.html', {
                              'journal': journal,
                              'add_form': journalform,
                              'titleformset': titleformset,
                              'missionformset': missionformset,
                              'has_cover_url': has_cover_url,
                              'has_logo_url': has_logo_url,
                              'form_hash': form_hash if form_hash else request.GET.get('resume', None),
                              'is_new': False if journal_id else True,
                              }, context_instance=RequestContext(request))


@login_required
def del_pended(request, form_hash):
    pended_form = get_object_or_404(models.PendedForm, form_hash=form_hash, user=request.user)
    pended_form.delete()
    messages.info(request, MSG_DELETE_PENDED)
    return HttpResponseRedirect(reverse('index'))


@permission_required('journalmanager.add_sponsor', login_url=AUTHZ_REDIRECT_URL)
def add_sponsor(request, sponsor_id=None):
    """
    Handles new and existing sponsors
    """

    if  sponsor_id is None:
        sponsor = models.Sponsor()
    else:
        sponsor = get_object_or_404(models.Sponsor.objects.all_by_user(request.user), id=sponsor_id)

    user_collections = models.get_user_collections(request.user.id)

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
        sponsorform = SponsorForm(instance=sponsor, prefix='sponsor',
            collections_qset=user_collections)

    return render_to_response('journalmanager/add_sponsor.html', {
                              'add_form': sponsorform,
                              'user_name': request.user.pk,
                              },
                              context_instance=RequestContext(request))


@permission_required('journalmanager.change_collection', login_url=AUTHZ_REDIRECT_URL)
def add_collection(request, collection_id):
    """
    Handles existing collections
    """

    collection = get_object_or_404(models.Collection, id=collection_id)

    if not collection.is_managed_by_user(request.user):
        return HttpResponseRedirect(AUTHZ_REDIRECT_URL)

    if request.method == "POST":
        collectionform = CollectionForm(request.POST, request.FILES, instance=collection, prefix='collection')

        if collectionform.is_valid():
            collectionform.save()
            messages.info(request, MSG_FORM_SAVED)
            return HttpResponseRedirect(reverse('collection.edit', kwargs={'collection_id': collection_id}))
        else:
            messages.error(request, MSG_FORM_MISSING)
    else:
        collectionform = CollectionForm(instance=collection, prefix='collection')

    try:
        collection_logo = collection.logo.url
    except ValueError:
        collection_logo = False

    return render_to_response('journalmanager/add_collection.html', {
                              'add_form': collectionform,
                              'collection_logo': collection_logo,
                              'user_name': request.user.pk,
                              },
                              context_instance=RequestContext(request))


@permission_required('journalmanager.add_issue', login_url=AUTHZ_REDIRECT_URL)
def edit_issue(request, journal_id, issue_id=None):
    """
    Handles edition of existing issues
    """

    def get_issue_form_by_type(issue_type, request, journal, instance):
        """
            This method is useful to get the correct IssueForm based on issue_type.
        """
        form_kwargs = {
            'params' : {
                'journal': journal,
            },
            'querysets' : {
                'section': journal.section_set.all(),
                'use_license': models.UseLicense.objects.all(),
            },
            'instance' : instance,
        }
        
        form_args = []
        if request.method == 'POST':
            form_args.append(request.POST)
            form_args.append(request.FILES)
        else:
            initial = issue.__dict__
            initial['suppl_type'] = issue.suppl_type if issue.type == 'supplement' else None
            initial['use_license'] = issue.use_license
            initial['section'] = issue.section.all()
            initial['journal'] = issue.journal
            form_kwargs['initial'] = initial

        if issue_type == 'supplement':
            return SupplementIssueForm(*form_args, **form_kwargs)
        elif issue_type == 'special':
            return SpecialIssueForm(*form_args, **form_kwargs)
        else: # issue_type == 'regular':
            return RegularIssueForm(*form_args, **form_kwargs)

    issue = models.Issue.objects.get(pk=issue_id)

    IssueTitleFormSet = inlineformset_factory(models.Issue, models.IssueTitle,
                                              form=IssueTitleForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = get_issue_form_by_type(issue.type, request, issue.journal, issue)
        titleformset = IssueTitleFormSet(request.POST, instance=issue, prefix='title')

        if form.is_valid():
            saved_issue = form.save(commit=False)
            saved_issue.journal = issue.journal
            saved_issue.save()
            form.save_m2m()

            if titleformset.is_valid():
                titleformset.save()

            messages.info(request, MSG_FORM_SAVED)

            # record the event
            models.DataChangeEvent.objects.create(
                user=request.user,
                content_object=saved_issue,
                collection=models.Collection.objects.get_default_by_user(request.user),
                event_type='updated'
            )

            return HttpResponseRedirect(reverse('issue.index', args=[journal_id]))
        else:
            messages.error(request, MSG_FORM_MISSING)
    else:
        form = get_issue_form_by_type(issue.type, request, issue.journal, issue)
        titleformset = IssueTitleFormSet(instance=issue, prefix='title')

    # Recovering Journal Cover url.
    try:
        has_cover_url = issue.cover.url
    except ValueError:
        has_cover_url = False

    # variable names are add_form, and add_issue_xxx is that way to re-use the template
    return render_to_response('journalmanager/add_issue_%s.html' % issue.type, {
                              'add_form': form,
                              'issue_type': issue.type,
                              'journal': issue.journal,
                              'titleformset': titleformset,
                              'user_name': request.user.pk,
                              'has_cover_url': has_cover_url,
                              },
                              context_instance=RequestContext(request))


@permission_required('journalmanager.add_issue', login_url=AUTHZ_REDIRECT_URL)
def add_issue(request, issue_type, journal_id, issue_id=None):
    """
    Handles new and existing issues
    """

    def get_issue_form_by_type(issue_type, request, journal, instance=None, initial=None):
        """
            This method is useful to get the correct IssueForm based on issue_type.
            if initial == None then the request.POST and request.FILES is used to fill the form.
            if initial != None then the form is used in a GET request.
        """
        form_kwargs = {
            'params' : {
                'journal': journal,
            },
            'querysets' : {
                'section': journal.section_set.all(),
                'use_license': models.UseLicense.objects.all(),
            },
            'instance' : instance,
            'initial' : initial,
        }
        form_args = []
        if initial is None:
            form_args.append(request.POST)
            form_args.append(request.FILES)
        if issue_type == 'supplement':
            return SupplementIssueForm(*form_args, **form_kwargs)
        elif issue_type == 'special':
            return SpecialIssueForm(*form_args, **form_kwargs)
        else: # issue_type == 'regular':
            return RegularIssueForm(*form_args, **form_kwargs)

    journal = get_object_or_404(models.Journal.objects.all_by_user(request.user), pk=journal_id)

    if issue_id is None:
        data_dict = {'use_license': journal.use_license.id,
                     'editorial_standard': journal.editorial_standard,
                     'ctrl_vocabulary': journal.ctrl_vocabulary}
        issue = models.Issue()
    else:
        data_dict = None
        issue = models.Issue.objects.get(pk=issue_id)

    IssueTitleFormSet = inlineformset_factory(models.Issue, models.IssueTitle,
                                              form=IssueTitleForm, extra=1, can_delete=True)

    if request.method == 'POST':
        add_form = get_issue_form_by_type(issue_type, request, journal, instance=issue)
        titleformset = IssueTitleFormSet(request.POST, instance=issue, prefix='title')

        if add_form.is_valid():
            saved_issue = add_form.save(commit=False)
            saved_issue.journal = journal
            saved_issue.type = issue_type
            saved_issue.save()
            add_form.save_m2m()
            # the backward relation is created only
            # if title is given.
            if titleformset.is_valid():
                titleformset.save()

            messages.info(request, MSG_FORM_SAVED)

            # record the event
            models.DataChangeEvent.objects.create(
                user=request.user,
                content_object=saved_issue,
                collection=models.Collection.objects.get_default_by_user(request.user),
                event_type='added'
            )

            return HttpResponseRedirect(reverse('issue.index', args=[journal_id]))
        else:
            messages.error(request, MSG_FORM_MISSING)
    else:
        add_form = get_issue_form_by_type(issue_type, request, journal, instance=issue, initial=data_dict)
        titleformset = IssueTitleFormSet(instance=issue, prefix='title')

    # Recovering Journal Cover url.
    try:
        has_cover_url = issue.cover.url
    except ValueError:
        has_cover_url = False
    return render_to_response('journalmanager/add_issue_%s.html' % issue_type, {
                              'add_form': add_form,
                              'issue_type': issue_type,
                              'journal': journal,
                              'titleformset': titleformset,
                              'user_name': request.user.pk,
                              'has_cover_url': has_cover_url,
                              },
                              context_instance=RequestContext(request))


@permission_required('journalmanager.reorder_issue', login_url=AUTHZ_REDIRECT_URL)
def issue_reorder(request, journal_id):
    """
    Handles issues reordering based on ajax interactions.
    """
    def _parse_data(data):
        """
        Parses the incoming request.GET::

            ``numbers=num%5B%5D%3D8036%26num%5B%5D%3D8035&issues_set=numbers-2005%7CNone``

        Returns::

            ``({'year': 2005, 'vol': None}, [8036, 8035])``
        """
        issues_set = {}

        parsed_data = urlparse.parse_qs(data.urlencode())
        splitted_issues_set = parsed_data['issues_set'][0].split('|')

        issues_set['year'] = splitted_issues_set[0][-4:]

        if 'None' in splitted_issues_set[1]:
            issues_set['vol'] = None
        else:
            issues_set['vol'] = splitted_issues_set[1]

        numbers = urlparse.parse_qs(parsed_data['numbers'][0]).get('num[]', [])

        return issues_set, numbers

    # here starts the actual view code. sorry.
    if request.is_ajax():
        if not request.GET:
            return HttpResponse(status=500)

        journal = get_object_or_404(models.Journal, pk=journal_id)
        issues_set, numbers = _parse_data(request.GET)

        if not journal.has_issues(numbers):
            return HttpResponse(status=500)

        # check if the user has privileges in this journal
        journal.reorder_issues(numbers,
            publication_year=issues_set['year'], volume=issues_set['vol'])

    return HttpResponse(status=200)


@permission_required('journalmanager.change_section', login_url=AUTHZ_REDIRECT_URL)
def add_section(request, journal_id, section_id=None):
    """
    Handles new and existing sections
    """
    journal = get_object_or_404(
        models.Journal.objects.all_by_user(request.user), pk=journal_id)

    if section_id is None:
        section = models.Section()
        has_relation = False
    else:
        section = get_object_or_404(models.Section, pk=section_id)
        has_relation = section.is_used()

    all_forms = get_all_section_forms(request.POST, journal, section)

    add_form = all_forms['section_form']
    section_title_formset = all_forms['section_title_formset']

    if request.method == 'POST':

        if add_form.is_valid() and section_title_formset.is_valid():
            add_form = add_form.save_all(journal)
            section_title_formset.save()

            if request.POST.get('popup', 0):
                return HttpResponse('<script type="text/javascript">\
                    opener.updateSelect(window, "%s", "%s", "id_section");</script>' % \
                    (escape(add_form.id), escape(add_form)))

            messages.info(request, MSG_FORM_SAVED)
            return HttpResponseRedirect(reverse('section.index', args=[journal_id]))
        else:
            messages.error(request, MSG_FORM_MISSING)

    return render_to_response('journalmanager/add_section.html', {
                              'add_form': add_form,
                              'section_title_formset': section_title_formset,
                              'user_name': request.user.pk,
                              'journal': journal,
                              'has_relation': has_relation,
                              }, context_instance=RequestContext(request))


@permission_required('journalmanager.delete_section', login_url=AUTHZ_REDIRECT_URL)
def del_section(request, journal_id, section_id):
    section = get_object_or_404(models.Section, pk=section_id)

    if not section.is_used():
        section.is_trashed = True
        section.save()
        messages.success(request, _('Section removed successfully'))
    else:
        messages.info(
            request,
            _('Cant\'t delete, some issues are using this Section')
        )

    return HttpResponseRedirect(
        reverse('section.index', args=[section.journal.id])
    )


@login_required
def toggle_user_availability(request, user_id):

    if request.is_ajax():
        user = get_object_or_404(models.User, pk=user_id)
        user.is_active = not user.is_active
        user.save()

        response_data = json.dumps({
          "result": str(user.is_active),
          "object_id": user.id
          })

        return HttpResponse(response_data, mimetype="application/json")
    else:
        return HttpResponse(status=400)


@login_required
def trash_listing(request):
    listing_ref = {
        'journal': models.Journal,
        'section': models.Section,
        'sponsor': models.Sponsor,
    }

    if request.GET.get('show', None) in listing_ref:
        doc_entity = listing_ref[request.GET['show']]
    else:
        doc_entity = models.Journal

    try:
        trashed_docs = doc_entity.objects.all_by_user(request.user, is_available=False)
    except AttributeError:
        trashed_docs = models.Journal.objects.all_by_user(request.user, is_available=False)

    trashed_docs_paginated = get_paginated(trashed_docs, request.GET.get('page', 1))

    return render_to_response(
        'journalmanager/trash_listing.html',
        {'trashed_docs': trashed_docs_paginated},
        context_instance=RequestContext(request))


@login_required
def ajx_list_users(request):
    """
    Lists the users acoording to the a given string.
    """
    if not request.is_ajax():
        return HttpResponse(status=400)

    users = User.objects.all()

    response_data = [user.username for user in users]

    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@login_required
def ajx_list_issues_for_markup_files(request):
    """
    Lists the issues of a given journal to be used by the
    ``markup_files.html`` page.

    The following values must be passed as querystring parameters:

    ``j`` is a journal's id

    ``all`` is a boolean value that returns all issues
    from a journal or only the ones containing the attribute
    ``is_marked_up`` set to False.
    """
    if not request.is_ajax():
        return HttpResponse(status=400)

    journal_id = request.GET.get('j', None)
    journal = get_object_or_404(models.Journal, pk=journal_id)

    all_issues = asbool(request.GET.get('all', True))

    journal_issues = journal.issue_set.all()

    if not all_issues:
        journal_issues = journal_issues.filter(is_marked_up=False)

    issues = []
    for issue in journal_issues:
        text = '{0} - {1}'.format(issue.publication_year, issue.label)
        issues.append({'id': issue.pk, 'text': text})

    response_data = json.dumps(issues)

    return HttpResponse(response_data, mimetype="application/json")


@login_required
def ajx_lookup_for_section_translation(request):
    """
    Says if a given translation already exists in a given
    journal.

    The following values must be passed as querystring parameters:

    ``j`` is a journal's id
    ``t`` is a urlencoded section translation
    ``exc`` is a section id to be excluded from the search
    """
    MSG_EXISTS = _('The section already exists.')
    MSG_NOT_EXISTS = _('This is a new section.')

    if not request.is_ajax():
        return HttpResponse(status=400)

    journal_id = request.GET.get('j', None)
    if not journal_id:
        return HttpResponse(status=400)

    section_title = request.GET.get('t', None)
    if not section_title:
        return HttpResponse(status=400)

    try:
        exclude = int(request.GET.get('exc', 0))
    except ValueError:
        return HttpResponse(status=400)

    found_secs = models.Section.userobjects.all().available().filter(
        journal__pk=journal_id, titles__title=section_title)

    sections = [[unicode(sec), sec.actual_code] for sec in found_secs if sec.pk != exclude]
    has_sections = bool(sections)
    data = {
        'exists': has_sections,
        'sections': sections,
        'message': MSG_EXISTS if has_sections else MSG_NOT_EXISTS,
    }

    response_data = json.dumps(data)

    return HttpResponse(response_data, mimetype="application/json")


@permission_required('journalmanager.add_pressrelease', login_url=AUTHZ_REDIRECT_URL)
def add_pressrelease(request, journal_id, prelease_id=None):
    journal = get_object_or_404(models.Journal, pk=journal_id)

    if prelease_id:
        pressrelease = get_object_or_404(models.RegularPressRelease,
                                         pk=prelease_id)
    else:
        pressrelease = models.RegularPressRelease()

    pr_forms = get_all_pressrelease_forms(request.POST, journal, pressrelease)

    pressrelease_form = pr_forms['pressrelease_form']
    translation_formset = pr_forms['translation_formset']
    article_formset = pr_forms['article_formset']

    if request.method == 'POST':

        if pressrelease_form.is_valid() and translation_formset.is_valid():
            pressrelease_form.save()
            translation_formset.save()

            if article_formset.is_valid():
                article_formset.save()

            messages.info(request, MSG_FORM_SAVED)

            return HttpResponseRedirect(reverse('prelease.index', args=[journal_id]))
        else:
            messages.error(request, MSG_FORM_MISSING)

    return render_to_response(
        'journalmanager/add_pressrelease.html',
        {
            'pressrelease_form': pressrelease_form,
            'translation_formset': translation_formset,
            'article_formset': article_formset,
            'journal': journal,
        },
        context_instance=RequestContext(request)
    )


@permission_required('journalmanager.add_pressrelease', login_url=AUTHZ_REDIRECT_URL)
def add_aheadpressrelease(request, journal_id, prelease_id=None):
    journal = get_object_or_404(models.Journal, pk=journal_id)

    if prelease_id:
        pressrelease = get_object_or_404(models.AheadPressRelease,
                                         pk=prelease_id)
    else:
        pressrelease = models.AheadPressRelease()

    pr_forms = get_all_ahead_pressrelease_forms(request.POST, journal, pressrelease)

    pressrelease_form = pr_forms['pressrelease_form']
    translation_formset = pr_forms['translation_formset']
    article_formset = pr_forms['article_formset']

    if request.method == 'POST':
        if (pressrelease_form.is_valid() and
                translation_formset.is_valid() and
                article_formset.is_valid()):

            pr = pressrelease_form.save(commit=False)
            pr.journal = journal
            pr.save()
            translation_formset.save()
            article_formset.save()

            messages.info(request, MSG_FORM_SAVED)

            return HttpResponseRedirect(reverse('prelease.index', args=[journal_id]) + '?tab=ahead')
        else:
            messages.error(request, MSG_FORM_MISSING)

    return render_to_response(
        'journalmanager/add_pressrelease.html',
        {
            'pressrelease_form': pressrelease_form,
            'translation_formset': translation_formset,
            'article_formset': article_formset,
            'journal': journal,
        },
        context_instance=RequestContext(request)
    )
