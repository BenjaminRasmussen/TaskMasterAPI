"""TaskMasterAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

schema_view = get_schema_view(title='Task Master Api',
                              renderer_classes=[OpenAPIRenderer,
                                                SwaggerUIRenderer])
urlpatterns = [
    url(r'^', include('drf_autodocs.urls')),
    url('admin/', admin.site.urls),
    url('^api/v1.0/TaskMaster/', include(('taskMaster.api.urls', 'taskMaster'),
                                         namespace='taskMaster-api')),

]
