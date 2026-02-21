from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect

from apps.blog.models import BlogPost

from .forms import CommentForm
from .models import Comment

_staff = lambda u: u.is_staff  # noqa: E731


@login_required
def create_comment_view(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status=BlogPost.Status.PUBLISHED)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post   = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment submitted for review.")
    return redirect(post.get_absolute_url())


@login_required
@user_passes_test(_staff)
def approve_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.is_approved = True
    comment.save(update_fields=["is_approved"])
    messages.success(request, "Comment approved.")
    return redirect(comment.post.get_absolute_url())


@login_required
@user_passes_test(_staff)
def delete_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_url = comment.post.get_absolute_url()
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted.")
        next_url = request.POST.get("next", post_url)
        return redirect(next_url)
    return redirect(post_url)
