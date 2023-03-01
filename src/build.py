import os
import subprocess

from colorama import Fore, Style

from src._config import config
from src.downloader import Downloader


class Build(object):
    def __init__(self, args):
        # Generate the build dir if it doesn't exist
        if not os.path.exists(config["dist_dir"]):
            os.mkdir(config["dist_dir"])

        self.args = args
        self.check_java_version()
        self.download_files = Downloader().download_required()

    def runBuild(self):
        target_app = self.args.app

        input_apk_filepath = Downloader().download_apk(target_app)

        print(Fore.BLUE + f"🔥 Running build for {target_app}:" + Style.RESET_ALL)

        # Run the build
        process = subprocess.Popen(
            [
                "java",
                "-jar",
                self.download_files["revanced-cli"],
                "--bundle",
                self.download_files["revanced-patches"],
                "--apk",
                input_apk_filepath,
                "--out",
                f"./{config['dist_dir']}/output-{target_app}.apk",
                "-m",
                self.download_files["revanced-integrations"],
                "--keystore",
                config["keystore_path"],
            ],
            stdout=subprocess.PIPE,
        )

        output = process.stdout

        # Stream the output to the console
        for line in output:
            print(line.decode("utf-8"), end="")

        if not output:
            raise Exception(
                Fore.RED + "An error occurred while running the Java program"
            )

    def check_java_version(self):
        version = subprocess.check_output(
            ["java", "-version"], stderr=subprocess.STDOUT
        ).decode("utf-8")

        if "17" not in version:
            raise Exception(Fore.RED + "Java 17 is required to run the build.")

        print(Fore.GREEN + "✅ Java 17 is installed" + Style.RESET_ALL)
