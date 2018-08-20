""" These are the serializers. They're responsible for validating model data,
formatting model data and appending prevously impossible moddel data to the
model views, such as URL's. They also declare the relationship between the
data model and the view its assigned by controlling different fields and
declaring them read only or whatnot. They are all boilerplate copy paste
but you have to have them. The configuration varies little but i have
explained the UserSerializer futher below as its the only one that actually
deviates. """
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from taskMaster.models import TaskList, Task, TaskListComment, TaskComment, \
    UserListRelation, Notification


class TaskListSerializer(serializers.ModelSerializer):  # forms.ModelForm
    url = serializers.SerializerMethodField(read_only=True)
    tasks = serializers.SerializerMethodField(read_only=True)
    tasksUrl = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)
    commentsUrl = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskList
        fields = [
            'url',
            'tasks',
            'tasksUrl',
            'comments',
            'commentsUrl',
            'pk',
            'title',
            'description',
            'owner',
            'views',
            'date_created',
        ]
        read_only_fields = ['pk', 'date_created', 'owner', 'views']

    # converts to JSON
    # validations for data passed

    def get_url(self, obj):
        # request
        request = self.context.get("request")
        return obj.get_api_url(request=request)

    def get_tasks(self, obj):
        return obj.get_tasks()

    def get_tasksUrl(self, obj):
        request = self.context.get("request")
        return [i.get_api_url(request=request) for i in Task.objects.filter(
            LinkedTaskList=obj)]

    def get_commentsUrl(self, obj):
        request = self.context.get("request")
        return [i.get_api_url(request=request) for i in
                TaskListComment.objects.filter(LinkedTaskList=obj)]

    def get_comments(self, obj):
        return [i.pk for i in
                TaskListComment.objects.filter(LinkedTaskList=obj)]


class TaskSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)
    linkedUrl = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)
    commentsUrl = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'url',
            'pk',
            'comments',
            'commentsUrl',
            'title',
            'completed',
            'LinkedTaskList',
            'linkedUrl',
            'owner',
            'date_created',
            'views',
        ]
        read_only_fields = ['pk', 'date_created', 'owner', 'views']

    # converts to JSON
    # validations for data passed

    def get_url(self, obj):
        # request
        request = self.context.get("request")
        return obj.get_api_url(request=request)

    def get_linkedUrl(self, obj):
        request = self.context.get("request")
        return obj.LinkedTaskList.get_api_url(request=request)

    def get_commentsUrl(self, obj):
        request = self.context.get("request")
        return [i.get_api_url(request=request) for i in
                TaskComment.objects.filter(LinkedTask=obj)]

    def get_comments(self, obj):
        return [i.pk for i in TaskComment.objects.filter(LinkedTask=obj)]


class UserListRelationSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserListRelation
        fields = [
            'url',
            'pk',
            'role',
            'user',
            'owner',
            'LinkedTaskList',
            'date_created',
        ]
        read_only_fields = ['pk', 'owner', 'date_created']

    def get_url(self, obj):
        # request
        request = self.context.get("request")
        return obj.get_api_url(request=request)


class TaskCommentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskComment
        fields = [
            'url',
            "pk",
            "title",
            "description",
            "LinkedTask",
            "views",
            "owner",
            "date_created",
        ]
        read_only_fields = ['pk', 'owner', 'views', 'date_created']

    def get_url(self, obj):
        # request
        request = self.context.get("request")
        return obj.get_api_url(request=request)


class TaskListCommentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskListComment
        fields = [
            'url',
            "pk",
            "title",
            "description",
            "LinkedTaskList",
            "views",
            "owner",
            "date_created",
        ]
        read_only_fields = ['pk', 'owner', 'views', 'date_created']

    def get_url(self, obj):
        # request
        request = self.context.get("request")
        return obj.get_api_url(request=request)


class NotificationSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "url",
            "pk",
            "title",
            "seen",
            "seen_on",
            "receiver",
            "date_created",
            "deep_link_url"
        ]

    def get_url(self, obj):
        # request
        request = self.context.get("request")
        return obj.get_api_url(request=request)


class UserSerializer(serializers.ModelSerializer):
    """This is the user serializer and its responsible for validating the
    data given by the signup form view. Its the only Serializer that defines
    or overrides its own fields and then retroactively fits that data into
    a model. Usually its the other way around."""

    # Validates the email data given by the user
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])

    # Validates the username data given by the user
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])

    # Validates the password data given by the user
    password = serializers.CharField(min_length=8)

    # Creates and returns the user model to the view.
    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        validated_data['email'],
                                        validated_data['password'])
        return user

    # model is the django.contrib.auth user model.
    class Meta:
        model = User
        fields = [
            'pk',
            'username',
            'email',
            'password',
        ]
