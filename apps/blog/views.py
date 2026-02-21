from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from apps.comments.forms import CommentForm
from apps.comments.models import Comment

from .forms import BlogPostForm
from .models import BlogPost, Category

_staff = lambda u: u.is_staff  # noqa: E731


def blog_list_view(request):
    posts      = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).select_related("category")
    categories = Category.objects.all()
    return render(request, "blog/list.html", {"posts": posts, "categories": categories})


def blog_detail_view(request, slug):
    # Staff can preview drafts
    qs = BlogPost.objects.all() if (request.user.is_authenticated and request.user.is_staff) \
         else BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)
    post = get_object_or_404(qs, slug=slug)
    comments = Comment.objects.filter(post=post, is_approved=True).select_related("author")
    pending  = Comment.objects.filter(post=post, is_approved=False).select_related("author") \
               if (request.user.is_authenticated and request.user.is_staff) else []
    form = CommentForm() if request.user.is_authenticated else None
    return render(request, "blog/detail.html", {
        "post": post,
        "comments": comments,
        "pending_comments": pending,
        "comment_form": form,
    })


@login_required
@user_passes_test(_staff)
def blog_create_view(request):
    form = BlogPostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, f'Post "{post.title}" created.')
        return redirect(post.get_absolute_url())
    return render(request, "blog/editor.html", {"form": form, "is_create": True})


@login_required
@user_passes_test(_staff)
def blog_edit_view(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    form = BlogPostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Post updated.")
        return redirect(post.get_absolute_url())
    return render(request, "blog/editor.html", {"form": form, "post": post})


@login_required
@user_passes_test(_staff)
def blog_delete_view(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if request.method == "POST":
        title = post.title
        post.delete()
        messages.success(request, f'Post "{title}" deleted.')
        return redirect("blog_list")
    return render(request, "dashboard/confirm_delete.html", {"object": post, "type": "Blog Post"})
