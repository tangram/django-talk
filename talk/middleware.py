from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

class UserLastseenMiddleware:
    def process_request(self, request):
        if request.user.is_authenticated():
            now = timezone.now()
            cache.set(
                'lastseen_%i' % request.user.id,
                now,
                getattr(settings, 'USER_ONLINE_TIMEOUT', 300)
            )
