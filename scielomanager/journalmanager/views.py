import json
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
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import loader
from django.template.context import RequestContext
from django.utils.translation import ugettext as _

from scielomanager.journalmanager import models
from scielomanager.journalmanager.forms import *
from scielomanager.tools import get_paginated


def get_user_collections(user_id):

    user_collections = User.objects.get(pk=user_id).usercollections_set.all()

    return user_collections        

def index(request):
    t = loader.get_template('journalmanager/home_journal.html')
    if request.user.is_authenticated():
        user_collections = get_user_collections(request.user.id)
    else:
        user_collections = ""

    c = RequestContext(request,{'user_collections':user_collections,})
    return HttpResponse(t.render(c),)

@login_required
def user_index(request):
    
    
    user_collections = get_user_collections(request.user.id)
    user_collections_managed = user_collections.filter(is_manager=True)

    # Filtering users manager by the administrator
    all_users = models.User.objects.filter(usercollections__collection__in =
        ( collection.collection.pk for collection in user_collections_managed )).distinct('username')

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
                    t = loader.get_template(next)
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
            c = RequestContext(request, {'next': next,})
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
        user = models.User()
    else:
        user = get_object_or_404(models.User, id = user_id)

    # Getting Collections from the logged user.
    user_collections = get_user_collections(request.user.id)

    UserCollectionsFormSet = inlineformset_factory(models.User, models.UserCollections, 
        form=UserCollectionsForm, extra=1, can_delete=True)

    if request.method == 'POST':
        usercollectionsformset = UserCollectionsFormSet(request.POST, instance=user, prefix='usercollections',)
        user_form_kwargs = {}

        if user_id is not None: #edit - preserve form-data    
            filled_form = user
            user_form_kwargs['instance'] = filled_form

        add_form = UserForm(request.POST, **user_form_kwargs)

        if add_form.is_valid():
            user_saved = add_form.save()
            usercollectionsformset = UserCollectionsFormSet(request.POST, instance=user_saved, prefix='usercollections',)
            usercollectionsformset.save()     

            return HttpResponseRedirect(reverse('user.index'))
    else:
        if user_id is None: #new
            add_form = UserForm() # An unbound form
            usercollectionsformset = UserCollectionsFormSet(instance=user, prefix='usercollections')
        else:
            filled_form = models.User.objects.get(pk = user_id)
            add_form = UserForm(instance = filled_form)
            usercollectionsformset = UserCollectionsFormSet(instance=user, prefix='usercollections')

    return render_to_response('journalmanager/add_user.html', {
                              'add_form': add_form,
                              'mode': 'user_journal',
                              'user_name': request.user.pk,
                              'user_collections': user_collections,
                              'usercollectionsformset': usercollectionsformset},
                              context_instance=RequestContext(request))

@login_required
def toggle_user_availability(request, user_id):
  user = get_object_or_404(models.User, pk = user_id)
  user.is_active = not user.is_active
  user.save()

  return HttpResponseRedirect(reverse('user.index'))

@login_required
def journal_index(request):
    user_collections = get_user_collections(request.user.id)
    default_collections = user_collections.filter(is_default=True)

    all_journals = models.Journal.objects.available(request.GET.get('is_available', 1))

    journals = get_paginated(all_journals, request.GET.get('page', 1))

    t = loader.get_template('journalmanager/journal_dashboard.html')
    c = RequestContext(request, {
                       'journals': journals,
                       'user_collections': user_collections,
                       })
    return HttpResponse(t.render(c))

