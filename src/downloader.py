import json
import os
from distutils.version import StrictVersion

import requests
from colorama import Fore, Style

from src._config import config
from src.apkmirror import APKmirror


class Downloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "anything"

    def _download(self, url: str, name: str) -> str:
        filepath = f"./{config['dist_dir']}/{name}"

        # Check if the tool exists
        if os.path.exists(filepath):
            print(
                Fore.YELLOW
                + f"⚠️ {filepath} already exists, skipping"
                + Style.RESET_ALL
            )
            return filepath

        with self.session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        print(Fore.GREEN + f"✅ {filepath} downloaded" + Style.RESET_ALL)
        return filepath

    def download_required(self):
        print(Fore.BLUE + "⬇️ Downloading required resources" + Style.RESET_ALL)

        # Get the tool list
        tools = requests.get("https://releases.revanced.app/tools").json()

        # Download the tools
        download_repository = [
            "revanced/revanced-cli",
            "revanced/revanced-patches",
            "revanced/revanced-integrations",
        ]

        downloaded_files = {}

        for tool in tools["tools"]:
            if tool["repository"] in download_repository:
                filepath = self._download(tool["browser_download_url"], tool["name"])

                name = tool["repository"].replace("revanced/", "")

                downloaded_files[name] = filepath

        return downloaded_files

    def download_apk(self, app_name: str):
        # Load from patches.json
        with open(f"./{config['dist_dir']}/patches.json", "r") as patches_file:
            patches = json.load(patches_file)

            # Reference APK app name
            app = {
                "youtube": {
                    "name": "com.google.android.youtube",
                    "apkmirror": "google-inc/youtube/youtube",
                },
                "youtube-music": {
                    "name": "com.google.android.apps.youtube.music",
                    "apkmirror": "google-inc/youtube-music/youtube-music",
                },
            }

            for patch in patches:
                for package in patch["compatiblePackages"]:
                    if package["name"] == app[app_name]["name"]:
                        versions = package["versions"]

                        version = max(versions, key=StrictVersion)

                        page = f"https://www.apkmirror.com/apk/{app[app_name]['apkmirror']}-{version}-release/"

                        download_page = APKmirror().get_download_page(url=page)

                        href = APKmirror().extract_download_link(download_page)

                        filename = f"{app[app_name]['name']}-{version}.apk"

                        return self._download(href, filename)
