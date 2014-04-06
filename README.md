django-talk
===========

A simple, smooth private messaging app for Django.

Features:
- A functional layout similar to a major social site's messages page
- Lightly styled so you can apply your own
- Allows Markdown when posting
- Middleware using cache to see conversation partners' online status
- E-mail notifications when conversation partners are away
- AJAX updates when posting messages and polling for new ones, among other things

Usage
-----

### Installation

    pip install git+git://github.com/tangram/django-talk#egg=talk

Requirements should be automatically installed.

### Setup

Add the app and dependencies to your `INSTALLED_APPS`:

    INSTALLED_APPS = (
        ...
        'talk',
        'autocomplete_light',
    )

Add the middleware to your `MIDDLEWARE_CLASSES`:

    MIDDLEWARE_CLASSES = (
        ...
        'talk.middleware.UserLastseenMiddleware',
    )

Include `talk.urls` in your urlconf, e.g.:

    urlpatterns = patterns('',
        ...
        url(r'^talk/', include('talk.urls')),
        ...
    )

Optional settings to control in chat/idle/away indicators (in seconds):

    USER_IN_CHAT_TIMEOUT = 20
    USER_ONLINE_TIMEOUT = 300

Notes
-----

This app uses very primitive AJAX polling every 10 seconds to check for new messages. This is far from optimal and does not scale well. Proper long polling and websocket functionality will be added by v1.0.