@login_required
def add_journal(request, journal_id = None):
    """
    Handles new and existing journals
    """
    user_collections = get_user_collections(request.user.id)

    if  journal_id == None:
        journal = models.Journal()
    else:
        journal = get_object_or_404(models.Journal, id = journal_id)

    JournalTitleFormSet = inlineformset_factory(models.Journal, models.JournalTitle, form=JournalTitleForm, extra=1, can_delete=True)
    JournalStudyAreaFormSet = inlineformset_factory(models.Journal, models.JournalStudyArea, form=JournalStudyAreaForm, extra=1, can_delete=True)
    JournalMissionFormSet = inlineformset_factory(models.Journal, models.JournalMission, form=JournalMissionForm, extra=1, can_delete=True)
    JournalTextLanguageFormSet = inlineformset_factory(models.Journal, models.JournalTextLanguage, extra=1, can_delete=True)
    JournalHistFormSet = inlineformset_factory(models.Journal, models.JournalHist, extra=1, can_delete=True)
    JournalCollectionsFormSet = inlineformset_factory(models.Journal, models.JournalCollections, extra=1, can_delete=True)
    JournalIndexCoverageFormSet = inlineformset_factory(models.Journal, models.JournalIndexCoverage, extra=1, can_delete=True)

    if request.method == "POST":

        journalform = JournalForm(request.POST, instance=journal, prefix='journal')
        studyareaformset = JournalStudyAreaFormSet(request.POST, instance=journal, prefix='studyarea')
        titleformset = JournalTitleFormSet(request.POST, instance=journal, prefix='title')
        missionformset = JournalMissionFormSet(request.POST, instance=journal, prefix='mission')
        textlanguageformset = JournalTextLanguageFormSet(request.POST, instance=journal, prefix='textlanguage')
        histformset = JournalHistFormSet(request.POST, instance=journal, prefix='hist')
        collectionsformset = JournalCollectionsFormSet(request.POST, instance=journal, prefix='collection')
        indexcoverageformset = JournalIndexCoverageFormSet(request.POST, instance=journal, prefix='indexcoverage')

        if journalform.is_valid() and studyareaformset.is_valid() and titleformset.is_valid() and indexcoverageformset.is_valid() and collectionsformset.is_valid() \
            and missionformset.is_valid() and textlanguageformset.is_valid() and histformset.is_valid():
            journalform.save_all(creator = request.user)
            studyareaformset.save()
            titleformset.save()
            missionformset.save()
            textlanguageformset.save()
            histformset.save()
            collectionsformset.save()
            indexcoverageformset.save()

            return HttpResponseRedirect(reverse('journal.index'))

    else:
        journalform  = JournalForm(instance=journal, prefix='journal')
        studyareaformset = JournalStudyAreaFormSet(instance=journal, prefix='studyarea')
        titleformset = JournalTitleFormSet(instance=journal, prefix='title')
        missionformset  = JournalMissionFormSet(instance=journal, prefix='mission')
        textlanguageformset = JournalTextLanguageFormSet(instance=journal, prefix='textlanguage')
        histformset = JournalHistFormSet(instance=journal, prefix='hist')
        collectionsformset = JournalCollectionsFormSet(instance=journal, prefix='collection')
        indexcoverageformset = JournalIndexCoverageFormSet(instance=journal, prefix='indexcoverage')

    return render_to_response('journalmanager/add_journal.html', {
                              'add_form': journalform,
                              'collectionsformset': collectionsformset,
                              'studyareaformset': studyareaformset,
                              'titleformset': titleformset,
                              'missionformset': missionformset,
                              'user_collections': user_collections,
                              'textlanguageformset': textlanguageformset,
                              'histformset': histformset,
                              'indexcoverageformset': indexcoverageformset,
                              }, context_instance = RequestContext(request))


@login_required
def publisher_index(request):
    user_collections = get_user_collections(request.user.id)
    default_collections = user_collections.filter(is_default = True)

    all_publishers = models.Publisher.objects.available(request.GET.get('is_available', 1))
    publishers = get_paginated(all_publishers, request.GET.get('page', 1))

    t = loader.get_template('journalmanager/publisher_dashboard.html')
    c = RequestContext(request, {
                       'publishers': publishers,
                       'user_collections': user_collections,
                       })
    return HttpResponse(t.render(c))

