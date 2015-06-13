from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.conf import settings as django_settings
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from talk.models import Message, Thread, MessageIndex, Settings
from talk.forms import MessageForm, ThreadForm
from talk.utils import get_page
import json


def new_message_count(request):
    if not request.user.is_authenticated():
        raise Http404
    count = MessageIndex.objects.count_unread(request.user)
    return HttpResponse(count, content_type='text/plain')


def get_threads(request):
    query = request.GET.get('query')
    if query:
        threads = Thread.objects.filter(
            users=request.user
        ).filter(
            Q(users__username__icontains=query) |
            Q(messages__body__icontains=query)
        ).order_by(
            '-updated_at'
        ).distinct()
    else:
        threads = Thread.objects.filter(
            users=request.user
        ).order_by(
            '-updated_at'
        ).distinct()

    for thread in threads:
        thread.others = thread.other_users(request.user)

    return threads


@login_required
def view_thread(request, thread_id=None):
    cache.set('in_chat_%s' % request.user.id,
        timezone.localtime(timezone.now()),
        getattr(django_settings, 'USER_IN_CHAT_TIMEOUT', 20)
    )

    threads = get_threads(request)

    if threads and not thread_id:
        return redirect('view_thread', thread_id=threads.all()[0].id)

    if thread_id:
        try:
            thread = threads.get(id=thread_id)
            if not request.user in thread.users.all():
                return redirect('index')

            thread.others = thread.other_users(request.user)
            index = MessageIndex.objects.filter(thread=thread).filter(user=request.user)
        except:
            raise Http404
    else:
        thread = None
        index = None

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid() and thread:
            message = form.save(commit=False)
            message.author = request.user
            message.save()
            for user in thread.users.distinct():
                index = MessageIndex(message=message, thread=thread, user=user)
                index.save(request=request)
    else:
        form = MessageForm()

    if request.is_ajax():
        index = MessageIndex.objects.filter(thread=thread)

        user_states = {}
        for i in index.exclude(message__author=request.user):
            if i.user_in_chat():
                user_states[i.message.author.id] = 'inchat'
            elif i.user_online():
                user_states[i.message.author.id] = 'idle'
            else:
                user_states[i.message.author.id] = 'away'

        index_new = list(index.filter(user=request.user).filter(new=True))
        context = {
            'index': index_new,
            'user_states': user_states,
        }

        index.filter(user=request.user).update(new=False)
        return render(request, 'talk/messages.html', context)

    if thread:
        thread.messageindex_set.filter(user=request.user).update(new=False)

    context = {
        'threads': get_page(request, threads),
        'thread': thread,
        'index': index,
        'form': form,
        'new': False,
    }
    return render(request, 'talk/index.html', context)


@login_required
def new_thread(request):
    cache.set('in_chat_%s' % request.user.id,
        timezone.localtime(timezone.now()),
        getattr(django_settings, 'USER_IN_CHAT_TIMEOUT', 20)
    )

    thread = None
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            recipients = [r.strip() for r in form.cleaned_data['recipients'].split(',')]
            users = [request.user]

            for recipient in recipients:
                try:
                    user = get_user_model().objects.get(username=recipient)
                    users.append(user)
                except:
                    pass

            thread = Thread()
            thread.save()

            body = form.cleaned_data['body']
            message = Message(body=body, author=request.user)
            message.save()

            for user in list(set(users)):
                index = MessageIndex(message=message, thread=thread, user=user)
                index.new = (user != request.user)
                index.save(request=request)

            return redirect('view_thread', thread_id=thread.id)
    else:
        form = ThreadForm(initial={'recipients': request.GET.get('recipients')})

    context = {
        'threads': get_page(request, get_threads(request)),
        'thread': thread,
        'form': form,
        'new': True,
    }
    return render(request, 'talk/index.html', context)


def api(request):
    return HttpResponse(json.dumps({ 'status': 'ok' }), content_type='application/json')


def thread_search(request):
    context = {
        'threads': get_page(request, get_threads(request))
    }
    return render(request, 'talk/threads.html', context)


def settings(request):
    response = { 'status': 'ok' }
    if request.method == 'POST':
        user_id = request.POST.get('user_id', None)
        try:
            user = get_user_model().objects.get(id=user_id)
        except:
            response = { 'status': 'unknown user' }

        settings, created = Settings.objects.get_or_create(user=user)
        settings.email_notifications = (not settings.email_notifications)
        settings.save()

    return HttpResponse(json.dumps(response), content_type='application/json')
