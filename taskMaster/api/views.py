""" This is views.py and this is where most of the user facing data is
handed off from the database to the user. """
# Have you ever heard of this thing called boilerplate? Me neither.
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from datetime import datetime
from rest_framework import generics, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from taskMaster.models import (
    Task, TaskList, TaskComment, TaskListComment, Notification,
    UserListRelation)
from .serializers import TaskListSerializer, TaskSerializer, \
    UserListRelationSerializer, TaskCommentSerializer, \
    TaskListCommentSerializer, NotificationSerializer, UserSerializer
from rest_framework import status
from rest_framework.response import Response
from .permissions import CRUDOnlyRelatedTaskList, \
    CRUDTaskComments, CRUDTaskListComments, CRUDUserListRelation, \
    IsAdminOrUserRelatedReadOnlyOr401
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from TaskMasterAPI.settings import REST_FRAMEWORK
from .request_reponse_examples import search_reponse_exampe


class TaskListAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    """
    This is the list view of the task list model. It returns all the users
    task lists and allows him to create new ones.

    GET:
        Returns a list of all task list available to the requesting user. Dont
        confuse with the primary key filter on the next tab. This function
        doesnt take ANY parameters.

    POST:
        Fill in the required fields and create a new task list and assign user
        as the owner
    """

    lookup_field = 'pk'
    serializer_class = TaskListSerializer
    permission_classes = (IsAdminOrUserRelatedReadOnlyOr401,)
    pagination_class = PageNumberPagination

    # Queryset defines the search space availablee to the querying user.
    def get_queryset(self, *args, **kwargs):
        # Gets the QS of UserListRelations that the user has access to.
        relations = UserListRelation.objects.filter(
            Q(user=self.request.user) |
            Q(owner=self.request.user)).distinct()
        return [i.LinkedTaskList for i in relations]

    # Perform_create is called after post() and it works like django form
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # Post is the app level object creation function and takes the POST request
    # POST requires the fields given by its serializer. Declared above
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class TaskListRudView(generics.RetrieveUpdateDestroyAPIView):
    """ This is the RUD view of TaskList and it takes a Primary_Key to enter
    this layer of the API. It is responsible for updating or deleting as well
    as viewing the model at the object level.
    GET:
        only accessed through passing a pk value through the slug field.
        returns the object with the matching pk value granted permission

    PUT, PATCH:
        Return the get data and modify it on the server side by sending back
         some manipulated data through a PUT or a PATCH request. If you have
         permission to the object this view will update the database model.

    DELETE:
        only works if you fill out the slug field and have object permission.

    """

    lookup_field = 'pk'  # slug, id # url(r'?P<pk>\d+')
    serializer_class = TaskListSerializer
    permission_classes = (IsAdminOrUserRelatedReadOnlyOr401,)

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}

    def get_queryset(self):
        obj = TaskList.objects.filter(pk=self.kwargs.get("pk"))
        return obj

    # Object level permission is handled manually in this class
    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


class TaskAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    """
    This is the generic list view of the task model. It returns all the users
    tasks (IF THEY ARE THE OWNER) and allows him to create new ones. If you
    want to access tasks otherwise, send an empty search on that endpoint or
    directly through task lists.

    GET:
        Returns a list of all tasks available to the requesting user. Dont
        confuse with the primary key filter on the next tab. This function
        doesnt take ANY parameters.

    POST:
        Fill in the required fields and create a new task list and assign user
        as the owner
    """

    lookup_field = 'pk'
    serializer_class = TaskSerializer
    permission_classes = (CRUDOnlyRelatedTaskList,)
    pagination_class = PageNumberPagination

    # Find user auth on this layer.
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        # Fix after implementing UserLIstRelation
        temp = Task.objects.filter(owner=self.request.user)
        return temp

    def post(self, request, *args, **kwargs):
        temp = TaskList.objects.get(pk=self.request.data.get("LinkedTaskList"))
        try:
            UserListRelation.objects.get(
                user=self.request.data.get("user"),
                LinkedTaskList=temp)
            return Response({"User-List-Relation conflict": "Duplicate found"},
                            status=status.HTTP_409_CONFLICT)
        except ObjectDoesNotExist:
            if temp.user_is_admin(temp, self.request.user) is True:
                return self.create(request, *args, **kwargs)
            else:
                return Response({"User is not authorized to make this request":
                                     str(self.request.user)},
                                status=status.HTTP_401_UNAUTHORIZED)

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class TaskRudView(generics.RetrieveUpdateDestroyAPIView):
    """
    This is the RUD view of Task. It takes a Primary_Key to enter
    this layer of the API. It is responsible for updating or deleting as well
    as viewing the model at the object level.
    GET:
        only accessed through passing a pk value through the slug field.
        returns the object with the matching pk value granted permission

    PUT, PATCH:
        Return the get data and modify it on the server side by sending back
         some manipulated data through a PUT or a PATCH request. If you have
         permission to the object this view will update the database model.

    DELETE:
        only works if you fill out the slug field and have object permission.
        Which at this level is already done once at this point.
    """

    lookup_field = 'pk'  # slug, id # url(r'?P<pk>\d+')
    serializer_class = TaskSerializer
    permission_classes = (CRUDOnlyRelatedTaskList,)

    def get_queryset(self):
        # Fix after implementing UserLIstRelation
        temp = Task.objects.filter(pk=self.kwargs['pk'])
        return temp

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class UserListRelationAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    """
    This is the generic list view of the UserListRelation model.
    It returns all the users relations if they are the owner or the user
    getting related by another user. And this list has a deeplink attached
    so you don't have to fill out the slugfields yourself.

    GET:
        Returns a list of all ULR's available to the requesting user. Dont
        confuse with the primary key filter on the next tab. This function
        doesnt take ANY parameters.

    POST:
        Fill in the required fields and create a new task list and assign user
        as the owner
        role:
            This field is pretty messy. Adding "Admin" or "admin" without the
            marks will let the model know that this user should be considered
            on par with the model owner in the future dealings with the task
            list. Its not required to fill out this field, i usually put guest
            there.
    """

    lookup_field = 'pk'
    serializer_class = UserListRelationSerializer
    permission_classes = (CRUDUserListRelation,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return UserListRelation.objects.filter(Q(owner=self.request.user) |
                                               Q(user=self.request.user))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        temp = TaskList.objects.get(pk=self.request.data.get("LinkedTaskList"))
        try:
            UserListRelation.objects.get(
                user=self.request.data.get("user"),
                LinkedTaskList=temp)
            return Response({"User-List-Relation conflict": "Duplicate found"},
                            status=status.HTTP_409_CONFLICT)
        except ObjectDoesNotExist:
            if temp.user_is_admin(temp, self.request.user) is True:
                return self.create(request, *args, **kwargs)
            else:
                return Response({"User is not authorized to make this request":
                                     str(self.request.user)},
                                status=status.HTTP_401_UNAUTHORIZED)

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class UserListRelationRudView(generics.RetrieveUpdateDestroyAPIView):
    """
    This is the RUD view of User-list-Relation. It takes a Primary_Key to enter
    this layer of the API. It is responsible for updating or deleting as well
    as viewing the model at the object level.
    GET:
        only accessed through passing a pk value through the slug field.
        returns the object with the matching pk value granted permission

    PUT, PATCH:
        Return the get data and modify it on the server side by sending back
        some manipulated data through a PUT or a PATCH request. If you have
        permission to the object this view will update the database model.

    DELETE:
        only works if you fill out the slug field and have object permission.
        Which at this level is already done once at this point.
    """

    lookup_field = 'pk'
    serializer_class = UserListRelationSerializer
    permission_classes = (CRUDUserListRelation,)

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}

    def get_queryset(self):
        obj = UserListRelation.objects.filter(pk=self.kwargs.get("pk"))
        return obj

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


class TaskCommentAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    """
    This is the generic list view of the Task-Comment model.
    It returns all the (task) comments where the user is  the owner.
    This list has a deeplink attached so you don't have to fill out the
    slugfields yourself.

    GET:
        Returns a list of all Comments available to the requesting user. Dont
        confuse with the primary key filter on the next tab. This function
        doesnt take ANY parameters.

    POST:
        Fill in the required fields and create a new task list and assign user
        as the owner
    """

    lookup_field = "pk"
    serializer_class = TaskCommentSerializer
    permission_classes = (CRUDTaskComments,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return TaskComment.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        task = Task.objects.get(pk=request.data.get("LinkedTask"))
        temp = task.LinkedTaskList
        try:
            UserListRelation.objects.get(
                user=self.request.data.get("user"),
                LinkedTaskList=temp)
            return Response({"User-List-Relation conflict": "Duplicate found"},
                            status=status.HTTP_409_CONFLICT)
        except ObjectDoesNotExist:
            if temp.user_is_admin(temp, self.request.user) is True:
                return self.create(request, *args, **kwargs)
            else:
                return Response({"User is not authorized to make this request":
                                     str(self.request.user)},
                                status=status.HTTP_401_UNAUTHORIZED)

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class TaskCommentRudView(generics.RetrieveUpdateDestroyAPIView):
    """
    This is the RUD view of Task Comment Model. It takes a Primary_Key to enter
    this layer of the API. It is responsible for updating or deleting as well
    as viewing the model at the object level.
    GET:
        only accessed through passing a pk value through the slug field.
        returns the object with the matching pk value granted permission

    PUT, PATCH:
        Return the get data and modify it on the server side by sending back
        some manipulated data through a PUT or a PATCH request. If you have
        permission to the object this view will update the database model.

    DELETE:
        only works if you fill out the slug field and have object permission.
        Which at this level is already done once at this point.
    """

    lookup_field = "pk"
    serializer_class = TaskCommentSerializer
    permission_classes = (CRUDTaskComments,)

    def get_queryset(self):
        obj = TaskComment.objects.filter(pk=self.kwargs["pk"])
        [i.increment() for i in obj]
        return obj

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


class TaskListCommentAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    """
    This is the generic list view of the Task-List-Comment model.
    It returns all the (task-list) comments where the user is the owner.
    This list has a deeplink attached so you don't have to fill out the
    slugfields yourself.

    GET:
        Returns a list of all Comments available to the requesting user. Dont
        confuse with the primary key filter on the next tab. This function
        doesnt take ANY parameters.

    POST:
        Fill in the required fields and create a new task list and assign user
        as the owner
    """

    lookup_field = "pk"
    serializer_class = TaskListCommentSerializer
    permission_classes = (CRUDTaskListComments,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return TaskListComment.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        temp = TaskList.objects.get(pk=self.request.data.get("LinkedTaskList"))
        try:
            UserListRelation.objects.get(
                user=self.request.data.get("user"),
                LinkedTaskList=temp)
            return Response({"User-List-Relation conflict": "Duplicate found"},
                            status=status.HTTP_409_CONFLICT)
        except ObjectDoesNotExist:
            if temp.user_is_admin(temp, self.request.user) is True:
                return self.create(request, *args, **kwargs)
            else:
                return Response({"User is not authorized to make this request":
                                     str(self.request.user)},
                                status=status.HTTP_401_UNAUTHORIZED)

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class TaskListCommentRudView(generics.RetrieveUpdateDestroyAPIView):
    """
    This is the RUD view of Task-List-Comment Model. It takes a Primary_Key to
    enter this layer of the API. It is responsible for updating or deleting as
     well as viewing the model at the object level.
    GET:
        only accessed through passing a pk value through the slug field.
        returns the object with the matching pk value granted permission

    PUT, PATCH:
        Return the get data and modify it on the server side by sending back
        some manipulated data through a PUT or a PATCH request. If you have
        permission to the object this view will update the database model.

    DELETE:
        only works if you fill out the slug field and have object permission.
        Which at this level is already done once at this point.
    """

    lookup_field = "pk"
    serializer_class = TaskListCommentSerializer
    permission_classes = (CRUDTaskListComments,)

    def get_queryset(self):
        temp = TaskListComment.objects.filter(pk=self.kwargs.get("pk"))
        [i.increment() for i in temp]
        return temp

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


class NotificationListAPIView(generics.ListAPIView):
    """
    This is the generic list view of the Notification model.
    It returns all the Notifications where the receiver is the user.
    This list has a deeplink, to the model that triggered the notification,
    attached so you don't have to fill out the slugfields yourself.

    GET:
        Returns a list of all Notifications available to the requesting user.
        Don't confuse with the primary key filter on the next tab. This
        function doesnt take ANY parameters.

    POST:
        POST is disabled here. The system creates notifications internally.
    """

    lookup_field = "pk"
    serializer_class = NotificationSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        temp = Notification.objects.filter(receiver=self.request.user)
        return temp.order_by("-date_created")

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        if not obj.seen:
            obj.seen_on = datetime.now()
            obj.seen = True
            obj.save()
        return obj


class NotificationRUDView(generics.RetrieveAPIView):
    """
    This is the Retreive view of the Notification Model. It takes a Primary
    Key to enter this layer of the API. It is responsible for updating and
    viewing the model at the object level.
    GET:
        only accessed through passing a pk value through the slug field.
        returns the object with the matching pk value granted permission.
        Once you access at this level through the slug fields on the list view
        you automatically mark this a seen and attach a seen_on field so
        you can come back and find out when you first saw this. That action
        then in turn allows the user to see more notifications concerning
        the model that triggered said notification.
    """

    lookup_field = "pk"
    serializer_class = NotificationSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        temp = Notification.objects.filter(receiver=self.request.user)
        return temp

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        if not obj.seen:
            obj.seen_on = datetime.now()
            obj.seen = True
            obj.save()
        return obj


class SearchAPI(mixins.ListModelMixin, APIView):
    """
    This is the multi-model 'global' search that queryes four different
    models and obeys both ordering and pagination given the option. Its the
    only low-level class i have implemented and given its size i think you can
    figure out why that is.
    get:
    This overrides the get function and allows us to customize the returned
    data that then gets responded to the user once he GET's this url.
    Lastly permissions arent included except for the is-logged-in one and that
    is because the user can only GET data based on that user's profile. So
    permissions are hard coded in this case.

    Request:
        /api/v1.0/TaskMaster/Search/&order=-views&page=1&q=test
    """
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,)
    pagination_class = PageNumberPagination
    extra_url_params = (('q',
                         'String',
                         'Simple filter, will match for any substring in '
                         'titles and descriptions of relevant models'),
                        ('order',
                         'String',
                         'only accepts views, -views, date, -date and returns '
                         'models in that order.'),
                        ('page',
                         'Integer',
                         'Still will flip the output to a paginated view and '
                         'include "deeplinks" for next and previous pages '))

    def get(self, request, *args, **kwargs):
        data = dict()
        data["user"] = request.user.username

        # The search filter 'algorithm' starts here
        if request.GET.get("q") is not None:
            query = request.GET.get("q")

            # Gets the QS of UserListRelations that the user has access to.
            relations = UserListRelation.objects.filter(
                Q(user=self.request.user) |
                Q(owner=self.request.user)).distinct()

            # Gets the entire search-space available to the user.
            task_list_list = TaskList.objects.filter(
                userlistrelation__in=relations).distinct()

            task_list = Task.objects.filter(
                LinkedTaskList__in=task_list_list).distinct()

            task_list_comments_list = TaskListComment.objects.filter(
                LinkedTaskList__in=task_list_list).distinct()

            task_comments_list = TaskComment.objects.filter(
                LinkedTask__in=task_list).distinct()

            # Apply the query filters
            taskList_list_unserialized = task_list_list.filter(
                Q(owner__first_name__icontains=query) |
                Q(owner__last_name__icontains=query) |
                Q(owner__username__icontains=query) |
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
            task_list_unserialized = task_list.filter(
                Q(owner__first_name__icontains=query) |
                Q(owner__last_name__icontains=query) |
                Q(owner__username__icontains=query) |
                Q(title__icontains=query)
            )
            task_list_comments_list_unserialized = \
                task_list_comments_list.filter(
                    Q(owner__first_name__icontains=query) |
                    Q(owner__last_name__icontains=query) |
                    Q(owner__username__icontains=query) |
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                )
            task_comments_list_unserialized = task_comments_list.filter(
                Q(owner__first_name__icontains=query) |
                Q(owner__last_name__icontains=query) |
                Q(owner__username__icontains=query) |
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

            # Obey the ordering.
            orderable_qs_list = [taskList_list_unserialized,
                                 task_list_unserialized,
                                 task_list_comments_list_unserialized,
                                 task_comments_list_unserialized]
            order_params = ("views", "-views", "date", "-date")
            if request.GET.get("order") in order_params:
                order = request.GET.get("order")

                if order == "views" or order == "-views":
                    for i in range(len(orderable_qs_list)):
                        orderable_qs_list[i] = \
                            orderable_qs_list[i].order_by(str(order))

                if order == "date" or order == "-date":
                    for i in range(len(orderable_qs_list)):
                        orderable_qs_list[i] = \
                            orderable_qs_list[i].order_by(str(order) +
                                                          "_created")

            # Finally serialize the links in the form of a list of lists.
            for i in orderable_qs_list:
                data[i.model.__name__] = [x.get_api_url(request) for x in i]

        # Reinvent the paginator because that Tom Christie guy fucked it up.
        if request.GET.get("page") is not None:
            page_response = dict()
            page_size = int(REST_FRAMEWORK['PAGE_SIZE'])
            page = request.GET.get("page")
            page_response["next"] = None
            page_response["previous"] = None

            # Just counts the user as 1.
            page_response["count"] = 1
            for i in orderable_qs_list:
                for j in list(data[i.model.__name__]):
                    page_response["count"] += 1

            # Start at -1 otherwise we get an off-by-one error on the
            # page_divided_data divides the list of lists into pages of lists
            page_divided_data = defaultdict(list)
            n = -1
            for i in orderable_qs_list:
                for j in list(data[i.model.__name__]):
                    n += 1
                    page_number = n.__floordiv__(int(page_size)) + 1
                    page_divided_data["page" + str(page_number)].append(
                        {i.model.__name__: j})

            # Takes the nested dicts of page_divided_data and collapses them
            paginated_nested_dict = defaultdict(list)
            for pages in page_divided_data:
                page_builder = defaultdict(list)
                for i in page_divided_data[str(pages)]:
                    for key, value in i.items():
                        if key in page_builder:
                            page_builder[key].append(value)
                        else:
                            page_builder[key] = [value]
                paginated_nested_dict[str(pages)] = page_builder

            """ I would have normally done this using a reverse_api filter
            but kwargs is an immutable field and reverse_api requires you to
            use that type of field. So its not suitable for anything that 
            isnt attatched to a serializer at the other end. Which this isnt
            So yes. The Next button reburies no less than 9 lines for itself.
            Same goes for the previous call. Im so sorry if this ever breaks.
            """
            if int(page) * int(page_size) <= int(page_response["count"]):
                GetText = str(request.get_raw_uri()).split("/")
                updated = GetText[-1]
                substring = GetText[-1].find("page=")
                prelim = updated[:substring + 5] + str(
                    int(updated[substring + 5:substring + 6]) + 1
                )
                newUrl = '/'.join(GetText[:-1]) + prelim
                page_response["next"] = newUrl

            # Does the same as the one above it but instead of +1 it goes -1
            if int(page) > 1:
                GetText = str(request.get_raw_uri()).split("/")
                updated = GetText[-1]
                substring = GetText[-1].find("page=")
                prelim = updated[:substring + 5] + str(
                    int(updated[substring + 5:substring + 6]) - 1
                )
                newUrl = '/'.join(GetText[:-1]) + prelim
                page_response["previous"] = newUrl

            # And just like that i can never come back to this code ever again.
            page_response["results"] = paginated_nested_dict[
                "page" + str(page)]
            return Response(page_response)

        # Return the final data no matter what it looks like.
        return Response(data)


class UserCreateAPI(APIView):
    """
    post:
        Create a new user.
    """
    serializer_class = UserSerializer
    """
    Creates the user
    """

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                data = serializer.data
                data['password'] = "Password was hidden for safety reasons."
                return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response({"data provided could not be validated."},
                            status=status.HTTP_400_BAD_REQUEST)
