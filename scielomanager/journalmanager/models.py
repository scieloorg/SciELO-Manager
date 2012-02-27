# -*- encoding: utf-8 -*-
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.conf.global_settings import LANGUAGES

import choices
import helptexts


class IndexingCoverage(models.Model):
    database_name = models.CharField(_('Database Name'),max_length=256,null=False,blank=True)
    database_acronym = models.CharField(_('Database Acronym'),max_length=16,null=False,blank=True)

    def __unicode__(self):
        return u'%s' % (self.database_name)

class Collection(models.Model):
    name = models.CharField(_('Collection Name'), max_length=128, db_index=True,)
    url = models.URLField(_('Instance URL'), )
    validated = models.BooleanField(_('Validated'), default=False, )

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        ordering = ['name']

class UserProfile(models.Model):
    user=models.ForeignKey(User, unique=True)
    collection = models.ForeignKey(Collection, related_name='user_collection', blank=False)
    is_manager = models.BooleanField(_('Is manager of the collection?'), default=False, null=False, blank=True)


class CustomInstitutionManager(models.Manager):

    def available(self, avalability=True):
        return super(CustomInstitutionManager, self).get_query_set().filter(is_available=avalability)

class Institution(models.Model):

    #Custom manager
    objects = CustomInstitutionManager()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(_('Institution Name'), max_length=128, db_index=True)
    acronym = models.CharField(_('Sigla'), max_length=16, db_index=True, blank=True)
    collection = models.ForeignKey(Collection, related_name='publisher_collection')
    country = models.CharField(_('Country'), max_length=32)
    state = models.CharField(_('State'), max_length=32, null=False,blank=True,)
    city = models.CharField(_('City'), max_length=32, null=False,blank=True,)
    Address = models.TextField(_('Address'), )
    Address_number = models.CharField(_('Number'), max_length=8)
    Address_complement = models.CharField(_('Complement'), max_length=128, null=False,blank=True,)
    zip_code = models.CharField(_('Zip Code'), max_length=16, null=True, blank=True)
    phone = models.CharField(_('Phone Number'), max_length=16, null=False,blank=True,)
    fax = models.CharField(_('Fax Number'), max_length=16, null=False,blank=True,)
    cel = models.CharField(_('Cel Number'), max_length=16, null=False,blank=True,)
    mail = models.EmailField(_('Email'),)
    validated = models.BooleanField(_('Validated'), default=False,)
    is_available = models.BooleanField(_('Is Available?'), default=True, null=False, blank=True)

    def __unicode__(self):
        return u'%s' % (self.name)

    def get_address_as_list(self):
        return self.Address.split("\n")

    class Meta:
        ordering = ['name']


class CustomJournalManager(models.Manager):

    def available(self, availability=True):
        return super(CustomJournalManager, self).get_query_set().filter(is_available=availability)

