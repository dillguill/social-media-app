from django.contrib.auth.models import User
from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest

from feed.models import Post
from followers.models import Follower

from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from .forms import UserUpdateForm, PasswordUpdateForm

class ProfileDetailView(DetailView):
    http_method_names = ["get", "post"]
    template_name = "profiles/detail.html"
    model = User
    context_object_name = "user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user = self.get_object()
        context = super().get_context_data(**kwargs)
        context['total_posts'] = Post.objects.filter(author=user).count()
        context['total_followers'] = Follower.objects.filter(following=user).count()
        if self.request.user.is_authenticated:
            context['you_follow'] = Follower.objects.filter(following=user, followed_by=self.request.user).exists()
        context['user_update_form'] = UserUpdateForm(instance=user)
        context['password_update_form'] = PasswordUpdateForm()
        return context

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        if 'update_user' in request.POST:
            user_update_form = UserUpdateForm(request.POST, instance=user)
            if user_update_form.is_valid():
                user_update_form.save()
                return redirect('profiles:detail', username=user.username)
        elif 'update_password' in request.POST:
            password_update_form = PasswordUpdateForm(request.POST)
            if password_update_form.is_valid():
                if user.check_password(password_update_form.cleaned_data['old_password']):
                    user.set_password(password_update_form.cleaned_data['new_password'])
                    user.save()
                    update_session_auth_hash(request, user)
                    return redirect('profiles:detail', username=user.username)
                else:
                    password_update_form.add_error('old_password', 'Old password is incorrect')
        context = self.get_context_data()
        context['user_update_form'] = user_update_form
        context['password_update_form'] = password_update_form
        return self.render_to_response(context)


class FollowView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        data = request.POST.dict()

        if "action" not in data or "username" not in data:
            return HttpResponseBadRequest("Missing data")

        try:
            other_user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            return HttpResponseBadRequest("Missing user")

        if data['action'] == "follow":
            # Follow
            follower, created = Follower.objects.get_or_create(
                followed_by=request.user,
                following=other_user
            )
        else:
            # Unfollow
            try:
                follower = Follower.objects.get(
                    followed_by=request.user,
                    following=other_user,
                )
            except Follower.DoesNotExist:
                follower = None

            if follower:
                follower.delete()

        return JsonResponse({
            'success': True,
            'wording': "Unfollow" if data['action'] == "follow" else "Follow"
        })
