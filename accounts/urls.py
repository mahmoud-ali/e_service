from django.urls import path,re_path

from allauth.account.views import LoginView as AllauthLoginView, LogoutView as AllauthLogoutView, PasswordSetView as AllauthPasswordSetView,PasswordChangeView as AllauthPasswordChangeView, PasswordResetView as AllauthPasswordResetView,ConfirmEmailView as AllauthConfirmEmailView

import allauth.account.views as allauth_view

urlpatterns = [
    path('login/', AllauthLoginView.as_view(), name='account_login'),
    path('logout/', AllauthLogoutView.as_view(), name='account_logout'),    
    path('password/set/', AllauthPasswordSetView.as_view(), name='account_set_password'),
    path('password/change/', AllauthPasswordChangeView.as_view(), name='account_change_password'),
    path('password/reset/', AllauthPasswordResetView.as_view(), name='account_reset_password'),
    
    # for password reset from allauth source code, but not exists in docs
    path(
        "password/reset/done/",
        allauth_view.password_reset_done,
        name="account_reset_password_done",
    ),
    re_path(
        r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        allauth_view.password_reset_from_key,
        name="account_reset_password_from_key",
    ),
    path(
        "password/reset/key/done/",
        allauth_view.password_reset_from_key_done,
        name="account_reset_password_from_key_done",
    ),
    
    #shadow sign up. if not exists error show up
    path('logout/', AllauthLogoutView.as_view(), name='account_signup'),    

]