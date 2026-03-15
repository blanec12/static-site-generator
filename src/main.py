import sys
from copystatic import copy_static_to_public
from utils import generate_pages_recursive


def main():

    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = "/"

    print(basepath)

    copy_static_to_public("static", "docs")
    generate_pages_recursive("content", "template.html", "docs", basepath)


if __name__ == "__main__":
    main()
