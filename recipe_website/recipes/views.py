from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import os
from PIL import Image

from pdf2image import convert_from_path
import platform
import glob

import os
import shutil
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


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
        recipes=sorted(
            [Recipe(name=os.path.basename(r).split(".")[0], link=r) for r in recipes],
            key=lambda r: r.name,
        ),
        subsets=sorted(
            os.path.basename(d) for d in glob.glob("pages/*") if os.path.isdir(d)
        ),
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


FOLDERS = "application/vnd.google-apps.folder"


class File:
    def __init__(self, id, name, md5Checksum=None, **kwargs):
        if kwargs:
            raise RuntimeError(f"Extra kwargs {kwargs}")

        self.id = id
        self.name = name
        self.md5 = md5Checksum

    def __repr__(self):
        return f"{self.id=}, {self.name=}, {self.md5=}"


def get_files(service, directory=None, mime_type=None) -> List[File]:
    params = dict(
        pageSize=50,
        fields="files(id, name, md5Checksum)",
    )

    query_params = []
    if directory is not None:
        query_params.append(f"'{directory}' in parents")

    if mime_type is not None:
        query_params.append(f"mimeType='{mime_type}'")

    if query_params:
        params["q"] = " & ".join(query_params)

    results = service.files().list(**params).execute()

    ret = []
    for item in results.get("files", [""]):
        ret.append(File(**item))

    return ret


def refresh_recipes(request):
    if os.path.exists("pages"):
        shutil.rmtree("pages")

    creds = service_account.Credentials.from_service_account_file(
        "recipes.json",
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )

    service = build("drive", "v3", credentials=creds)

    for folder in get_files(service=service, mime_type=FOLDERS):
        if folder.name == "Recipes":
            continue

        directory = f"pages/{folder.name}"
        os.makedirs(directory, exist_ok=True)
        for recipe in get_files(service=service, directory=folder.id):
            request = service.files().get_media(fileId=recipe.id)
            with open(f"{directory}/{recipe.name}", "wb") as out_file:
                downloader = MediaIoBaseDownload(out_file, request)
                done = False
                while done is False:
                    _, done = downloader.next_chunk()

    return HttpResponseRedirect("/")
