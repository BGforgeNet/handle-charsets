#!/usr/bin/env python3

import argparse
import os
import sys

# If split_console is true, these files should be in ANSI encoding
# Otherwise, in UTF-8
CONSOLE_FILES = ["setup.tra", "install.tra"]

# Keys are lowercase to allow case-insensitive lookup.
CHARSET_MAP = {
    "schinese": "cp936",
    "zh_cn": "cp936",
    "tchinese": "cp950",
    "czech": "cp1250",
    "cs_cz": "cp1250",
    "english": "cp1252",
    "american": "cp1252",
    "en_us": "cp1252",
    "french": "cp1252",
    "francais": "cp1252",
    "fr_fr": "cp1252",
    "german": "cp1252",
    "deutsch": "cp1252",
    "de_de": "cp1252",
    "italian": "cp1252",
    "italiano": "cp1252",
    "it_it": "cp1252",
    "japanese": "cp932",
    "ja_jp": "cp932",
    "korean": "cp932",
    "ko_kr": "cp932",
    "polish": "cp1250",
    "polski": "cp1250",
    "pl_pl": "cp1250",
    "portuguese": "cp1252",
    "pt_br": "cp1252",
    "russian": "cp1251",
    "ru_ru": "cp1251",
    "spanish": "cp1252",
    "castilian": "cp1252",
    "espanol": "cp1252",
    "castellano": "cp1252",
    "es_es": "cp1252",
    "swedish": "cp1252",
    "sw_se": "cp1252",
    "ukrainian": "cp1251",
    "uk_ua": "cp1251",
}

COMMENT_NO_MANUAL = (
    "// Do not edit. This file is generated automatically by handle-charsets. Your changes will be lost.\n\n"
)


def resave_file(src_path: str, src_enc: str, dst_path: str, dst_enc: str) -> None:
    """Read source file with source encoding and save it to destination with another encoding."""
    print(f"{src_path}, {src_enc}\t=>\t{dst_path}, {dst_enc}")

    with open(src_path, encoding=src_enc) as ifile:
        data = ifile.read()

    # prepare directory
    dst_dir = os.path.dirname(dst_path)
    if dst_dir and not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    elif dst_dir and not os.path.isdir(dst_dir):
        os.remove(dst_dir)
        os.makedirs(dst_dir)

    data = COMMENT_NO_MANUAL + data
    with open(dst_path, mode="w", encoding=dst_enc) as ofile:
        ofile.write(data)


def find_files(path: str, ext: str) -> list[str]:
    """Return a sorted list of files under path matching the given extension."""
    ext_lower = ext.lower()
    flist = []
    for root, _dirs, files in os.walk(path, followlinks=True):
        for fname in files:
            if fname.lower().endswith(ext_lower):
                flist.append(os.path.join(root, fname))
    return sorted(flist)


def get_win_encoding(language: str, file_path: str) -> str:
    """Determine the Windows-specific encoding for the file.

    Raises ValueError for unknown languages.
    """
    language = language.lower()
    filename = get_filename(file_path)

    if filename in CONSOLE_FILES and language in ("russian", "ukrainian", "ru_ru", "uk_ua"):
        return "cp866"

    if filename == "ee.tra" or filename.endswith("_ee.tra"):
        return "utf-8"

    if language in CHARSET_MAP:
        return CHARSET_MAP[language]

    raise ValueError(f"Failed to infer encoding for file {file_path} in language {language}")


def get_dst_encoding(language: str, file_path: str, from_utf8: bool, split_console: bool) -> str:
    """Return the encoding to save the converted file in."""
    filename = get_filename(file_path)

    # Console messages should be in UTF-8, unless we're splitting them.
    if filename in CONSOLE_FILES:
        if split_console:
            return get_win_encoding(language, file_path)
        return "utf-8"

    if from_utf8:
        return get_win_encoding(language, file_path)

    return "utf-8"


def get_src_encoding(language: str, file_path: str, from_utf8: bool) -> str:
    """Return the encoding to read the source file in."""
    filename = get_filename(file_path)

    # Source console messages are assumed to be in UTF-8 for new WeiDU.
    if filename in CONSOLE_FILES:
        return "utf-8"

    if from_utf8:
        return "utf-8"
    return get_win_encoding(language, file_path)


def get_language(dirpath: str) -> str:
    """Extract the language component from a tra directory path."""
    return dirpath.split(os.path.sep)[0]


def get_relpath(tra_file: str, tra_path: str) -> str:
    """Return tra_file's path relative to tra_path."""
    return os.path.relpath(tra_file, start=tra_path)


def get_dirpath(tra_relpath: str) -> str:
    """Return the directory component of a relative tra path."""
    return os.path.dirname(tra_relpath)


def get_filename(filepath: str) -> str:
    """Return the lowercased basename of a path."""
    return os.path.basename(filepath).lower()


def get_os_path(relpath: str, weidu_os: str) -> str:
    """Return the OS-specific file path for a console tra file.

    Example: tra/setup.tra + win32 -> tra/setup-win32.tra
    """
    dirname = get_dirpath(relpath)
    filename = get_filename(relpath)
    base, ext = os.path.splitext(filename)
    filename = f"{base}-{weidu_os}{ext}"
    return os.path.join(dirname, filename)


def main() -> None:
    """Parse arguments and convert TRA files."""
    parser = argparse.ArgumentParser(
        description="Convert TRA files from Windows-specific encoding to UTF-8 and back",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--tra-path", dest="tra_path", help="source tra directory path", required=True)
    parser.add_argument("--out-path", dest="out_path", help="directory path for converted files", required=True)
    parser.add_argument(
        "--from-utf8",
        dest="from_utf8",
        help="reverse conversion: from ANSI to UTF-8",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--split-console",
        dest="split_console",
        help="Generate separate console message files from setup.tra and install.tra."
        "This will create setup-win32.tra, setup-unix.tra, etc for each OS with ANSI encoding.",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    tra_files = find_files(args.tra_path, "tra")
    for tra_file in tra_files:
        relpath = get_relpath(tra_file, args.tra_path)
        dirpath = get_dirpath(relpath)
        language = get_language(dirpath)
        try:
            src_encoding = get_src_encoding(language, tra_file, args.from_utf8)
            dst_encoding = get_dst_encoding(language, tra_file, args.from_utf8, args.split_console)
        except ValueError as exc:
            print(exc)
            sys.exit(1)
        tra_out_file = os.path.join(args.out_path, relpath)
        filename = get_filename(relpath)

        if args.split_console and filename in CONSOLE_FILES:
            console_out_file = get_os_path(tra_out_file, "win32")
            resave_file(tra_file, src_encoding, console_out_file, dst_encoding)
            for weidu_os in ["unix", "osx"]:
                console_out_file = get_os_path(tra_out_file, weidu_os)
                resave_file(tra_file, src_encoding, console_out_file, "utf-8")
        else:
            resave_file(tra_file, src_encoding, tra_out_file, dst_encoding)


if __name__ == "__main__":
    main()