@login_required
def add_publisher(request, publisher_id=None):
    """
    Handles new and existing publishers
    """

    if  publisher_id == None:
        publisher = models.Publisher()
    else:
        publisher = get_object_or_404(models.Publisher, id = publisher_id)

    user_collections = get_user_collections(request.user.id)

    PublisherCollectionsFormSet = inlineformset_factory(models.Publisher, models.InstitutionCollections, 
      form=PublisherCollectionsForm, extra=1, can_delete=True)

    if request.method == "POST":
        publisherform = PublisherForm(request.POST, instance=publisher, prefix='publisher')
        publishercollectionsformset = PublisherCollectionsFormSet(request.POST, instance=publisher, prefix='publishercollections')


        if publisherform.is_valid() and publishercollectionsformset.is_valid():
            publisherform.save()
            publishercollectionsformset.save()

            return HttpResponseRedirect(reverse('publisher.index'))

    else:
        publisherform  = PublisherForm(instance=publisher, prefix='publisher')
        publishercollectionsformset =  PublisherCollectionsFormSet(instance=publisher, prefix='publishercollections')

    return render_to_response('journalmanager/add_publisher.html', {
                              'add_form': publisherform,
                              'user_name': request.user.pk,
                              'user_collections': user_collections,
                              'publishercollectionsformset': publishercollectionsformset,
                              },
                              context_instance = RequestContext(request))

@login_required
def issue_index(request, journal_id):
    #FIXME: models.Journal e models.Issue ja se relacionam, avaliar
    #estas queries.
    journal = models.Journal.objects.get(pk = journal_id)

    user_collections = get_user_collections(request.user.id)

    all_issues = models.Issue.objects.available(request.GET.get('is_available', 1)).filter(journal = journal_id)

    issues = get_paginated(all_issues, request.GET.get('page', 1))

    t = loader.get_template('journalmanager/issue_dashboard.html')
    c = RequestContext(request, {
                       'issues': issues,
                       'journal': journal,
                       'user_collections': user_collections,
                       })
    return HttpResponse(t.render(c))

@login_required
def add_issue(request, journal_id, issue_id=None):
    """
    Handles new and existing issues
    """

    user_collections = get_user_collections(request.user.id)
    journal = get_object_or_404(models.Journal, pk=journal_id)

    if issue_id is None:
        issue = models.Issue()
    else:
        issue = models.Issue.objects.get(pk=issue_id)


    if request.method == 'POST':
        add_form = IssueForm(request.POST, journal_id=journal.pk, instance=issue)

        if add_form.is_valid():
            add_form.save_all(journal)

            return HttpResponseRedirect(reverse('issue.index', args=[journal_id]))
    else:
        add_form = IssueForm(journal_id=journal.pk, instance=issue)

    return render_to_response('journalmanager/add_issue.html', {
                              'add_form': add_form,
                              'journal': journal,
                              'user_name': request.user.pk,
                              'user_collections': user_collections},
                              context_instance = RequestContext(request))

@login_required
def search_journal(request):
    user_collections = get_user_collections(request.user.id)
    default_collections = user_collections.filter(is_default=True)

    #Get journals where title contains the "q" value and collection equal with the user
    journals_filter = models.Journal.objects.filter(title__icontains = request.REQUEST['q']).order_by('title')

    #Paginated the result
    journals = get_paginated(journals_filter, request.GET.get('page', 1))

    t = loader.get_template('journalmanager/journal_search_result.html')
    c = RequestContext(request, {
                       'journals': journals,
                       'user_collections': user_collections,
                       'search_query_string': request.REQUEST['q'],
                       })
    return HttpResponse(t.render(c))

@login_required
def search_publisher(request):
    return publisher_index(request)

