from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from recipes.models import Tag, Recipe
import glob
import os
import string
import json


def make_context():
    context = {
        'recipes': Recipe,
        'tags': Tag
    }

    return context


def index(request):
    return render(request, 'home.html', make_context())


def recipe(_, recipe=None):
    link = 'pages/{recipe}.pdf'.format(recipe=recipe)

    with open(link, 'rb') as in_file:
        data = in_file.read()

    response = HttpResponse(data, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename={recipe}.pdf'.format(recipe=recipe)

    return response


def tag_manager(request):
    return render(request, 'tag_manager.html', make_context())


def recipe_manager(request):
    return render(request, 'recipe_manager.html', make_context())


def add_tag(request):
    request_data = json.loads(request.body.decode())
    tag_name = request_data.get('tag')
    if not tag_name:
        return JsonResponse(dict(status='error', error='Must specify tag name'))

    if Tag.exists(name=tag_name):
        return JsonResponse(dict(status='error', error='Tag Exists'))

    tag = Tag(name=tag_name)
    tag.save()

    return JsonResponse(dict(status='success'))


def remove_tag(request):
    request_data = json.loads(request.body.decode())
    tag_name = request_data.get('tag_name')
    if not tag_name:
        return JsonResponse(dict(status='error', error='Must specify a tag name'))

    if not Tag.exists(name=tag_name):
        return JsonResponse(dict(status='error', error='Could not find tag'))

    existing_tag = Tag.objects.get(name=tag_name)
    existing_tag.delete()

    return JsonResponse(dict(status='success'))


def get_tags(_):
    tags = sorted(x.name for x in Tag.objects.all())
    return JsonResponse(dict(status='success', tags=tags))


def get_recipes(_):
    recipes = list()
    for recipe in Recipe.objects.all():
        recipes.append(recipe.as_dict())

    return JsonResponse(dict(status='success', recipes=recipes))


def add_tag_to_recipe(request):
    request_data = json.loads(request.body.decode())
    recipe_name = request_data.get('recipe_name')
    tag_name = request_data.get('tag_name')

    if not recipe_name:
        return JsonResponse(dict(status='error', error='Must specify recipe_name'))

    if not tag_name:
        return JsonResponse(dict(status='error', error='Must specify tag_name'))

    if not Recipe.exists(name=recipe_name):
        return JsonResponse(dict(status='error', error='Recipe does not exist'))

    if not Tag.exists(name=tag_name):
        return JsonResponse(dict(status='error', error='Tag does not exist'))

    tag = Tag.objects.get(name=tag_name)
    recipe_obj = Recipe.objects.get(name=recipe_name)

    recipe_obj.tags.add(tag)
    recipe_obj.save()

    return JsonResponse(dict(status='success', recipe_name=recipe_name, tag_name=tag_name))


def remove_tag_from_recipe(request):
    request_data = json.loads(request.body.decode())
    recipe_name = request_data.get('recipe_name')
    tag_name = request_data.get('tag_name')

    if not recipe_name:
        return JsonResponse(dict(status='error', error='Must specify recipe_name'))

    if not tag_name:
        return JsonResponse(dict(status='error', error='Must specify tag_name'))

    if not Recipe.exists(name=recipe_name):
        return JsonResponse(dict(status='error', error='Recipe does not exist'))

    if not Tag.exists(name=tag_name):
        return JsonResponse(dict(status='error', error='Tag does not exist'))

    tag = Tag.objects.get(name=tag_name)
    recipe_obj = Recipe.objects.get(name=recipe_name)

    recipe_obj.tags.remove(tag)
    recipe_obj.save()

    return JsonResponse(dict(status='success', recipe_name=recipe_name, tag_name=tag_name))


def collect_recipes(_):
    num_recipes = 0
    for recipe_file in sorted(glob.glob(os.path.join('pages', '*.pdf'))):
        recipe_file_name = os.path.basename(recipe_file).split('.')[0]

        recipe_name = string.capwords(recipe_file_name.replace('_', ' '))
        recipe_link = f'recipe/{recipe_file_name}'

        if Recipe.exists(name=recipe_name):
            recipe_obj = Recipe.objects.filter(name=recipe_name).first()
        else:
            recipe_obj = Recipe(name=recipe_name)

        recipe_obj.link = recipe_link
        recipe_obj.save()

        num_recipes += 1

    return JsonResponse(dict(status='success', recipes_loaded=num_recipes))
