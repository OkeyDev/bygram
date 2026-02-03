import sys
from io import StringIO
from typing import TextIO

import requests

from compiler.logic import process_file

TL_URL = "https://raw.githubusercontent.com/tdlib/td/refs/heads/master/td/generate/scheme/td_api.tl"


def get_reader(file_link: str) -> TextIO:
    if file_link.startswith("http"):
        resp = requests.get(file_link)
        resp.raise_for_status()
        return StringIO(resp.text)
    else:
        with open(file_link, "r") as file:
            data = file.read()
        return StringIO(data)


def main():
    args = sys.argv
    if len(args) < 3:
        print(f"Usage: {args[0]} input_file output_file")
        print("Exports telegram tl file to python objects")
        return

    input_file = get_reader(args[1])
    with open(sys.argv[2], "w") as output_file:
        count = process_file(input_file, output_file)

    print(f"Processed {count} definitions")


if __name__ == "__main__":
    main()
