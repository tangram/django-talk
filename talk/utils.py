from __future__ import unicode_literals
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def get_page(request, queryset, per_page=15, page_name='threads_page'):
    paginator = Paginator(queryset, per_page)

    page = request.GET.get(page_name)

    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
        page = 1
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    adjacent = 2
    start_page = max(int(page) - adjacent, 1)
    if start_page <= 3:
        start_page = 1

    end_page = int(page) + adjacent + 1
    if end_page >= paginator.num_pages - 1:
        end_page = paginator.num_pages + 1

    results.paginator.start_page = start_page
    results.paginator.end_page = end_page

    page_numbers = [n for n in range(start_page, end_page) if n > 0 and n <= paginator.num_pages]

    results.paginator.page_numbers = page_numbers

    results.paginator.show_first = 1 not in page_numbers
    results.paginator.show_last = paginator.num_pages not in page_numbers

    if request.GET.get(page_name):
        request.GET = request.GET.copy()
        del request.GET[page_name]

    if len(request.GET) > 0:
        results.query = '?' + request.GET.urlencode() + '&' + page_name + '='
    else:
        results.query = '?' + page_name + '='

    return results
