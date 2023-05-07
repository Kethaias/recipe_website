from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os
from PIL import Image

from pdf2image import convert_from_path
from recipes.models import Tag, Recipe
import platform
import glob


class Recipe:
    def __init__(self, name, link):
        self.name = name
        self.link = link


def make_context(subset=""):
    recipes = []
    if subset:
        recipes += list(glob.glob(f"pages/{subset}/*.png"))
    else:
        recipes += list(glob.glob("pages/*.png"))
        recipes += list(glob.glob("pages/*/*.png"))

    return dict(
        recipes=[
            Recipe(name=os.path.basename(r).split(".")[0], link=r) for r in recipes
        ],
        subsets=[os.path.basename(d) for d in glob.glob("pages/*") if os.path.isdir(d)],
    )


def index(request, subset=""):
    return render(
        request,
        "home.html",
        make_context(
            subset=subset,
        ),
    )


def recipe(request, recipe):
    if platform.system() == "Windows":
        cache_file_path = "pages/cache.txt"
        first_recipe = 10
        if os.path.exists(cache_file_path):
            with open(cache_file_path, "r") as in_file:
                content = in_file.readline().strip()
                first_recipe = int(content)

        pages = convert_from_path(
            "pages/recipes.pdf",
            200,
            first_page=first_recipe,
            poppler_path="C:\\Users\\brand\\Downloads\\poppler-23.01.0\\Library\\bin",
        )

        with open(cache_file_path, "w") as out_file:
            print(first_recipe + len(pages), file=out_file)

        for index, page in enumerate(pages, start=first_recipe + 1):
            image = page.resize((1700, 2200))
            image.save(f"pages/{index}.png")

    possibilities = glob.glob(f"pages/*/{recipe}.png")
    with open(possibilities[0], "rb") as in_file:
        return HttpResponse(in_file.read(), content_type="image/png")