@login_required
def search_issue(request, journal_id):

    journal = models.Journal.objects.get(pk = journal_id)
    user_collections = get_user_collections(request.user.id)

    #Get issues where journal.id = journal_id and volume contains "q"
    selected_issues = models.Issue.objects.filter(journal = journal_id,
                                                  volume__icontains = request.REQUEST['q']).order_by('publication_date')

    #Paginated the result
    issues = get_paginated(selected_issues, request.GET.get('page', 1))

    t = loader.get_template('journalmanager/issue_dashboard.html')
    c = RequestContext(request, {
                       'issues': issues,
                       'journal': journal,
                       'user_collection': user_collections,
                       'search_query_string': request.REQUEST['q'],
                       })
    return HttpResponse(t.render(c))

@login_required
def section_index(request, journal_id):
    #FIXME: models.Journal e models.Issue ja se relacionam, avaliar
    #estas queries.
    journal = models.Journal.objects.get(pk = journal_id)
    user_collections = get_user_collections(request.user.id)

    all_sections = models.Section.objects.available(request.GET.get('is_available', 1)).filter(journal=journal_id)

    sections = get_paginated(all_sections, request.GET.get('page', 1))

    t = loader.get_template('journalmanager/section_dashboard.html')
    c = RequestContext(request, {
                       'items': sections,
                       'journal': journal,
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
    else:
        section = get_object_or_404(models.Section, pk=section_id)

    journal = get_object_or_404(models.Journal, pk=journal_id)

    if request.method == 'POST':
        add_form = SectionForm(request.POST, instance=section)

        if add_form.is_valid():
            add_form.save_all(journal)

            return HttpResponseRedirect(reverse('section.index', args=[journal_id]))

    else:
        add_form = SectionForm(instance=section)

    return render_to_response('journalmanager/add_section.html', {
                              'add_form': add_form,
                              'user_name': request.user.pk,
                              'journal': journal,
                              },
                              context_instance = RequestContext(request))
@login_required
def center_index(request):
    user_collections = get_user_collections(request.user.id)
    default_collections = user_collections.filter(is_default=True)

    all_centers = models.Center.objects.available(request.GET.get('is_available', 1))
    centers = get_paginated(all_centers, request.GET.get('page', 1))

    t = loader.get_template('journalmanager/center_dashboard.html')
    c = RequestContext(request, {
                       'centers': centers,
                       'user_collections': user_collections,
                       })
    return HttpResponse(t.render(c))

@login_required
def add_center(request, center_id=None):
    """
    Handles new and existing centers
    """
    if  center_id == None:
        center = models.Center()
    else:
        center = get_object_or_404(models.Center, id = center_id)

    user_collections = get_user_collections(request.user.id)

    CenterCollectionsFormSet = inlineformset_factory(models.Center, models.InstitutionCollections, 
      form=CenterCollectionsForm, extra=1, can_delete=True)


    if request.method == 'POST':
        centerform = CenterForm(request.POST, instance=center, prefix='center')
        centercollectionsformset = CenterCollectionsFormSet(request.POST, instance=center, prefix='centercollections')

        if centerform.is_valid():
            centerform.save()
            centercollectionsformset.save()

            return HttpResponseRedirect(reverse('center.index'))

    else:
        centerform  = CenterForm(instance=center, prefix='center')
        centercollectionsformset =  CenterCollectionsFormSet(instance=center, prefix='centercollections')

    return render_to_response('journalmanager/add_center.html', {
                              'add_form': centerform,
                              'user_name': request.user.pk,
                              'user_collections': user_collections,
                              'centercollectionsformset': centercollectionsformset,
                              },
                              context_instance = RequestContext(request))

@login_required
def generic_toggle_availability(request, object_id, model):

  if request.is_ajax():

    model = get_object_or_404(model, pk = object_id)
    model.is_available = not model.is_available
    model.save()

    response_data = json.dumps({
      "result": str(model.is_available),
      "object_id": model.id
      })

    #ajax response json
    return HttpResponse(response_data, mimetype="application/json")
  else:
    #bad request
    return HttpResponse(status=400)
    
@login_required
def search_center(request):
    return center_index(request)

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


