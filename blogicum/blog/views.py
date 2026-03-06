from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post, User
from .services import get_posts_queryset


def index(request):
    """Главная страница с пагинацией постов."""
    page_obj = get_posts_queryset(
        filter_public=True,
        annotate_comments=True,
        paginate=True,
        request=request
    )
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """Страница отдельного поста."""
    if request.user.is_authenticated:
        post = get_object_or_404(
            Post.objects.select_related('author', 'location', 'category'),
            pk=post_id,
        )
        is_visible = (
            post.is_published
            and post.category.is_published
            and post.pub_date <= timezone.now()
        )
        if not is_visible and post.author != request.user:
            raise Http404('Пост не найден')
    else:
        post = get_object_or_404(
            get_posts_queryset(filter_public=True), pk=post_id
        )

    comments = post.comments.select_related('author')
    form = CommentForm()
    context = {'post': post, 'form': form, 'comments': comments}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Страница категории с пагинацией постов."""
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    page_obj = get_posts_queryset(
        queryset=Post.objects.filter(category=category),
        filter_public=True,
        annotate_comments=True,
        paginate=True,
        request=request
    )
    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


def profile(request, username):
    """Страница профиля пользователя."""
    user = get_object_or_404(User, username=username)
    filter_public = request.user != user

    page_obj = get_posts_queryset(
        queryset=user.posts.select_related('author', 'location', 'category'),
        filter_public=filter_public,
        annotate_comments=True,
        paginate=True,
        request=request
    )
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


def signup(request):
    """Регистрация нового пользователя."""
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('blog:profile', username=user.username)
    return render(
        request,
        'registration/registration_form.html',
        {'form': form}
    )


@login_required
def create_post(request):
    """Создание нового поста."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    """Редактирование поста."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    """Удаление поста."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    form = PostForm(instance=post)
    return render(
        request,
        'blog/create.html',
        {'form': form, 'post': post}
    )


@login_required
def add_comment(request, post_id):
    """Добавление комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request,
        'blog/comment.html',
        {'form': form, 'comment': comment}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request,
        'blog/comment.html',
        {'comment': comment}
    )


@login_required
def edit_profile(request):
    """Редактирование профиля пользователя."""
    form = ProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(
        request,
        'blog/user.html',
        {'form': form}
    )


@login_required
def change_password(request):
    """Изменение пароля пользователя."""
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect('blog:profile', username=request.user.username)
    return render(
        request,
        'registration/password_change_form.html',
        {'form': form}
    )
