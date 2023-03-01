import argparse

from src.build import Build


def main():
    parser = argparse.ArgumentParser("revanced_build")

    parser.add_argument("--app", help="Target build app", type=str)

    args = parser.parse_args()

    build = Build(args)

    build.runBuild()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        exit(1)
