
from django.urls import path
from django.contrib.auth.views import LoginView
from .views import register_view


class RememberMeLoginView(LoginView):

    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.POST.get("remember_me"):
            # Keep the user logged in for 14 days
            self.request.session.set_expiry(60 * 60 * 24 * 14)
        else:
            # Session expires when the browser closes
            self.request.session.set_expiry(0)

        return response


app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        RememberMeLoginView.as_view(),
        name="login"
    ),

    path(
        "register/",
        register_view,
        name="register"
    ),
]
