from __future__ import print_function

import os
import shutil
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


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


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = service_account.Credentials.from_service_account_file(
        "recipes.json",
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )

    service = build("drive", "v3", credentials=creds)
    shutil.rmtree("pages")
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


if __name__ == "__main__":
    main()