class Journal(models.Model):

    #Custom manager
    objects = CustomJournalManager()

    # PART 1
    creator = models.ForeignKey(User, related_name='enjoy_creator', editable=False)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    collections = models.ManyToManyField('Collection')
    institution = models.ForeignKey(Institution, related_name='journal_institution',null=False)
    title = models.CharField(_('Journal Title'),max_length=256, db_index=True)

    previous_title = models.ForeignKey('Journal',related_name='prev_title', null=True, blank=True)

    acronym = models.CharField(_('Acronym'),max_length=8, blank=False)
    scielo_issn = models.CharField(_('SciELO ISSN'),max_length=16,
        choices=choices.SCIELO_ISSN,null=False,blank=True)
    print_issn = models.CharField(_('Print ISSN'),max_length=9,null=False,blank=True)
    eletronic_issn = models.CharField(_('Eletronic ISSN'),max_length=9,null=False,blank=True)
    subject_descriptors = models.CharField(_('Subject / Descriptors'),max_length=512,null=False,blank=True)
    study_area = models.CharField(_('Study Area'),max_length=256,
        choices=choices.SUBJECTS,null=False,blank=True)

    #PART 2
    init_year = models.CharField(_('Initial Date'),max_length=10,null=True,blank=True)
    init_vol = models.CharField(_('Initial Volume'), max_length=4,null=False,blank=True)
    init_num = models.CharField(_('Initial Number'), max_length=4,null=False,blank=True)
    final_year = models.CharField(_('Final Date'),max_length=10,null=True,blank=True)
    final_vol = models.CharField(_('Final Volume'),max_length=4,null=False,blank=True)
    final_num = models.CharField(_('Final Number'),max_length=4,null=False,blank=True)
    frequency = models.CharField(_('Frequency'),max_length=16,
        choices=choices.FREQUENCY,null=False,blank=True)
    pub_status = models.CharField(_('Publication Status'),max_length=16,
        choices=choices.PUBLICATION_STATUS,null=False,blank=True)
    alphabet = models.CharField(_('Alphabet'),max_length=16,
        choices=choices.ALPHABET,null=False,blank=True)
    sponsor = models.CharField(_('Sponsor'), max_length=256,null=True,blank=True)
    national_code = models.CharField(_('National Code'), max_length=16,null=False,blank=True)
    editorial_standard = models.CharField(_('Editorial Standard'),max_length=64,
        choices=choices.STANDARD,null=False,blank=True)
    ctrl_vocabulary = models.CharField(_('Controlled Vocabulary'),max_length=64,
        choices=choices.CTRL_VOCABULARY,null=False,blank=True)
    literature_type = models.CharField(_('Literature Type'),max_length=64,
        choices=choices.LITERATURE_TYPE,null=False,blank=True)
    treatment_level = models.CharField(_('Treatment Type'),max_length=64,
        choices=choices.TREATMENT_LEVEL,null=False,blank=True)
    pub_level = models.CharField(_('Publication Level'),max_length=64,
        choices=choices.PUBLICATION_LEVEL,null=False,blank=True)
    indexing_coverage = models.ManyToManyField(IndexingCoverage)
    secs_code = models.CharField(_('SECS Code'), max_length=64,null=False,blank=True)

    use_license = models.ForeignKey('UseLicense', null=True, blank=False)
    copyrighter = models.CharField(_('Copyrighter'), max_length=254, null=True, blank=True)
    url_main_collection = models.CharField(_('URL of main collection'), max_length=64,null=True,blank=True)
    url_online_submission = models.CharField(_('URL of online submission'), max_length=64,null=True,blank=True)
    url_journal = models.CharField(_('URL of the journal'), max_length=64,null=True,blank=True)
    subscription = models.CharField(_('Subscription'), max_length=4, null=False, default='na', blank=True, choices=choices.SUBSCRIPT)

    notes = models.TextField(_('Notes'), max_length=254, null=True, blank=True)

    id_provided_by_the_center = models.CharField(_('ID provided by the Center'), max_length=64,null=True,blank=True) #v30

    center = models.ForeignKey('Center', related_name='center_id', null=True, blank=False, )
    validated = models.BooleanField(_('Validated'), default=False,null=False,blank=True )
    is_available = models.BooleanField(_('Is Available?'), default=True, null=False, blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']

class JournalTitle(models.Model):
    journal = models.ForeignKey(Journal)
    title = models.CharField(_('Title'), null=False, max_length=128)
    category = models.CharField(_('Title Category'), null=False, max_length=128, choices=choices.TITLE_CATEGORY)

class JournalTextLanguage(models.Model):
    journal = models.ForeignKey(Journal)
    language = models.CharField(_('Text Languages'),max_length=64,choices=LANGUAGES,blank=True,null=False)

class JournalAbstrLanguage(models.Model):
    journal = models.ForeignKey(Journal)
    language = models.CharField(_('Language of the Abstract'), max_length=8, choices=LANGUAGES,null=False,blank=True)

class JournalHist(models.Model):
    journal = models.ForeignKey(Journal)
    date = models.DateField(_('Date'),editable=True,blank=True)
    status = models.CharField(_('Status'),choices=choices.JOURNAL_HIST_STATUS,null=False,blank=True, max_length=2)

class JournalMission(models.Model):
    journal = models.ForeignKey(Journal,null=False)
    description = models.TextField(_('Mission'),null=False)
    language = models.CharField(_('Language'),null=False, max_length=2,choices=LANGUAGES)

class UseLicense(models.Model):
    license_code = models.CharField(_('License Code'), unique=True, null=False, blank=False, max_length=64)
    reference_url = models.URLField(_('License Reference URL'), null=True, blank=True)
    disclaimer = models.TextField(_('Disclaimer'), null=True, blank=True, max_length=512)

    def __unicode__(self):
        return self.license_code

class TranslatedData(models.Model):
    translation = models.CharField(_('Translation'), null=True, blank=True, max_length=512)
    language = models.CharField(_('Language'), choices=choices.LANGUAGE, null=False, blank=False, max_length=32)
    model = models.CharField(_('Model'), null=False, blank=False, max_length=32)
    field = models.CharField(_('Field'), null=False, blank=False, max_length=32)

    def __unicode__(self):
        return self.translation if self.translation is not None else 'Missing trans: {0}.{1}'.format(self.model, self.field)

class Section(models.Model):
    #Custom manager
    objects = CustomJournalManager()

    title = models.CharField(_('Title'), null=True, blank=True, max_length=256)
    title_translations = models.ManyToManyField(TranslatedData, null=True, blank=True,)
    journal = models.ForeignKey(Journal, null=False, blank=False)
    code = models.CharField(_('Code'), null=True, blank=True, max_length=16)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(_('Is Available?'), default=True, null=False, blank=False)

    def __unicode__(self):
        return self.code

class CustomIssueManager(models.Manager):

    def available(self, avalability=True):
        return super(CustomIssueManager, self).get_query_set().filter(is_available=avalability)

class Issue(models.Model):

    #Custom manager
    objects = CustomIssueManager()

    section = models.ManyToManyField(Section)
    journal = models.ForeignKey(Journal, null=True, blank=False)
    title = models.CharField(_('Title'), null=True, blank=True, max_length=256)
    volume = models.CharField(_('Volume'), null=True, blank=True, max_length=16)
    number = models.CharField(_('Number'), null=True, blank=True, max_length=16)
    is_press_release = models.BooleanField(_('Is Press Release?'), default=False, null=False, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    publication_date = models.DateField(null=False, blank=False)
    is_available = models.BooleanField(_('Is Available?'), default=True, null=False, blank=True) #status v42
    is_marked_up = models.BooleanField(_('Is Marked Up?'), default=False, null=False, blank=True) #v200
    bibliographic_strip = models.CharField(_('Custom Bibliographic Strip'), null=True, blank=True, max_length=128) #l10n
    use_license = models.ForeignKey(UseLicense, null=True)
    publisher_fullname = models.CharField(_('Publisher Full Name'), null=True, blank=True, max_length=128)
    total_documents = models.IntegerField(_('Total of Documents'), null=False, blank=False, default=0)
    ctrl_vocabulary = models.CharField(_('Controlled Vocabulary'), max_length=64,
        choices=choices.CTRL_VOCABULARY, null=False, blank=True)
    editorial_standard = models.CharField(_('Editorial Standard'), max_length=64,
        choices=choices.STANDARD, null=False, blank=True)

    def identification(self):
        n = self.number
        if n != 'ahead' and n != 'review':
            n ='(' + self.number + ')'
        else:
            n = self.number

        return self.volume + ' ' + n

    def __unicode__(self):
        return self.identification()

class Supplement(Issue):
    suppl_label = models.CharField(_('Supplement Label'), null=True, blank=True, max_length=256)

class Center(Institution):
    is_provider_of_markup = models.BooleanField(_('Is provider of the marked files?'), default=False, null=False, blank=True)
