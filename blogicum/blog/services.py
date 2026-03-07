from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from .constants import POSTS_ON_MAIN_PAGE
from .models import Post


def get_pagination_page(queryset, request, per_page=POSTS_ON_MAIN_PAGE):
    """Возвращает страницу пагинатора."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def get_posts_queryset(
    queryset=None,
    filter_public=True,
    annotate_comments=False,
    paginate=False,
    request=None
):
    """Возвращает отфильтрованный и аннотированный queryset постов."""
    if queryset is None:
        queryset = Post.objects.all()

    queryset = queryset.select_related('author', 'location', 'category')

    if filter_public:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    if annotate_comments:
        queryset = queryset.annotate(comment_count=Count('comments'))

    queryset = queryset.order_by('-pub_date')

    if paginate and request is not None:
        return get_pagination_page(queryset, request)

    return queryset
