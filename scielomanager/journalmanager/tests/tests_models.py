# coding: utf-8
from django.test import TestCase
from django_factory_boy import auth

from .modelfactories import (
    IssueFactory,
    UserProfileFactory,
    SectionFactory,
    LanguageFactory,
    SectionTitleFactory,
    JournalFactory,
)


class SectionTests(TestCase):

    def test_section_not_being_used(self):
        section = SectionFactory.build()
        self.assertFalse(section.is_used())

    def test_section_bound_to_a_journal(self):
        issue = IssueFactory.create()
        section = issue.section.all()[0]

        self.assertTrue(section.is_used())

    def test_actual_code_is_the_instance_pk(self):
        section = SectionFactory.create()
        self.assertEqual(section.pk, section.actual_code)

    def test_actual_code_must_raise_attributeerror_for_unsaved_instances(self):
        section = SectionFactory.build()
        self.assertRaises(AttributeError, section.actual_code)

    def test_unicode_repr_with_only_one_language(self):
        section_title = SectionTitleFactory.create()
        expected = 'Artigos Originais'

        self.assertEqual(unicode(section_title.section), expected)

    def test_unicode_repr_with_two_languages(self):
        language = LanguageFactory.create(iso_code='en', name='english')
        section_title = SectionTitleFactory.create()
        section_title_en = SectionTitleFactory.build(
            title='Original Articles',
            language=language
        )
        section_title_en.section = section_title.section
        section_title_en.save()

        expected = 'Original Articles / Artigos Originais'

        self.assertEqual(unicode(section_title.section), expected)


class UserProfileTests(TestCase):

    def test_gravatar_id_generation(self):
        profile = UserProfileFactory.build(email='foo@bar.org')
        expected_gravatar_id = '24191827e60cdb49a3d17fb1befe951b'

        self.assertEqual(profile.gravatar_id, expected_gravatar_id)

    def test_gravatar_url(self):
        expected_url = 'https://secure.gravatar.com/avatar/24191827e60cdb49a3d17fb1befe951b?s=25&d=mm'
        profile = UserProfileFactory.build(email='foo@bar.org')

        self.assertEqual(profile.avatar_url, expected_url)


class IssueTests(TestCase):

    def test_identification_for_suppl_volume(self):
        issue = IssueFactory.create(number='1', suppl_volume='2')
        expected = u'1 suppl.2'

        self.assertEqual(issue.identification, expected)

    def test_identification_for_number(self):
        issue = IssueFactory.create(number='1')
        expected = u'1'

        self.assertEqual(issue.identification, expected)

    def test_identification_for_number_with_sublevels(self):
        issue = IssueFactory.create(number='1a')
        expected = u'1a'

        self.assertEqual(issue.identification, expected)

    def test_identification_for_suppl_number(self):
        issue = IssueFactory.create(number='1', suppl_number='2')
        expected = u'1 suppl.2'

        self.assertEqual(issue.identification, expected)

    def test_identification_for_press_release(self):
        issue = IssueFactory.create(number='1', is_press_release=True)
        expected = u'1 pr'

        self.assertEqual(issue.identification, expected)

    def test_identification_for_ahead(self):
        issue = IssueFactory.create(number='ahead')
        expected = u'ahead of print'

        self.assertEqual(issue.identification, expected)

    def test_identification_for_special(self):
        issue = IssueFactory.create(number='spe')
        expected = u'special'

        self.assertEqual(issue.identification, expected)

    def test_unicode_representation(self):
        issue = IssueFactory.create(volume='2', number='1', suppl_number='2')
        expected = u'2 (1 suppl.2)'

        self.assertEqual(unicode(issue), expected)

    def test_publication_date(self):
        issue = IssueFactory.create()
        expected = '9 / 11 - 2012'

        self.assertEqual(issue.publication_date, expected)


class LanguageTests(TestCase):

    def test_the_unicode_repr_must_be_in_current_language(self):
        # todo: learn a good way to change the current language of the app
        # in order to check the unicode value translated.
        language = LanguageFactory.build(name='portuguese')
        self.assertEqual(unicode(language), u'portuguese')


class JournalTests(TestCase):

    def test_changing_publication_status(self):
        user = auth.UserF()
        journal = JournalFactory.create()
        journal.change_publication_status(status=u'deceased',
            reason=u'baz', changed_by=user)

        self.assertEqual(journal.pub_status, u'deceased')
        self.assertEqual(journal.pub_status_reason, u'baz')
        self.assertEqual(journal.pub_status_changed_by, user)

    def test_issues_grid_with_numerical_issue_numbers(self):
        journal = JournalFactory.create()
        for i in range(5):
            journal.issue_set.add(IssueFactory.create(volume=9,
                publication_year=2012))

        grid = journal.issues_as_grid()

        self.assertTrue(2012 in grid)
        self.assertTrue('9' in grid[2012])
        self.assertEqual(len(grid[2012]['9']['numbers']), 5)

    def test_issues_grid_with_alphabetical_issue_numbers(self):
        journal = JournalFactory.create()
        for i in range(5):
            if i % 2:
                kwargs = {'volume': 9, 'publication_year': 2012}
            else:
                kwargs = {'volume': 9, 'publication_year': 2012, 'number': 'ahead'}

            journal.issue_set.add(IssueFactory.create(**kwargs))

        grid = journal.issues_as_grid()

        self.assertTrue(2012 in grid)
        self.assertTrue('9' in grid[2012])
        self.assertTrue('numbers' in grid[2012]['9'])
        self.assertTrue('others' in grid[2012]['9'])
        self.assertEqual(len(grid[2012]['9']['numbers']), 2)
        self.assertEqual(len(grid[2012]['9']['others']), 3)

    def test_issues_grid_with_unavailable_issues(self):
        journal = JournalFactory.create()
        for i in range(5):
            journal.issue_set.add(IssueFactory.create(volume=9,
                publication_year=2012))

        grid = journal.issues_as_grid(is_available=False)

        self.assertFalse(grid)
