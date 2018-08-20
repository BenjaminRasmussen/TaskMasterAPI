from django.contrib import admin
from .models import TaskList, UserListRelation, Task, TaskComment, \
    TaskListComment, Notification
# Register your models here.


@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = TaskList.list_display
    fields = TaskList.list_display


@admin.register(UserListRelation)
class UserRelationAdmin(admin.ModelAdmin):
    list_display = UserListRelation.list_display
    fields = UserListRelation.fields


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = Task.list_display
    fields = Task.fields


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = TaskComment.list_display
    fields = TaskComment.fields


@admin.register(TaskListComment)
class TaskListCommentAdmin(admin.ModelAdmin):
    list_display = TaskListComment.list_display
    fields = TaskListComment.fields


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = Notification.list_display
    fields = Notification.fields

