# coding: utf-8
from django.conf import settings

from scielomanager.export import bundle
from scielomanager.journalmanager import choices


MEDIA_ROOT = settings.MEDIA_ROOT + '/export/'
MEDIA_URL = settings.MEDIA_URL + '/export/'


class GenerationError(Exception):
    def __init__(self, *args, **kwargs):
        super(GenerationError, self).__init__(*args, **kwargs)


class Automata(object):
    """
    Represents the automata.mds file
    http://ref.scielo.org/2qx6fb
    """
    # {dbvalue: (citat, norma)}
    standards = {
        'iso690': ('icitat', 'iso'),
        'nbr6023': ('acitat', 'abnt'),
        'other': ('ocitat', 'other'),
        'vancouv': ('vcitat', 'vanc'),
        'apa': ('pcitat', 'apa'),
    }
    # {dbvalue: journalmethod}
    issns = {
        'print': 'print_issn',
        'electronic': 'electronic_issn',
    }

    def __init__(self, journal):
        self._journal = journal

    @property
    def citat(self):
        tags = self.standards.get(self._journal.editorial_standard, None)
        if not tags:
            raise AttributeError()

        return tags[0]

    @property
    def norma(self):
        tags = self.standards.get(self._journal.editorial_standard, None)
        if not tags:
            raise AttributeError()

        return tags[1]

    @property
    def issn(self):
        pid_issn_field = self._journal.scielo_issn
        pid_issn = getattr(self._journal, self.issns[pid_issn_field], None)
        if not pid_issn:
            raise AttributeError()

        return pid_issn

    @property
    def acron(self):
        return self._journal.acronym

    def __unicode__(self):
        return '{0};{1};{2}.amd;tg{3}.amd'.format(self.issn,
            self.citat, self.acron, self.norma)


class Issue(object):
    def __init__(self, issue):
        self._issue = issue

    @property
    def legend(self):
        return '{0} {1}'.format(self._issue.journal.title_iso,
                                unicode(self._issue))

    @property
    def period(self):
        return '%02d/%02d' % (self._issue.publication_start_month,
            self._issue.publication_end_month)

    @property
    def order(self):
        return str(self._issue.order)

    def __unicode__(self):
        rows = '\n'.join([self.legend, self.period, self.order, '', ''])
        return rows


class L10nIssue(Automata, Issue):
    def __init__(self, journal, issue):
        self._journal = journal
        self._issue = issue

    @property
    def abbrev_title(self):
        return self._issue.journal.title_iso

    @property
    def volume(self):
        return unicode(self._issue.volume)

    @property
    def number(self):
        return unicode(self._issue.number)

    @property
    def suppl_volume(self):
        return unicode(self._issue.suppl_volume)

    @property
    def suppl_number(self):
        return unicode(self._issue.suppl_number)

    @property
    def date_iso(self):
        return unicode(self._issue.publication_year)

    @property
    def status(self):
        # placebo
        return '1'

    @property
    def issue_meta(self):
        return ';'.join([
            self.abbrev_title,
            self.volume,
            self.suppl_volume,
            self.number,
            self.suppl_number,
            self.date_iso,
            self.issn,
            self.status,
        ])

    @property
    def sections(self):
        sections = ';'.join([unicode(section) for section in self._issue.section.all()])
        return sections if sections else 'No section title'

    @property
    def sections_ids(self):
        ids = ';'.join([unicode(section.actual_code) for section in self._issue.section.all()])
        return ids if ids else 'nd'

    @property
    def ctrl_vocabulary(self):
        vocabulary = dict(choices.CTRL_VOCABULARY)
        return vocabulary.get(self._issue.journal.ctrl_vocabulary, 'No Descriptor')

    def __unicode__(self):
        rows = '\n'.join([
            self.legend,
            self.issue_meta,
            self.sections,
            self.sections_ids,
            self.ctrl_vocabulary,
            self.norma,
            '',
        ])
        return rows


class JournalStandards(L10nIssue):

    def journal_meta(self):
        return '#'.join([
            self.issn,
            self.abbrev_title,
            self.norma,
            self.issn,
            self.tematic_area,
            self.medline_title,
            self.codigo_medline,
            self.title,
            self.acron,
            self.print_issn,
            self.online_issn,
            ])

    def __unicode__(self):
        rows = '\n'.join([self.journal_meta])

        return rows


def generate(journal, issue):
    export_automata = Automata(journal)
    export_issue = Issue(issue)
    export_l10n_issue = L10nIssue(journal, issue)
    # export_journal_standard = JournalStandards(journal, issue)

    try:
        l10n_issue = unicode(export_l10n_issue)
        packmeta = [
            ('automata.mds', unicode(export_automata)),
            ('issue.mds', unicode(export_issue)),
            ('en_issue.mds', l10n_issue),
            ('es_issue.mds', l10n_issue),
            ('pt_issue.mds', l10n_issue),
            # ('journal_standards.txt', unicode(export_journal_standard)),
        ]
    except AttributeError as exc:
        raise GenerationError('it was impossible to generate the package for %s. %s' % (journal.pk, exc))
    else:
        pkg = bundle.Bundle(*packmeta)

    pkg_filename = bundle.generate_filename('markupfiles')

    pkg.deploy(MEDIA_ROOT + pkg_filename)
    return MEDIA_URL + pkg_filename
