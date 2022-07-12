import imp
from django.contrib import admin
from django.urls import path
from django.urls import include, re_path
from app import urls, views as cviews
from general import apiviews as gapiviews
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()
routers.register('users',gapiviews.UserList,basename= "users")
routers.register('users/paginate',gapiviews.UserListPaginated,basename= "users_paginated")

urlpatterns = [
    path('user/create', gapiviews.UserView.as_view(),name='user'),
    path('user/', gapiviews.UserView.as_view(),name='user_update'),
    path("login/", gapiviews.LoginView.as_view(), name="login"),
    path("token/auth/", gapiviews.tokenAuth.as_view(), name="token-auth"),
    # path("packages/", gapiviews.Packages.as_view(), name="packages"),
    path("user/helps/", gapiviews.AddHelp.as_view(), name="add_help"),
    # path("signup/create_profile/", gapiviews.CreateProfile.as_view(), name="create_profile"),
    path("user/profile/", gapiviews.ProfileView.as_view(), name="profile"),
    path("user/picture/", gapiviews.PictureView.as_view(), name="picture"),
    path("user/like-unlike/", gapiviews.LikeUnlikeMango.as_view(), name="like_unlike"),
    path("user/swipe/", gapiviews.SwipeView.as_view(), name="swipe"),
    path("user/chats/", gapiviews.ChatView.as_view(), name="chats"),
    path("user/replies/", gapiviews.ReplyView.as_view(), name="replies"),
    path("user/swipe/filter", gapiviews.FilterSwipe.as_view(), name="filter_swipe"),
    path("user/security/", gapiviews.SecurityView.as_view(), name="security"),
    path("user/security/two-factor/enable", gapiviews.UserTwoFactorEnableView.as_view(), name="enable_two_factor"),
    path("user/security/two-factor/disable", gapiviews.UserTwoFactorDisableView().as_view(), name="disable_two_factor"),
    path("user/verify-phone/", gapiviews.VerifyPhone.as_view(), name="verify_phone"),
    path("user/change-password/request", gapiviews.RequestChangePasswordView.as_view(), name="request_change_password"),

]

urlpatterns+= routers.urls