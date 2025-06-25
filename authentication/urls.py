from django.urls import path
from .views import (
    SignupAPIView, LoginAPIView, LogoutAPIView,
    OrganizationCreateAPIView, OrganizationListAPIView, OrganizationUpdateAPIView, OrganizationDeleteAPIView,
    MemberCreateAPIView, MemberListAPIView, MemberUpdateAPIView, MemberDeleteAPIView
)

urlpatterns = [
    # Auth
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),

    # Organization
    path('organizations/create', OrganizationCreateAPIView.as_view(), name='organization-create'),
    path('organizations/get', OrganizationListAPIView.as_view(), name='organization-get'),
    path('organizations/update/<int:org_id>', OrganizationUpdateAPIView.as_view(), name='organization-update'),
    path('organizations/delete/<int:org_id>', OrganizationDeleteAPIView.as_view(), name='organization-delete'),

    # Member
    path('members/create', MemberCreateAPIView.as_view(), name='member-create'),
    path('members/get', MemberListAPIView.as_view(), name='member-get'),
    path('members/update/<int:member_id>', MemberUpdateAPIView.as_view(), name='member-update'),
    path('members/delete/<int:member_id>', MemberDeleteAPIView.as_view(), name='member-delete'),
]
