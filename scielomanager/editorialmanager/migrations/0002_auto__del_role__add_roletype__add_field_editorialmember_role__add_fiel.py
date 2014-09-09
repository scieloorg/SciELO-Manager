# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Role'
        db.delete_table('editorialmanager_role')

        # Adding model 'RoleType'
        db.create_table('editorialmanager_roletype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('role_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('editorialmanager', ['RoleType'])

        # Adding M2M table for field members on 'EditorialBoard'
        m2m_table_name = db.shorten_name('editorialmanager_editorialboard_members')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('editorialboard', models.ForeignKey(orm['editorialmanager.editorialboard'], null=False)),
            ('editorialmember', models.ForeignKey(orm['editorialmanager.editorialmember'], null=False))
        ))
        db.create_unique(m2m_table_name, ['editorialboard_id', 'editorialmember_id'])

        # Adding field 'EditorialMember.role'
        db.add_column('editorialmanager_editorialmember', 'role',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['editorialmanager.RoleType']),
                      keep_default=False)

        # Adding field 'EditorialMember.first_name'
        db.add_column('editorialmanager_editorialmember', 'first_name',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=256),
                      keep_default=False)

        # Adding field 'EditorialMember.last_name'
        db.add_column('editorialmanager_editorialmember', 'last_name',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=256),
                      keep_default=False)

        # Adding field 'EditorialMember.email'
        db.add_column('editorialmanager_editorialmember', 'email',
                      self.gf('django.db.models.fields.EmailField')(default=None, max_length=75),
                      keep_default=False)

        # Adding field 'EditorialMember.institution'
        db.add_column('editorialmanager_editorialmember', 'institution',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EditorialMember.link_cv'
        db.add_column('editorialmanager_editorialmember', 'link_cv',
                      self.gf('django.db.models.fields.URLField')(default=None, max_length=200),
                      keep_default=False)

        # Adding field 'EditorialMember.city'
        db.add_column('editorialmanager_editorialmember', 'city',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EditorialMember.state'
        db.add_column('editorialmanager_editorialmember', 'state',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EditorialMember.country'
        db.add_column('editorialmanager_editorialmember', 'country',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'Role'
        db.create_table('editorialmanager_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('editorialmanager', ['Role'])

        # Deleting model 'RoleType'
        db.delete_table('editorialmanager_roletype')

        # Removing M2M table for field members on 'EditorialBoard'
        db.delete_table(db.shorten_name('editorialmanager_editorialboard_members'))

        # Deleting field 'EditorialMember.role'
        db.delete_column('editorialmanager_editorialmember', 'role_id')

        # Deleting field 'EditorialMember.first_name'
        db.delete_column('editorialmanager_editorialmember', 'first_name')

        # Deleting field 'EditorialMember.last_name'
        db.delete_column('editorialmanager_editorialmember', 'last_name')

        # Deleting field 'EditorialMember.email'
        db.delete_column('editorialmanager_editorialmember', 'email')

        # Deleting field 'EditorialMember.institution'
        db.delete_column('editorialmanager_editorialmember', 'institution')

        # Deleting field 'EditorialMember.link_cv'
        db.delete_column('editorialmanager_editorialmember', 'link_cv')

        # Deleting field 'EditorialMember.city'
        db.delete_column('editorialmanager_editorialmember', 'city')

        # Deleting field 'EditorialMember.state'
        db.delete_column('editorialmanager_editorialmember', 'state')

        # Deleting field 'EditorialMember.country'
        db.delete_column('editorialmanager_editorialmember', 'country')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'editorialmanager.editorialboard': {
            'Meta': {'object_name': 'EditorialBoard'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['journalmanager.Issue']"}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['editorialmanager.EditorialMember']", 'symmetrical': 'False'})
        },
        'editorialmanager.editorialmember': {
            'Meta': {'object_name': 'EditorialMember'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'link_cv': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['editorialmanager.RoleType']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        'editorialmanager.roletype': {
            'Meta': {'object_name': 'RoleType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role_name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'journalmanager.collection': {
            'Meta': {'ordering': "['name']", 'object_name': 'Collection'},
            'acronym': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '16', 'blank': 'True'}),
            'address': ('django.db.models.fields.TextField', [], {}),
            'address_complement': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'address_number': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'collection': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'user_collection'", 'to': "orm['auth.User']", 'through': "orm['journalmanager.UserCollections']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'name_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'})
        },
        'journalmanager.institution': {
            'Meta': {'ordering': "['name']", 'object_name': 'Institution'},
            'acronym': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '16', 'blank': 'True'}),
            'address': ('django.db.models.fields.TextField', [], {}),
            'address_complement': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'address_number': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'cel': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'complement': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_trashed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'})
        },
        'journalmanager.issue': {
            'Meta': {'ordering': "('created', 'id')", 'object_name': 'Issue'},
            'cover': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ctrl_vocabulary': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'editorial_standard': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_marked_up': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_trashed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'journal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['journalmanager.Journal']"}),
            'label': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'publication_end_month': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'publication_start_month': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'publication_year': ('django.db.models.fields.IntegerField', [], {}),
            'section': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['journalmanager.Section']", 'symmetrical': 'False', 'blank': 'True'}),
            'spe_text': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'suppl_text': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'total_documents': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'regular'", 'max_length': '15'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'use_license': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['journalmanager.UseLicense']", 'null': 'True'}),
            'volume': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'})
        },
        'journalmanager.journal': {
            'Meta': {'ordering': "('title', 'id')", 'object_name': 'Journal'},
            'abstract_keyword_languages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'abstract_keyword_languages'", 'symmetrical': 'False', 'to': "orm['journalmanager.Language']"}),
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'collections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['journalmanager.Collection']", 'through': "orm['journalmanager.Membership']", 'symmetrical': 'False'}),
            'copyrighter': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'cover': ('scielomanager.custom_fields.ContentTypeRestrictedFileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'enjoy_creator'", 'to': "orm['auth.User']"}),
            'ctrl_vocabulary': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'current_ahead_documents': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'editor_address': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'editor_address_city': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'editor_address_country': ('scielo_extensions.modelfields.CountryField', [], {'max_length': '2'}),
            'editor_address_state': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'editor_address_zip': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'editor_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'editor_name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'editor_phone1': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'editor_phone2': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'editorial_standard': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'eletronic_issn': ('django.db.models.fields.CharField', [], {'max_length': '9', 'db_index': 'True'}),
            'final_num': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'final_vol': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'final_year': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index_coverage': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'init_num': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'init_vol': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'init_year': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'is_indexed_aehci': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_indexed_scie': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_indexed_ssci': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_trashed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['journalmanager.Language']", 'symmetrical': 'False'}),
            'logo': ('scielomanager.custom_fields.ContentTypeRestrictedFileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'medline_code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'medline_title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'national_code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'other_previous_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'previous_ahead_documents': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'previous_title': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'prev_title'", 'null': 'True', 'to': "orm['journalmanager.Journal']"}),
            'print_issn': ('django.db.models.fields.CharField', [], {'max_length': '9', 'db_index': 'True'}),
            'pub_level': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'publication_city': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'publisher_country': ('scielo_extensions.modelfields.CountryField', [], {'max_length': '2'}),
            'publisher_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'publisher_state': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'scielo_issn': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'secs_code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'db_index': 'True'}),
            'sponsor': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'journal_sponsor'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['journalmanager.Sponsor']"}),
            'study_areas': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'journals_migration_tmp'", 'null': 'True', 'to': "orm['journalmanager.StudyArea']"}),
            'subject_categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'journals'", 'null': 'True', 'to': "orm['journalmanager.SubjectCategory']"}),
            'subject_descriptors': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            'title_iso': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            'twitter_user': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url_journal': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'url_online_submission': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'use_license': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['journalmanager.UseLicense']"})
        },
        'journalmanager.language': {
            'Meta': {'ordering': "['name']", 'object_name': 'Language'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'journalmanager.membership': {
            'Meta': {'unique_together': "(('journal', 'collection'),)", 'object_name': 'Membership'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['journalmanager.Collection']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['journalmanager.Journal']"}),
            'reason': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'since': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'inprogress'", 'max_length': '16'})
        },
        'journalmanager.section': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Section'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '21', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_trashed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'journal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['journalmanager.Journal']"}),
            'legacy_code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'journalmanager.sponsor': {
            'Meta': {'ordering': "['name']", 'object_name': 'Sponsor', '_ormbases': ['journalmanager.Institution']},
            'collections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['journalmanager.Collection']", 'symmetrical': 'False'}),
            'institution_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['journalmanager.Institution']", 'unique': 'True', 'primary_key': 'True'})
        },
        'journalmanager.studyarea': {
            'Meta': {'object_name': 'StudyArea'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'study_area': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'journalmanager.subjectcategory': {
            'Meta': {'object_name': 'SubjectCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'})
        },
        'journalmanager.uselicense': {
            'Meta': {'ordering': "['license_code']", 'object_name': 'UseLicense'},
            'disclaimer': ('django.db.models.fields.TextField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'license_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'reference_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'journalmanager.usercollections': {
            'Meta': {'unique_together': "(('user', 'collection'),)", 'object_name': 'UserCollections'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['journalmanager.Collection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_manager': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['editorialmanager']