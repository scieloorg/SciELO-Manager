import caching.base
import datetime
import logging

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import SuspiciousOperation, ValidationError

from articletrack import modelmanagers
from journalmanager.models import Journal

logger = logging.getLogger(__name__)

MSG_WORKFLOW_ACCEPTED = 'Checkin Accepted'
MSG_WORKFLOW_REJECTED = 'Checkin Rejected'
MSG_WORKFLOW_REVIEWED = 'Checkin Reviewed'
MSG_WORKFLOW_SENT_TO_PENDIG = 'Checkin Sent to Pending'
MSG_WORKFLOW_SENT_TO_REVIEW = 'Checkin Sent to Review'


class Notice(caching.base.CachingMixin, models.Model):

    checkin = models.ForeignKey('Checkin', related_name='notices')

    stage = models.CharField(max_length=64)
    checkpoint = models.CharField(max_length=64)
    message = models.CharField(max_length=512, null=False)
    status = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        permissions = (("list_notice", "Can list Notices"),)

    def __unicode__(self):
        return u"%s %s (%s) for checkin: %s" % (self.stage, self.checkpoint, self.status, self.checkin)


CHECKIN_STATUS_CHOICES = (
    ('pending', _('Pending')),
    ('review', _('Review')),
    ('accepted', _('Accepted')),
    ('rejected', _('Rejected')),
)


