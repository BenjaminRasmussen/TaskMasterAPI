"""This is the django URL's file. Its pretty selfexplanitory and its
responsible for linking all the endpoints and their REGEX up to all the views
in their given files. Its effectively boilerplate and rarely does it devaite
from the cookie cutter formal as seen below."""
# What is a * import?
from django.conf.urls import url
from .views import TaskListAPIView, TaskListRudView, TaskAPIView, TaskRudView,\
    UserListRelationAPIView, UserListRelationRudView, TaskCommentAPIView, \
    TaskCommentRudView, TaskListCommentAPIView, TaskListCommentRudView, \
    SearchAPI, NotificationListAPIView, UserCreateAPI, NotificationRUDView
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

urlpatterns = [
    # TaskList CRUD
    url(r'^TaskList/$', TaskListAPIView.as_view(), name='taskList-listcreate'),
    url(r'^TaskList/(?P<pk>\d+)/$', TaskListRudView.as_view(),
        name='taskList-rud'),

    # Task CRUD
    url(r'^Task/$', TaskAPIView.as_view(), name='task-listcreate'),
    url(r'^Task/(?P<pk>\d+)/$', TaskRudView.as_view(), name='task-rud'),

    # UserListRelation Create and listview
    url(r'^UserListRelation/$', UserListRelationAPIView.as_view(),
        name='userListRelation-listcreate'),
    # View single
    url(r'^UserListRelation/(?P<pk>\d+)/$',
        UserListRelationRudView.as_view(),
        name='userListRelation-rud'),

    # Comment CRUD
    url(r'^TaskComment/$', TaskCommentAPIView.as_view(),
        name='taskComment-listcreate'),
    url(r'^TaskComment/(?P<pk>\d+)/$', TaskCommentRudView.as_view(),
        name='taskComment-rud'),
    url(r'^TaskListComment/$', TaskListCommentAPIView.as_view(),
        name='taskListComment-listcreate'),
    url(r'^TaskListComment/(?P<pk>\d+)/$', TaskListCommentRudView.as_view(),
        name='taskListComment-rud'),

    # Notifications RUD
    url(r'^Notifications/$', NotificationListAPIView.as_view(),
        name="notifications-api"),
    url(r'^Notifications/(?P<pk>\d+)/$', NotificationRUDView.as_view(),
        name="notifications-rud"),

    # Search algorithm endpoint... duh.
    url(r'^Search/', SearchAPI.as_view(), name="search-api"),

    # User accounts system
    url(r'^Auth/login/$', obtain_jwt_token, name='api-login'),
    url(r'^Auth/Accounts/$', UserCreateAPI.as_view(),
        name="api-accounts")
]
