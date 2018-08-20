from rest_framework import permissions, status
from rest_framework.response import Response

from taskMaster.models import TaskList, UserListRelation, Task, \
    TaskComment, TaskListComment


class IsAdminOrUserRelatedReadOnlyOr401(permissions.BasePermission):
    """
    This is the TaskList permission settings. Its both responsible for read and
    object level -permissions.
    It will grant read permission to users who are UserListRealted to this
    list or to the user who made this model.
    It will grant object level permission to admins of this task list. So that
    means any user who has a user list relation with the role field slotted
    as "admin" without the marks, or the owner himself.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if obj.has_user_relation(obj, request.user) is True:
                return True

        if obj.user_is_admin(obj, request.user) is True:
            return True

        return False


class IsTaskListRelatedOr401(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if type(obj) in (Task, TaskComment, TaskListComment):
            if obj.LinkedTaskList.has_user_relation(obj.LinkedTaskList,
                                                    request.user):
                if request.method in permissions.SAFE_METHODS:
                    return True  # Allow view only.
            else:
                return True

        return False


class CRUDOnlyRelatedTaskList(permissions.BasePermission):
    """
    This is the Task permission settings. Its both responsible for read and
    object level -permissions.
    It will grant read permission to users who are UserListRealted to this
    tasks tasklist model or to the user who made this model.
    It will grant object level permission to admins of this tasks list. So that
    means any user who has a user list relation with the role field slotted
    as "admin" without the marks, or the owner himself.
    """
    def has_object_permission(self, request, view, obj):
        # Restricted field manipulation should get rejected at runtime.
        Task_list = obj.LinkedTaskList
        if request.data.get('LinkedTaskList') is not None:
            temp = TaskList.objects.get(pk=request.data.get('LinkedTaskList'))
            if temp.user_is_admin(temp, request.user) is True:
                return True  # User is an admin or owner of the new list.
            else:
                return False

        if Task_list.has_user_relation(Task_list, request.user) is True:
            if request.method in permissions.SAFE_METHODS:
                return True  # Allow view only.
            if Task_list.user_is_admin(Task_list, request.user) is True:
                return True  # Allow edit.

        return False


class CRUDTaskComments(permissions.BasePermission):
    """ Has object permission in class works differnetly. The owner should be
    able to switch to comment inbetween tasks but we should check if they
    have access to the tasks if they wish to change related tasks.
    First check if its the owner thats making a change if not, return false
    """
    def has_object_permission(self, request, view, obj):
        # Get the relevant LinkedTaskList and from there find auth.
        task = obj.LinkedTask
        Task_list = task.LinkedTaskList
        if request.data.get('LinkedTask') is not None:
            task = Task.objects.get(pk=request.data.get('LinkedTask'))
            if task.owner == request.user:
                return True  # User is an admin or owner of the new list.
            else:
                return False

        if Task_list.has_user_relation(Task_list, request.user) is True:
            if request.method in permissions.SAFE_METHODS:
                return True  # Allow view only.
            if obj.owner == request.user:
                return True  # Allow edit.
        return False


class CRUDTaskListComments(permissions.BasePermission):
    """ This class is pretty straight forward, if youre the owner you can
    change the relational field. If you want to change the relational field
    you have to have access to the item within that field.
    If you wanna access this data point you have to have a userrelation or
    you can get returned false. """
    def has_object_permission(self, request, view, obj):
        # Get the relevant LinkedTaskList and from there find auth.
        Task_list = obj.LinkedTaskList
        if request.data.get('LinkedTaskList') is not None:
            temp = TaskList.objects.get(pk=request.data.get('LinkedTaskList'))
            if temp.user_is_admin(temp, request.user) is True:
                return True  # User is an admin or owner of the new list.
            else:
                return False

        if Task_list.has_user_relation(Task_list, request.user) is True:
            if request.method in permissions.SAFE_METHODS:
                return True  # Allow view only.
            if Task_list.user_is_admin(Task_list, request.user) is True:
                return True  # Allow edit.

        if obj.owner == request.user:
            return True

        return False


class CRUDUserListRelation(permissions.BasePermission):
    """
    This is the UserListRelation permission settings. Its both responsible for
    read and object level -permissions.
    It will grant read permission to users who are related to this model.
    It will grant object level permission to the owner or admin only.
    """
    def has_object_permission(self, request, view, obj):
        temp = obj.LinkedTaskList
        if request.data.get('LinkedTaskList') is not None:
            # Remarks temp so that it may fail at the bottom. No need to
            # Check immediately.
            temp = TaskList.objects.get(pk=request.data.get('LinkedTaskList'))

        # Checks if user is owner in order to alter owner field.
        if request.data.get("owner") is not None:
            if obj.owner == request.user:
                return True

        # Checks for standard read write instead of specific fields
        if obj.owner == request.user:
            return True  # Edit access granted to owner of model.

        if temp.has_user_relation(temp, request.user) is True:
            if request.method in permissions.SAFE_METHODS is True:
                return True  # Read only access granted by to a non admin
            else:
                if temp.user_is_admin(temp, request.user) is True:
                    return True
        return False
