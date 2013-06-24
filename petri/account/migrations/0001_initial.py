# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table('account_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('email_notifications', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('email_digest', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('allow_discuss', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_official', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_announce', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('is_leader', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_moderator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('chapter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chapter.Chapter'], null=True)),
            ('invitation_count', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('leader', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='mentees', null=True, to=orm['auth.User'])),
            ('gravatar_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('facebook_url', self.gf('django.db.models.fields.URLField')(default='', max_length=200, null=True, blank=True)),
            ('twitter_url', self.gf('django.db.models.fields.URLField')(default='', max_length=200, null=True, blank=True)),
            ('linkedin_url', self.gf('django.db.models.fields.URLField')(default='', max_length=200, null=True, blank=True)),
            ('github_url', self.gf('django.db.models.fields.URLField')(default='', max_length=200, null=True, blank=True)),
            ('dribble_url', self.gf('django.db.models.fields.URLField')(default='', max_length=200, null=True, blank=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('show_guide', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('account', ['UserProfile'])

        # Adding M2M table for field starred on 'UserProfile'
        m2m_table_name = db.shorten_name('account_userprofile_starred')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['account.userprofile'], null=False)),
            ('bulletin', models.ForeignKey(orm['bulletin.bulletin'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'bulletin_id'])

        # Adding M2M table for field skills on 'UserProfile'
        m2m_table_name = db.shorten_name('account_userprofile_skills')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['account.userprofile'], null=False)),
            ('skill', models.ForeignKey(orm['tag.skill'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'skill_id'])

        # Adding M2M table for field affiliations on 'UserProfile'
        m2m_table_name = db.shorten_name('account_userprofile_affiliations')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['account.userprofile'], null=False)),
            ('affiliation', models.ForeignKey(orm['tag.affiliation'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'affiliation_id'])

        # Adding M2M table for field initiatives on 'UserProfile'
        m2m_table_name = db.shorten_name('account_userprofile_initiatives')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['account.userprofile'], null=False)),
            ('initiative', models.ForeignKey(orm['tag.initiative'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'initiative_id'])

        # Adding model 'Invitation'
        db.create_table('account_invitation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(default='f0ff42812ee5eb40', max_length=16)),
            ('sponsor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('chapter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chapter.Chapter'])),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('target', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
        ))
        db.send_create_signal('account', ['Invitation'])


    def backwards(self, orm):
        # Deleting model 'UserProfile'
        db.delete_table('account_userprofile')

        # Removing M2M table for field starred on 'UserProfile'
        db.delete_table(db.shorten_name('account_userprofile_starred'))

        # Removing M2M table for field skills on 'UserProfile'
        db.delete_table(db.shorten_name('account_userprofile_skills'))

        # Removing M2M table for field affiliations on 'UserProfile'
        db.delete_table(db.shorten_name('account_userprofile_affiliations'))

        # Removing M2M table for field initiatives on 'UserProfile'
        db.delete_table(db.shorten_name('account_userprofile_initiatives'))

        # Deleting model 'Invitation'
        db.delete_table('account_invitation')


    models = {
        'account.invitation': {
            'Meta': {'object_name': 'Invitation'},
            'chapter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chapter.Chapter']"}),
            'code': ('django.db.models.fields.CharField', [], {'default': "'8bc1d6a2832ee6cd'", 'max_length': '16'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sponsor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'target': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'})
        },
        'account.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'affiliations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tag.Affiliation']", 'symmetrical': 'False', 'blank': 'True'}),
            'allow_announce': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_discuss': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_official': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'chapter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chapter.Chapter']", 'null': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'dribble_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email_digest': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'email_notifications': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'facebook_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'github_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'gravatar_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiatives': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tag.Initiative']", 'symmetrical': 'False', 'blank': 'True'}),
            'invitation_count': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'is_leader': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_moderator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'leader': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'mentees'", 'null': 'True', 'to': "orm['auth.User']"}),
            'linkedin_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'show_guide': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'skills': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tag.Skill']", 'symmetrical': 'False', 'blank': 'True'}),
            'starred': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['bulletin.Bulletin']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'twitter_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
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
        'bulletin.bulletin': {
            'Meta': {'object_name': 'Bulletin'},
            'actual_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'chapter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chapter.Chapter']"}),
            'content': ('sanitizer.models.SanitizedTextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'followed_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'following'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_generated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_global': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_official': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'moderated_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'moderated'", 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'to': "orm['auth.User']"}),
            'promoted_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'promoted'", 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"}),
            'promoted_on': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'related': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['bulletin.Bulletin']", 'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'bulletins'", 'symmetrical': 'False', 'to': "orm['tag.Tag']"}),
            'thread_id': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'users_mentioned': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mentioned'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'users_notified': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'notified'", 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'chapter.chapter': {
            'Meta': {'object_name': 'Chapter'},
            'base_color': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'custom_css': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'founded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'founder': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'founded_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.TextField', [], {}),
            'markup': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'project.project': {
            'Meta': {'object_name': 'Project', '_ormbases': ['bulletin.Bulletin']},
            'bulletin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['bulletin.Bulletin']", 'unique': 'True', 'primary_key': 'True'}),
            'picture': ('django.db.models.fields.URLField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'tag.affiliation': {
            'Meta': {'object_name': 'Affiliation', '_ormbases': ['tag.Tag']},
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'tag_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['tag.Tag']", 'unique': 'True', 'primary_key': 'True'})
        },
        'tag.initiative': {
            'Meta': {'object_name': 'Initiative', '_ormbases': ['tag.Tag']},
            'project': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['project.Project']", 'unique': 'True'}),
            'tag_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['tag.Tag']", 'unique': 'True', 'primary_key': 'True'})
        },
        'tag.skill': {
            'Meta': {'object_name': 'Skill', '_ormbases': ['tag.Tag']},
            'tag_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['tag.Tag']", 'unique': 'True', 'primary_key': 'True'})
        },
        'tag.tag': {
            'Meta': {'object_name': 'Tag'},
            'actual_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['account']