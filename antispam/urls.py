from django.urls import path

from antispam import views

urlpatterns = [
    # /signup
    path('my/signup/', views.signup, name='pre-signup'),
    path('signup/', views.signup, name='pre-signup'),

    path('confirm/<uid>', views.confirm, name='confirm-email'),

    path('member/create/<uid>/<token>', views.ProtectedMemberSignupView.as_view(), name='signup'),
    path('member/create/<uid>/<token>', views.ProtectedMemberSignupView.as_view(), name='member-create'),
]
