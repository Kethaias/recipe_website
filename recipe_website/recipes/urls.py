"""recipe_website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, re_path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^recipe/(?P<recipe>\w+)/$', views.recipe, name='recipe'),
    path(r'recipe_manager/', views.recipe_manager, name='recipe_manager'),

    path(r'add_tag', views.add_tag, name='add_tag'),
    path(r'remove_tag', views.remove_tag, name='remove_tag'),
    path(r'get_tags', views.get_tags, name='get_tags'),
    path(r'get_recipes', views.get_recipes, name='get_recipes'),
    path(r'add_tag_to_recipe', views.add_tag_to_recipe, name='add_tag_to_recipe'),
    path(r'remove_tag_from_recipe', views.add_tag_to_recipe, name='add_tag_to_recipe'),
    path(r'collect_recipes', views.collect_recipes, name='collect_recipes'),

    path('', views.index, name='index'),
]
