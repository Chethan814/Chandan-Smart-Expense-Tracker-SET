from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy
from django.views.generic import CreateView


class StyledLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("login")


from accounts import views

urlpatterns = [
    path("login/", StyledLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/update/", views.update_profile, name="update_profile"),
    path("profile/delete/", views.delete_account, name="delete_account"),
]
