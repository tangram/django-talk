from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import get_current_site
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
import autocomplete_light


class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['username']
    choices = get_user_model().objects.all()
    model = get_user_model()

autocomplete_light.register(UserAutocomplete)


class Message(models.Model):
    author = models.ForeignKey(get_user_model(), editable=False, related_name='talk_message')
    body = models.TextField()
    created_at = models.DateTimeField(default=lambda:timezone.localtime(timezone.now()), editable=False)

    class Meta:
        ordering = ['created_at']
        verbose_name = _('message')
        verbose_name_plural = _('messages')

    def __unicode__(self):
        return '%s...' % self.body[:25]


class Thread(models.Model):
    users = models.ManyToManyField(get_user_model(), through='MessageIndex', related_name='talk_thread')
    messages = models.ManyToManyField(Message, through='MessageIndex')
    updated_at = models.DateTimeField(default=lambda:timezone.localtime(timezone.now()), editable=False)

    class Meta:
        ordering = ['updated_at']
        verbose_name = _('conversation')
        verbose_name_plural = _('conversations')

    def __unicode__(self):
        return '%s' % self.user_list

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('view_thread', kwargs={'thread_id': self.id})

    @property
    def last_message_excerpt(self):
        try:
            ex = self.messages.latest('created_at').body[:25]
            return '%s...' % ex if len(ex) >= 25 else ex
        except:
            return ''

    @property
    def last_message_author(self):
        try:
            return self.messages.latest('created_at').author
        except:
            return None

    @property
    def user_list(self):
        return ', '.join([user.__unicode__() for user in self.users.distinct()])

    def other_users(self, user):
        return self.users.exclude(id=user.id).distinct()

    def count_unread(self, user):
        return self.messageindex_set.filter(user=user).filter(new=True).count()


class MessageIndexManager(models.Manager):
    def new(self, user):
        return self.filter(user=user).filter(new=True)

    def count_unread(self, user):
        return self.new(user).count()


class MessageIndex(models.Model):
    message = models.ForeignKey(Message)
    thread = models.ForeignKey(Thread)
    user = models.ForeignKey(get_user_model(), related_name='talk_messageindex')
    new = models.BooleanField(default=True)
    next_day = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=lambda:timezone.localtime(timezone.now()), editable=False)

    objects = MessageIndexManager()

    class Meta:
        ordering = ['created_at']
        verbose_name = _('message index')
        verbose_name_plural = _('message indices')

    def save(self, *args, **kwargs):
        try:
            message = self.thread.messages.latest('created_at')
            if message:
                self.next_day = (self.created_at.date() != message.created_at.date())
        except:
            pass

        request = kwargs.pop('request')
        super(MessageIndex, self).save(*args, **kwargs)
        Thread.objects.filter(id=self.thread.id).update(updated_at=self.created_at)

        if (self.user != self.message.author and not
            self.user_in_chat() and not
            self.user_online()):
            try:
                notify_user = self.user.talk_settings.email_notifications
            except:
                notify_user = False

            if notify_user:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain

                context = {
                    'author': self.message.author,
                    'subject': self.user,
                    'message_url': 'http://%s%s#%s' % (
                        domain,
                        self.thread.get_absolute_url(),
                        self.message.id
                    ),
                    'site_name': site_name,
                }
                message = render_to_string('talk/email_notification.txt', context)
                send_mail(
                    subject=_('%(prefix)s New message notification' % {
                        'prefix': settings.EMAIL_SUBJECT_PREFIX
                    }),
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.user.email],
                )

    def user_online(self):
        return cache.get('lastseen_%i' % self.user.id, None)

    def user_in_chat(self):
        return cache.get('in_chat_%i' % self.user.id, None)


class Settings(models.Model):
    user = models.OneToOneField(get_user_model(), related_name='talk_settings')
    email_notifications = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('user settings')
        verbose_name_plural = _('user settings')
