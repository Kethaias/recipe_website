from django.shortcuts import render
from django.http import HttpResponse, FileResponse
import glob
import os
import string


def make_recipe(recipe_file):
    recipe_link = os.path.basename(recipe_file).split('.')[0]
    recipe_name = string.capwords(recipe_link.replace('_', ' '))

    return dict(name=recipe_name, link='recipe/{recipe}'.format(recipe=recipe_link))


def index(request):
    recipes = list()
    for pdf_file in sorted(glob.glob(os.path.join('pages', '*.pdf'))):
        recipes.append(make_recipe(pdf_file))

    context = {
        'recipes': recipes
    }

    return render(request, 'home.html', context)


def recipe(request, recipe=None):
    link = 'pages/{recipe}.pdf'.format(recipe=recipe)

    with open(link, 'rb') as in_file:
        data = in_file.read()

    response = HttpResponse(data, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename={recipe}.pdf'.format(recipe=recipe)

    return response
