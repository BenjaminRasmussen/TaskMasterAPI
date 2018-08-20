from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.dispatch import receiver
from rest_framework import status
from rest_framework.reverse import reverse as api_reverse
from django.core import signals
from rest_framework.response import Response


class TaskList(models.Model):
    title = models.CharField(help_text="Task name", max_length=55)
    description = models.TextField(help_text="Description")
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name="TaskList_owner")
    date_created = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)

    list_display = ["pk", "title", "description", "owner", "views",
                    "date_created"]
    fields = ["title", "description"]

    def get_api_url(self, request=None):
        return api_reverse("taskMaster-api:taskList-rud",
                           kwargs={'pk': self.pk}, request=request)

    def get_tasks(self):
        return ', '.join([str(Task.pk) for Task in
                          Task.objects.filter(LinkedTaskList=self.pk)])

    def increment(self):
        self.views += 1
        self.save()

    @staticmethod
    def has_user_relation(obj, user):
        try:  # Keep calm and ignore best practices
            if obj.owner == user:
                return True
            if UserListRelation.objects.get(user=user, LinkedTaskList=obj):
                return True
            else:
                return False
        except:  # You cant throw exception on the permission level, dont try.
            return False

    @staticmethod
    def user_is_admin(obj, user):
        try:  # Keep calm and ignore best practices
            if obj.owner == user:
                return True
            temp = UserListRelation.objects.get(LinkedTaskList=obj, user=user)
            if temp.role.lower() == "admin" or temp.owner == user:
                return True
            else:
                return False
        except:
            return False  # You cant raise excetions on the permission level.


class Task(models.Model):
    title = models.CharField(help_text="name", max_length=55)
    completed = models.BooleanField(default=False)
    LinkedTaskList = models.ForeignKey(TaskList, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name="Task_owner")
    date_created = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)

    list_display = ["pk", "title", "completed", "LinkedTaskList", "owner",
                    "views", "date_created"]
    fields = ["title", "LinkedTaskList", "completed"]

    def get_api_url(self, request=None):
        return api_reverse("taskMaster-api:task-rud",
                           kwargs={'pk': self.pk}, request=request)

    def increment(self):
        self.views += 1
        self.save()


class UserListRelation(models.Model):
    LinkedTaskList = models.ForeignKey(TaskList, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name="UserRelation_owner")
    date_created = models.DateTimeField(auto_now=True)
    role = models.CharField(help_text="case insensitive. Type admin to give "
                                      "special rights!",
                            max_length=55, default="guest")

    list_display = ["pk", "LinkedTaskList", "user", "date_created", "role",
                    "owner"]
    fields = ["LinkedTaskList", "user", "role"]

    def get_api_url(self, request=None):
        return api_reverse("taskMaster-api:userListRelation-rud",
                           kwargs={'pk': self.pk}, request=request)


class TaskComment(models.Model):
    title = models.CharField(help_text="name", max_length=55)
    description = models.TextField(help_text="Description")
    LinkedTask = models.ForeignKey(Task, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name="TaskComment_owner")
    date_created = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)

    list_display = ["pk", "title", "description", "LinkedTask", "owner",
                    "date_created"]
    fields = ["title", "description", "LinkedTask"]

    def get_api_url(self, request=None):
        return api_reverse("taskMaster-api:taskComment-rud",
                           kwargs={'pk': self.pk}, request=request)

    def increment(self):
        self.views += 1
        self.save()


class TaskListComment(models.Model):
    title = models.CharField(help_text="name", max_length=55)
    description = models.TextField(help_text="Description")
    LinkedTaskList = models.ForeignKey(TaskList, on_delete=models.CASCADE, )
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name="TaskListComment_owner")
    date_created = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)

    list_display = ["pk", "title", "description", "LinkedTaskList", "owner",
                    "date_created"]
    fields = ["title", "description", "LinkedTaskList"]

    def get_api_url(self, request=None):
        return api_reverse("taskMaster-api:taskListComment-rud",
                           kwargs={'pk': self.pk}, request=request)

    def increment(self):
        self.views += 1
        self.save()


class Notification(models.Model):
    title = models.CharField(help_text="name", max_length=55)
    changes = models.CharField(help_text="Plaintext list of changes",
                               max_length=250,
                               default="")
    # seen is flipped when its FIRST GET request is sent.
    seen = models.BooleanField(default=False,
                               help_text="Has this notification been seen?")
    # seen on is handled by signals and wont be an endpoint. :)
    seen_on = models.DateTimeField(null=True)
    # Used as a dynamic reverse-api-url field for whatever model uses this.
    deep_link_url = models.CharField(help_text="name", max_length=250,
                                     default="")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name="Notification_receiver")
    date_created = models.DateTimeField(auto_now=True)

    list_display = ["pk", "title", "seen", "seen_on", "receiver",
                    "date_created", "deep_link_url"]
    fields = ["title", "seen", "seen_on", "receiver", "deep_link_url"]

    def get_api_url(self, request=None):
        return api_reverse("taskMaster-api:notifications-rud",
                           kwargs={'pk': self.pk}, request=request)


@receiver(models.signals.post_save, sender=TaskList, weak=False)
def execute_after_save(sender, instance, created, *args, **kwargs):
    receivers = UserListRelation.objects.filter(LinkedTaskList=instance)
    for i in receivers:
        notification, created = Notification.objects.get_or_create(
            title=f"A change has been made to the {type(instance)}, "
                  f"called {instance.title}",
            seen=False,
            deep_link_url=i.get_api_url(),
            receiver=i.user,
        )


@receiver(models.signals.post_save, sender=Task, weak=False)
def execute_after_save(sender, instance, created, *args, **kwargs):
    receivers = UserListRelation.objects.filter(LinkedTaskList=
                                                instance.LinkedTaskList)
    for i in receivers:
        notification, created = Notification.objects.get_or_create(
            title=f"A change has been made to the {type(instance)}, "
                  f"called {instance.title}",
            seen=False,
            deep_link_url=i.get_api_url(),
            receiver=i.user,
        )


@receiver(models.signals.post_save, sender=TaskListComment, weak=False)
def execute_after_save(sender, instance, created, *args, **kwargs):
    receivers = UserListRelation.objects.filter(LinkedTaskList=
                                                instance.LinkedTaskList)
    for i in receivers:
        notification, created = Notification.objects.get_or_create(
            title=f"A change has been made to the {type(instance)}, "
                  f"called {instance.title}",
            seen=False,
            deep_link_url=i.get_api_url(),
            receiver=i.user,
        )


@receiver(models.signals.post_save, sender=TaskComment, weak=False)
def execute_after_save(sender, instance, created, *args, **kwargs):
    receivers = UserListRelation.objects. \
        filter(LinkedTaskList=instance.LinkedTask.LinkedTaskList)
    for i in receivers:
        notification, created = Notification.objects.get_or_create(
            title=f"A change has been made to the {type(instance)}, "
                  f"called {instance.title}",
            seen=False,
            deep_link_url=i.get_api_url(),
            receiver=i.user,
        )


@receiver(models.signals.post_save, sender=UserListRelation, weak=False)
def execute_after_save(sender, instance, created, *args, **kwargs):
    notification, created = Notification.objects.get_or_create(
        title=f"A change has been made to the {type(instance)}, "
              f"with the list called {instance.LinkedTaskList.title}",
        seen=False,
        receiver=instance.user,
        deep_link_url=instance.get_api_url(),
    )
