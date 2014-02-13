import datetime
from waffle.decorators import waffle_flag
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from . import models
from scielomanager.tools import get_paginated, get_referer_view
from articletrack.forms import CommentMessageForm, TicketForm


AUTHZ_REDIRECT_URL = '/accounts/unauthorized/'
MSG_FORM_SAVED = _('Saved.')
MSG_FORM_SAVED_PARTIALLY = _('Saved partially. You can continue to fill in this form later.')
MSG_FORM_MISSING = _('There are some errors or missing data.')
MSG_DELETE_PENDED = _('The pended form has been deleted.')


@waffle_flag('articletrack')
@permission_required('articletrack.list_checkin', login_url=AUTHZ_REDIRECT_URL)
def checkin_index(request):

    checkins = models.Checkin.userobjects.active()

    objects = get_paginated(checkins, request.GET.get('page', 1))

    return render_to_response(
        'articletrack/checkin_list.html',
        {
            'checkins': objects,
        },
        context_instance=RequestContext(request)
    )


@waffle_flag('articletrack')
@permission_required('articletrack.list_checkin', login_url=AUTHZ_REDIRECT_URL)
def checkin_history(request, article_id):
    try:
        article = models.Article.userobjects.active().get(pk=article_id)
    except models.Article.DoesNotExist:
        raise Http404

    objects = get_paginated(article.checkins.all(), request.GET.get('page', 1))

    return render_to_response(
        'articletrack/history.html',
        {
            'checkins': objects,
            'first_article': article,
        },
        context_instance=RequestContext(request)
    )


@waffle_flag('articletrack')
@permission_required('articletrack.list_notice', login_url=AUTHZ_REDIRECT_URL)
def notice_detail(request, checkin_id):

    notices = models.Notice.objects.filter(checkin=checkin_id)
    checkin = models.Checkin.userobjects.active().get(pk=checkin_id)

    objects = get_paginated(notices, request.GET.get('page', 1))

    tickets = models.Ticket.userobjects.active()
    opened_tickets = tickets.filter(finished_at__isnull=True)
    closed_tickets = tickets.filter(finished_at__isnull=False)

    return render_to_response(
        'articletrack/notice_detail.html',
        {
            'notices': objects,
            'checkin': checkin,
            'opened_tickets': opened_tickets,
            'closed_tickets': closed_tickets,
        },
        context_instance=RequestContext(request)
    )


@waffle_flag('articletrack')
@permission_required('articletrack.list_ticket', login_url=AUTHZ_REDIRECT_URL)
def ticket_list(request):

    tickets = models.Ticket.userobjects.active()
    objects = get_paginated(tickets, request.GET.get('page', 1))
    
    return render_to_response(
        'articletrack/ticket_list.html',
        {
            'tickets': objects,
        },
        context_instance=RequestContext(request)
    )


@waffle_flag('articletrack')
@permission_required('articletrack.list_ticket', login_url=AUTHZ_REDIRECT_URL)
def ticket_detail(request, ticket_id, template_name='articletrack/ticket_detail.html'):

    ticket = models.Ticket.objects.get(pk=ticket_id)
    comment_form = CommentMessageForm()
    context = {
        'ticket': ticket,
        'form': comment_form,
    }

    if request.method == "POST":

        comment_form = CommentMessageForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.ticket = ticket
            comment.save()
            messages.info(request, MSG_FORM_SAVED)
            return render_to_response(
                template_name,
                context,
                context_instance=RequestContext(request)
            )

    return render_to_response(
        template_name,
        context,
        context_instance=RequestContext(request)
    )


@waffle_flag('articletrack')
@permission_required('articletrack.change_ticket', login_url=AUTHZ_REDIRECT_URL)
def ticket_close(request, ticket_id):

    ticket = models.Ticket.objects.get(pk=ticket_id)
    if not ticket.is_open:
        messages.info(request, _("Ticket are already closed"))
        return HttpResponseRedirect(reverse('ticket_detail', args=[ticket.id]))

    ticket.finished_at = datetime.datetime.now()
    ticket.save()
    messages.info(request, MSG_FORM_SAVED)

    referer = get_referer_view(request)
    return HttpResponseRedirect(referer)


@waffle_flag('articletrack')
@permission_required('articletrack.add_ticket', login_url=AUTHZ_REDIRECT_URL)
def ticket_add(request, checkin_id, template_name='articletrack/ticket_add.html'):

    checkin = models.Checkin.userobjects.active().get(pk=checkin_id)
    ticket_form = TicketForm()
    context = {
        'checkin': checkin,
        'form': ticket_form,
    }

    if request.method == "POST":

        ticket_form = TicketForm(request.POST)

        if ticket_form.is_valid():

            ticket = ticket_form.save(commit=False)
            ticket.author = request.user
            ticket.article = checkin.article
            ticket.save()
            
            messages.info(request, MSG_FORM_SAVED)
            return HttpResponseRedirect(reverse('ticket_detail', args=[ticket.id]))

    return render_to_response(
        template_name,
        context,
        context_instance=RequestContext(request)
    )


@waffle_flag('articletrack')
@permission_required('articletrack.change_ticket', login_url=AUTHZ_REDIRECT_URL)
def ticket_edit(request, ticket_id, template_name='articletrack/ticket_edit.html'):

    ticket = models.Ticket.userobjects.active().get(pk=ticket_id)
    if not ticket.is_open:
        messages.info(request, _("Closed ticket can't be edited"))
        return HttpResponseRedirect(reverse('ticket_detail', args=[ticket.pk]))

    ticket_form = TicketForm(instance=ticket)
    context = {
        'form': ticket_form,
        'ticket': ticket,
    }

    if request.method == "POST":

        ticket_form = TicketForm(request.POST, instance=ticket)

        if ticket_form.is_valid():

            ticket = ticket_form.save()
            
            messages.info(request, MSG_FORM_SAVED)
            return HttpResponseRedirect(reverse('ticket_detail', args=[ticket.pk]))
        

    return render_to_response(
        template_name,
        context,
        context_instance=RequestContext(request)
    )
