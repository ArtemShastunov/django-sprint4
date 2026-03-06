from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from .constants import POSTS_ON_MAIN_PAGE


def get_posts_queryset(
    queryset=None,
    filter_public=True,
    annotate_comments=False,
    author=None,
    paginate=True,
    request=None
):
    """Возвращает отфильтрованный и аннотированный queryset постов."""
    from .models import Post

    if queryset is None:
        queryset = Post.objects.select_related(
            'author', 'location', 'category'
        )

    if author is not None:
        queryset = queryset.filter(author=author)
    elif filter_public:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    if annotate_comments:
        queryset = queryset.annotate(comment_count=Count('comments'))

    if paginate and request is not None:
        paginator = Paginator(queryset, POSTS_ON_MAIN_PAGE)
        page_number = request.GET.get('page')
        return paginator.get_page(page_number)

    return queryset
