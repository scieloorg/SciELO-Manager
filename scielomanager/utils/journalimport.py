#!/usr/bin/env python
#coding: utf-8
import json
import os
import difflib
import subfield
from datetime import date

from django.core.management import setup_environ
from django.core import exceptions

try:
    from scielomanager import settings
except ImportError:
    BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
    from sys import path
    path.append(BASE_PATH)
    import settings

setup_environ(settings)
from journalmanager.models import *

class JournalImport:

    def __init__(self):
        self._publishers_pool = []
        self._sponsors_pool = []
        self._summary = {}
        self.trans_pub_status = {'c':'current',
            'd':'deceased',
            's':'suspended',
            '?':'inprogress',
            }

    def iso_format(self, dates, string='-'):
        day = dates[6:8]
        if day == "00":
            day = "01"

        month = dates[4:6]
        if month == "00":
            month = "01"

        dateformated = "%s-%s-%s" % (dates[0:4],month,day)

        return dateformated

    def charge_summary(self, attribute):
        """
        Function: charge_summary
        Carrega com +1 cada atributo passado para o metodo, se o attributo nao existir ele e criado.
        """
        if not self._summary.has_key(attribute):
            self._summary[attribute] = 0

        self._summary[attribute] += 1

    def have_similar_publishers(self, match_string):
        """
        Function: have_similar_publishers
        Identifica se existe instituicao ja registrada com o mesmo nome, com o objetivo de filtrar
        instituticoes duplicadas.
        Retorna o id da instituicao se houver uma cadastrada com o mesmo nome, caso contrario Retorna
        False.
        """
        publisher_id=""

        if len(self._publishers_pool) > 0:
            for inst in self._publishers_pool:
                if inst["match_string"] == match_string:
                    publisher_id = inst["id"]
                    break
                else:
                    publisher_id = False
        else:
            publisher_id = False

        return publisher_id

    def have_similar_sponsors(self, match_string):
        """
        Function: have_similar_sponsors
        Identifica se existe instituicao ja registrada com o mesmo nome, com o objetivo de filtrar
        instituticoes duplicadas.
        Retorna o id da instituicao se houver uma cadastrada com o mesmo nome, caso contrario Retorna
        False.
        """
        sponsor_id=""

        if len(self._sponsors_pool) > 0:
            for inst in self._sponsors_pool:
                if inst["match_string"] == match_string:
                    sponsor_id = inst["id"]
                    break
                else:
                    sponsor_id = False
        else:
            sponsor_id = False

        return sponsor_id

    def load_publisher(self, collection, record):
        """
        Function: load_publisher
        Retorna um objeto Publisher() caso a gravação do mesmo em banco de dados for concluida
        """

        publisher = Publisher()

        # Publishers Import
        if not record.has_key('480'):
            return []

        publisher.name = record['480'][0]
        publisher.address = " ".join(record['63'])

        match_string=publisher.name

        similar_key =  self.have_similar_publishers(match_string)

        loaded_publisher=""

        if similar_key != False:
            similar_publisher=Publisher.objects.get(id=similar_key)
            similar_publisher.address += "\n"+publisher.address
            similar_publisher.save()
            self.charge_summary("publishers_duplication_fix")
            loaded_publisher = similar_publisher
        else:
            publisher.save(force_insert=True)
            publisher.collections.add(collection)
            self.charge_summary("publishers")
            loaded_publisher = publisher
            self._publishers_pool.append(dict({"id":publisher.id,"match_string":match_string}))


        return [loaded_publisher,]

    def load_sponsor(self, collection, record):
        """
        Function: load_sponsor
        Retorna um objeto Sponsor() caso a gravação do mesmo em banco de dados for concluida
        """

        sponsor = Sponsor()

        # Sponsors Import
        if not record.has_key('140'):
            return []

        sponsor.name = record['140'][0]

        match_string=sponsor.name.strip()

        similar_key =  self.have_similar_sponsors(match_string)

        loaded_sponsor=""

        if similar_key != False:
            similar_sponsor=Sponsor.objects.get(id=similar_key)
            self.charge_summary("sponsors_duplication_fix")
            loaded_sponsor = similar_sponsor
        else:
            sponsor.save(force_insert=True)
            sponsor.collections.add(collection)
            self.charge_summary("sponsors")
            loaded_sponsor = sponsor
            self._sponsors_pool.append(dict({"id":sponsor.id,"match_string":match_string.strip()}))

        return [loaded_sponsor,]

    def load_studyarea(self, journal, areas):

        for i in areas:
            studyarea = JournalStudyArea()
            studyarea.study_area = i
            journal.journalstudyarea_set.add(studyarea)
            self.charge_summary("studyarea")

    def load_textlanguage(self, journal, langs):

        from sectionimport import LANG_DICT as lang_dict
        for i in langs:
            language = Language.objects.get_or_create(iso_code = i, name = lang_dict.get(i, '###NOT FOUND###'))[0]

            journal.languages.add(language)
            self.charge_summary("language_%s" % i)

    def load_abstractlanguage(self, journal, langs):

        from sectionimport import LANG_DICT as lang_dict
        for i in langs:
            language = Language.objects.get_or_create(iso_code = i, name = lang_dict.get(i, '###NOT FOUND###'))[0]

            journal.abstract_keyword_languages.add(language)
            self.charge_summary("language_%s" % i)

    def load_mission(self, journal, missions):
        from sectionimport import LANG_DICT as lang_dict

        for i in missions:
            parsed_subfields = subfield.CompositeField(subfield.expand(i))
            mission = JournalMission()
            try:
                language = Language.objects.get_or_create(iso_code = parsed_subfields['l'], name = lang_dict.get(parsed_subfields['l'], '###NOT FOUND###'))[0]
                mission.language = language
            except:
                pass
            mission.description = parsed_subfields['_']
            journal.missions.add(mission)
            self.charge_summary("mission")

    def load_historic(self, journal, historicals):
        import operator

        lifecycles = {}

        for i in historicals:
            expanded = subfield.expand(i)
            parsed_subfields = dict(expanded)
            try:
                lifecycles[self.iso_format(parsed_subfields['a'])] = parsed_subfields['b']
            except KeyError:
                self.charge_summary("history_error_field")

            try:
                lifecycles[self.iso_format(parsed_subfields['c'])] = parsed_subfields['d']
            except KeyError:
                self.charge_summary("history_error_field")


        for cyclekey,cyclevalue in iter(sorted(lifecycles.iteritems())):
            try:
                journalhist = JournalPublicationEvents()
                journalhist.created_at = cyclekey
                journalhist.status = self.trans_pub_status.get(cyclevalue.lower(),'inprogress')
                journalhist.journal = journal
                journalhist.changed_by_id = 1
                journalhist.save()
                journalhist.created_at = cyclekey
                journalhist.save() #Updating to real date, once when saving the model is given a automatica value
                self.charge_summary("publication_events")
            except exceptions.ValidationError:
                self.charge_summary("publications_events_error_data")
                return False

        return True

    def get_last_status(self, historicals):
        import operator

        lifecycles = {}

        for i in historicals:
            expanded = subfield.expand(i)
            parsed_subfields = dict(expanded)
            try:
                lifecycles[self.iso_format(parsed_subfields['a'])] = parsed_subfields['b']
            except KeyError:
                self.charge_summary("history_error_field")

            try:
                lifecycles[self.iso_format(parsed_subfields['c'])] = parsed_subfields['d']
            except KeyError:
                self.charge_summary("history_error_field")

        return sorted(lifecycles.iteritems())[-1][1]

    def load_title(self, journal, titles, category):

        for i in titles:
            title = JournalTitle()
            title.title = i
            title.category = category
            journal.other_titles.add(title)
            self.charge_summary("title")

    def load_use_license(self,code, disclaimer):

        expanded_disclaimer = subfield.expand(disclaimer)
        parsed_subfields_disclaimer = dict(expanded_disclaimer)

        use_license = UseLicense.objects.get_or_create(license_code=code)[0]

        if parsed_subfields_disclaimer.has_key('t'):
            use_license.disclaimer = parsed_subfields_disclaimer['t']

        use_license.save()
        
        return use_license

    def load_journal(self, collection, loaded_publisher, loaded_sponsor, record):
        """
        Function: load_journal
        Retorna um objeto journal() caso a gravação do mesmo em banco de dados for concluida
        """

        issn_type=""
        print_issn=""
        electronic_issn=""

        # Creating use license codes.
        license_code = ""
        license_disclaimer = ""
        if record.has_key('541'):
            license_code = record['541'][0]
        if record.has_key('540'):
            license_disclaimer = record['540'][0]
        use_license = self.load_use_license(license_code,license_disclaimer)

        journal = Journal()

        # ISSN and Other Complex Stuffs from the old version
        if record['35'][0] == "PRINT":
            issn_type="print"
            print_issn = record['935'][0]
            if record['935'][0] != record['400'][0]:
                issn_type="eletronic"
                electronic_issn = record['400'][0]
        else:
            issn_type="electronic"
            electronic_issn = record['935'][0]
            if record['935'][0] != record['400'][0]:
                issn_type="print"
                print_issn = record['400'][0]

        journal.scielo_issn = issn_type
        journal.print_issn = print_issn
        journal.eletronic_issn = electronic_issn

        # Journal Original Title
        journal.title =  record['100'][0]

        # Short Title
        journal.short_title =  record['150'][0]

        # Acronym
        journal.acronym = record['930'][0]

        # Use License
        journal.use_license = use_license

        # Subject Descriptors
        journal.subject_descriptors = '\n'.join(record['440']).lower()

        # Indexing Coverage
        if record.has_key('450'):
            journal.index_coverage = '\n'.join(record['450']).lower()

        # Copyright
        if record.has_key('62'):
            journal.copyrighter = record['62'][0]

        # Text Language
        if record.has_key('301'):
            journal.init_year = record['301'][0]

        # Initial Volume
        if record.has_key('302'):
            journal.init_vol = record['302'][0]

        # Initial Number
        if record.has_key('303'):
            journal.init_num = record['303'][0]

        # Final Year
        if record.has_key('304'):
            journal.final_year = record['304'][0]

        # Final Volumen
        if record.has_key('305'):
            journal.final_vol = record['305'][0]

        # Final Number
        if record.has_key('306'):
            journal.final_num = record['306'][0]

        # Publication Frequency
        if record.has_key('380'):
            journal.frequency = record['380'][0]

        if record.has_key('692'):
            journal.url_online_submission = record['692'][0]

        if record.has_key('69'):
            journal.url_journal = record['69'][0]

        if record.has_key('51'):
            journal.pub_status = self.trans_pub_status.get(self.get_last_status(record['51']).lower(),'inprogress')

        if record.has_key('340'):
            journal.alphabet = record['340'][0]

        if record.has_key('20'):
            journal.national_code = record['20'][0]

        if record.has_key('117'):
            journal.editorial_standard = record['117'][0]

        if record.has_key('85'):
            journal.ctrl_vocabulary = record['85'][0]

        if record.has_key('5'):
            journal.literature_type = record['5'][0]

        if record.has_key('6'):
            journal.treatment_level = record['6'][0]

        if record.has_key('330'):
            journal.pub_level = record['330'][0]

        if record.has_key('37'):
            journal.secs_code = record['37'][0]

        if record.has_key('151'):
            journal.title_iso = record['151'][0]


        journal.pub_status_changed_by_id = 1
        journal.creator_id = 1
        journal.save(force_insert=True)

        journal.collections.add(collection)

        self.charge_summary("journals")

        journal.publisher = loaded_publisher

        journal.sponsor = loaded_sponsor

        # created date
        if record.has_key('940'):
            journal.created = self.iso_format(record['940'][0])

        # updated date
        if record.has_key('941'):
            journal.updated = self.iso_format(record['941'][0])

        # text language
        if record.has_key('350'):
            self.load_textlanguage(journal,record['350'])

        # abstract language
        if record.has_key('360'):
            self.load_abstractlanguage(journal,record['360'])

        # study area
        if record.has_key('441'):
            self.load_studyarea(journal,record['441'])

        # mission
        if record.has_key('901'):
            self.load_mission(journal,record['901'])

        # historic - JournalPublicationEvents
        if record.has_key('51'):
            self.load_historic(journal,record['51'])

        # titles
        if record.has_key('421'):
            self.load_title(journal,record['421'],'other')

        if record.has_key('150'):
            self.load_title(journal,record['150'],'other')

        if record.has_key('230'):
            self.load_title(journal,record['230'],'paralleltitle')

        journal.save()

        return journal

    def run_import(self, json_file, collection):
        """
        Function: run_import
        Dispara processo de importacao de dados
        """

        json_parsed={}

        json_file = open(json_file,'r')
        json_parsed = json.loads(json_file.read())

        for record in json_parsed:
            loaded_publisher = self.load_publisher(collection, record)
            loaded_sponsor = self.load_sponsor(collection, record)
            loaded_journal = self.load_journal(collection, loaded_publisher, loaded_sponsor, record)

        # Cleaning data
        JournalPublicationEvents.objects.filter(created_at__month=date.today().month, created_at__year=date.today().year).delete()

    def get_summary(self):
        """
        Function: get_summary
        Retorna o resumo de carga de registros
        """
        return self._summary