class Checkin(caching.base.CachingMixin, models.Model):

    # Custom Managers
    objects = models.Manager()
    userobjects = modelmanagers.CheckinManager()

    attempt_ref = models.CharField(max_length=32)
    package_name = models.CharField(max_length=128)
    uploaded_at = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    article = models.ForeignKey('Article', related_name='checkins', null=True)
    status = models.CharField(_(u'Status'), choices=CHECKIN_STATUS_CHOICES, max_length=10, default='pending')

    accepted_by = models.ForeignKey(User, null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    reviewed_by = models.ForeignKey(User, related_name='checkins_reviewed', null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    rejected_by = models.ForeignKey(User, related_name='checkins_rejected', null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejected_cause = models.CharField(_(u'Cause of Rejection'), max_length=128, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        permissions = (("list_checkin", "Can list Checkin"),)

    @property
    def get_error_level(self):
        if self.notices.filter(status__iexact="error").count() > 0:
            return "error"
        elif self.notices.filter(status__iexact="warning").count() > 0:
            return "warning"
        else:
            return "ok"

    @property
    def get_newest_checkin(self):
        return self.article.checkins.order_by('-uploaded_at')[0]

    @property
    def is_newest_checkin(self):
        return self.pk == self.get_newest_checkin.pk

    def is_accepted(self):
        """
        Checks if this checkin has been accepted
        """
        return self.status == 'accepted' and bool(self.accepted_by and self.accepted_at)

    def is_reviewed(self):
        """
        Checks if this checkin has been reviewed
        """
        return self.status == 'review' and bool(self.reviewed_by and self.reviewed_at)

    def is_rejected(self):
        """
        Checks if this checkin has been rejected
        """
        return self.status == 'rejected'

    def can_be_send_to_pending(self):
        """
        Check the conditions to enable: 'send to pending'  action.
        Return True if this checkin have status ``rejected``
        does not exist another checkin accepted for the related article.
        """
        return self.status == 'rejected' and not self.article.is_accepted()

    def can_be_send_to_review(self):
        """
        Check the conditions to enable: 'send to review'  action.
        Return True if this checkin have status ``pending`` and have no errors and
        does not exist another checkin accepted for the related article.
        """
        return self.status == 'pending' and self.get_error_level != 'error' and not self.article.is_accepted()

    def can_be_reviewed(self):
        """
        Check the conditions to enable the process of 'review' action.
        Return True if this checkin is in status ``pending`` and have no errors and
        does not exist another checkin accepted for the related article.
        """
        return self.status == 'review' and self.get_error_level != 'error' and not self.article.is_accepted()

    def can_be_accepted(self):
        """
        Check the conditions to enable the process of 'accept' action.
        Return True if this checkin is in status ``review`` and self.is_reviewed == True and
        does not exist another checkin accepted for the related article.
        """
        return self.status == 'review' and self.is_reviewed and not self.article.is_accepted()

    def can_be_rejected(self):
        """
        Return True if Checkin can be rejected.
        Only checkins with status 'review' can be rejected.
        """
        return self.status == 'review'

    def accept(self, responsible):
        """
        Accept the checkin as ready to be part of the collection.
        Change status of this checkin from 'review' to 'accepted'.

        Raises ValueError if self relates to an already accepted article or
        if the user `responsible` is not active or if exist any accepted article already.
        :param responsible: instance of django.contrib.auth.User
        """
        if not responsible.is_active:
            raise ValueError('User must be active')

        if self.article.is_accepted():
            raise ValueError('Cannot accept more than one checkin per article')
        elif self.can_be_accepted:
            self.accepted_by = responsible
            self.accepted_at = datetime.datetime.now()
            self.status = 'accepted'
            self.save()
            # log data for history
            log = CheckinWorflowLog()
            log.checkin = self
            log.status = self.status
            log.created_at = self.accepted_at
            log.user = responsible
            log.description = MSG_WORKFLOW_ACCEPTED
            log.save()
        else:
            raise ValueError('This checkin does not comply with the conditions to be accepted')

    def send_to_pending(self, responsible):
        """
        Send to pending list: change the status to 'pending' if self.can_be_send_to_pending == True else raise
        ValueError.

        Raises ValueError if self relates to an already accepted article or
        if the user `responsible` is not active or if exist any accepted article already.
        :param responsible: instance of django.contrib.auth.User
        """
        if not responsible.is_active:
            raise ValueError('User must be active')

        if self.article.is_accepted():
            raise ValueError('Cannot accept more than one checkin per article')
        elif self.can_be_send_to_pending:
            self.status = 'pending'
            self.save()
            # log data for history
            log = CheckinWorflowLog()
            log.checkin = self
            log.status = self.status
            log.created_at = datetime.datetime.now()
            log.user = responsible
            log.description = MSG_WORKFLOW_SENT_TO_PENDIG
            log.save()
        else:
            raise ValueError('This checkin does not comply with the conditions to change status to "review"')

    def send_to_review(self, responsible):
        """
        Send to review list: change the status to review if self.can_be_send_to_review == True else raise
        ValueError.

        Raises ValueError if self relates to an already accepted article or
        if the user `responsible` is not active or if exist any accepted article already.
        :param responsible: instance of django.contrib.auth.User
        """
        if not responsible.is_active:
            raise ValueError('User must be active')

        if self.article.is_accepted():
            raise ValueError('Cannot accept more than one checkin per article')
        elif self.can_be_send_to_review:
            self.status = 'review'
            self.save()
            # log data for history
            log = CheckinWorflowLog()
            log.checkin = self
            log.status = self.status
            log.created_at = datetime.datetime.now()
            log.user = responsible
            log.description = MSG_WORKFLOW_SENT_TO_REVIEW
            log.save()
        else:
            raise ValueError('This checkin does not comply with the conditions to change status to "review"')

    def do_review(self, responsible):
        """
        Checkin with status review, are filled with review information (saves reviewer and revisition data)

        Raises ValueError if self relates to an already accepted article or
        if the user `responsible` is not active or if exist any accepted article already.
        :param responsible: instance of django.contrib.auth.User
        """
        if not responsible.is_active:
            raise ValueError('User must be active')

        if self.article.is_accepted():
            raise ValueError('Cannot accept more than one checkin per article')
        elif self.can_be_reviewed:
            self.status = 'review'
            self.reviewed_by = responsible
            self.reviewed_at = datetime.datetime.now()
            self.save()
            # log data for history
            log = CheckinWorflowLog()
            log.checkin = self
            log.status = self.status
            log.created_at = self.reviewed_at
            log.user = responsible
            log.description = MSG_WORKFLOW_REVIEWED
            log.save()
        else:
            raise ValueError('This checkin does not comply with the conditions to be reviewed')

    def do_reject(self, responsible, cause):
        """
        Checkins that can_be_rejected == True, is changed to status == 'rejected'
        Must be saved the date, the responsible of the action and a cause of rejection.

        Raises ValueError if self relates to an already accepted article or
        if the user `responsible` is not active or if exist any accepted article already.
        :param responsible: instance of django.contrib.auth.User
        """
        if not responsible.is_active:
            raise ValueError('User must be active')

        if self.article.is_accepted():
            raise ValueError('Cannot accept more than one checkin per article')
        elif self.can_be_rejected:
            self.status = 'rejected'
            self.rejected_by = responsible
            self.rejected_at = datetime.datetime.now()
            self.rejected_cause = cause
            self.save()
            # log data for history
            log = CheckinWorflowLog()
            log.checkin = self
            log.status = self.status
            log.created_at = self.rejected_at
            log.user = responsible
            log.description = "%s. Rejected cause: %s" % (MSG_WORKFLOW_REJECTED, self.rejected_cause)
            log.save()
        else:
            raise ValueError('This checkin does not comply with the conditions to change status to "rejected"')

    def clean(self):
        # validation for status "accepted"
        if self.status == 'accepted' and not bool(self.accepted_by and self.accepted_at and self.reviewed_by and self.reviewed_at):
            raise ValidationError('Checkin with "accepted" status must have filled: "accepted_by", \
                "accepted_at", "reviewed_by" and "reviewed_at" fields.')

        if self.status == 'rejected' and not bool(self.rejected_by and self.rejected_at and self.rejected_cause):
            raise ValidationError('Checkin with "rejected" status must have filled: "rejected_by", \
                "rejected_at" and "reviewed_cause" fields.')

    def save(self, *args, **kwargs):
        if self.status == 'pending':
            # clear 'review' fields
            self.reviewed_by = None
            self.reviewed_at = None
            # clear 'accepted' fields
            self.accepted_by = None
            self.accepted_at = None
            # clear 'rejected' fields
            self.rejected_by = None
            self.rejected_at = None
            self.rejected_cause = None
        elif self.status == 'review':
            # clear 'accepted' fields
            self.accepted_by = None
            self.accepted_at = None
            # clear 'rejected' fields
            self.rejected_by = None
            self.rejected_at = None
            self.rejected_cause = None
        elif self.status == 'rejected':
            # clear 'review' fields
            self.reviewed_by = None
            self.reviewed_at = None
            # clear 'accepted' fields
            self.accepted_by = None
            self.accepted_at = None
        super(Checkin, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s [attept ref: %s]' % (self.package_name, self.attempt_ref)


class CheckinWorflowLog(caching.base.CachingMixin, models.Model):
    created_at = models.DateTimeField(_(u'Created at'), default=datetime.datetime.now)
    user = models.ForeignKey(User, related_name='checkin_log_responsible', null=True, blank=True)  # nullable in caso of (Celery's task) processing
    status = models.CharField(_(u'Status'), choices=CHECKIN_STATUS_CHOICES, max_length=10, default='pending')
    description = models.TextField(_(u'Description'), null=True, blank=True)
    checkin = models.ForeignKey(Checkin, related_name='checkin_worflow_logs')


class Article(caching.base.CachingMixin, models.Model):

    # Custom Managers
    objects = models.Manager()
    userobjects = modelmanagers.ArticleManager()

    journals = models.ManyToManyField(Journal, null=True, related_name='checkin_articles')
    article_title = models.CharField(max_length=512)
    articlepkg_ref = models.CharField(max_length=32)
    journal_title = models.CharField(max_length=256)
    issue_label = models.CharField(max_length=64)
    pissn = models.CharField(max_length=9, default='')
    eissn = models.CharField(max_length=9, default='')

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        permissions = (("list_article", "Can list Article"),)

    def is_accepted(self):
        """
        Checks if there is any checkin accepted for this article.
        """
        return self.checkins.filter(status='accepted').exists()

    def __unicode__(self):
        return "%s (ref: %s)" % (self.article_title, self.articlepkg_ref)


class Ticket(caching.base.CachingMixin, models.Model):

    # Custom Managers
    objects = models.Manager()
    userobjects = modelmanagers.TicketManager()

    started_at = models.DateTimeField(_("Started at"), auto_now=True)
    finished_at = models.DateTimeField(_("Finished at"), null=True, blank=True)
    author = models.ForeignKey(User, related_name='tickets')
    title = models.CharField(_("Title"), max_length=256)
    message = models.TextField(_("Message"))
    article = models.ForeignKey(Article, related_name='tickets')

    class Meta:
        verbose_name = _(u'Ticket')
        verbose_name_plural = _(u'Tickets')
        permissions = (("list_ticket", "Can list Ticket"),)
        ordering = ['started_at']

    def __unicode__(self):
        return u"%s - %s" % (self.pk, self.title)

    @property
    def is_open(self):
        return self.finished_at is None


class Comment(caching.base.CachingMixin, models.Model):
    """
        Represents a comment related to a Ticket
    """
    # Custom Managers
    objects = models.Manager()
    userobjects = modelmanagers.CommentManager()

    created_at = models.DateTimeField(_(u"Creation date"), auto_now_add=True)
    updated_at = models.DateTimeField(_(u"Updated date"), auto_now=True)
    author = models.ForeignKey(User, related_name='comments_author')
    ticket = models.ForeignKey(Ticket, related_name='comments')
    message = models.TextField(_(u"Message"))

    class Meta:
        verbose_name = _(u'Comment')
        verbose_name_plural = _(u'Comments')
        ordering = ['created_at']
        permissions = (("list_comment", "Can list Comment"),)

    def __unicode__(self):
        return u"%s (ticket: %s)" % (self.pk, self.ticket)
