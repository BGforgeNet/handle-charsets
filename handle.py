#!/usr/bin/env python3

import argparse
import os
import sys

parser = argparse.ArgumentParser(
    description="Convert TRA files from Windows-specific encoding to UTF-8",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument("--tra-path", dest="tra_path", help="source tra directory path", required=True)
parser.add_argument("--out-path", dest="out_path", help="directory path for converted files", required=True)
parser.add_argument("--from-utf8", dest="from_utf8", help="reverse conversion", action="store_true", default=False)
parser.add_argument(
    "--split-console",
    dest="split_console",
    help="Generate separate console message files from setup.tra and install.tra."
    "This will create setup-win32.tra, setup-unix.tra, etc for each OS with correct encoding.",
    action="store_true",
    default=False,
)
args = parser.parse_args()

# these files are assumed to be in system encoding always
CONSOLE_FILES = ["setup.tra", "install.tra"]

CHARSET_MAP = {
    "schinese": "cp936",
    "zh_CN": "cp936",
    "tchinese": "cp950",
    "czech": "cp1250",
    "cs_CZ": "cp1250",
    "english": "cp1252",
    "american": "cp1252",
    "en_US": "cp1252",
    "french": "cp1252",
    "francais": "cp1252",
    "fr_FR": "cp1252",
    "german": "cp1252",
    "deutsch": "cp1252",
    "de_DE": "cp1252",
    "italian": "cp1252",
    "italiano": "cp1252",
    "it_IT": "cp1252",
    "japanese": "cp932",
    "ja_JP": "cp932",
    "korean": "cp932",
    "ko_KR": "cp932",
    "polish": "cp1250",
    "polski": "cp1250",
    "pl_PL": "cp1250",
    "portuguese": "cp1252",
    "pt_BR": "cp1252",
    "russian": "cp1251",
    "ru_RU": "cp1251",
    "spanish": "cp1252",
    "castilian": "cp1252",
    "espanol": "cp1252",
    "castellano": "cp1252",
    "es_ES": "cp1252",
    "swedish": "cp1252",
    "sw_SE": "cp1252",
    "ukrainian": "cp1251",
    "uk_UA": "cp1251",
}

COMMENT_NO_MANUAL = (
    "// Do not edit manually. This file is generated automatically by handle-charsets. Your changes will be lost.\n\n"
)


def resave_file(src_path, src_enc, dst_path, dst_enc):
    """
    Read source file with source encoding and save it to destination with another encoding
    """
    print(f"{src_path}, {src_enc}\t=>\t{dst_path}, {dst_enc}")

    with open(src_path, encoding=src_enc) as ifile:
        data = ifile.read()

    # prepare directory
    dst_dir = os.path.dirname(dst_path)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    else:
        if not os.path.isdir(dst_dir):
            os.remove(dst_dir)
            os.makedirs(dst_dir)

    data = COMMENT_NO_MANUAL + data
    with open(dst_path, mode="w", encoding=dst_enc) as ofile:
        ofile.write(data)


def find_files(path, ext):
    """
    @path: directory path
    @ext: file extension

    Returns a list of files with this extensions
    """
    flist = []
    for root, dirs, files in os.walk(path, followlinks=True):  # pylint: disable=unused-variable
        for fname in files:
            if fname.lower().endswith(ext.lower()):
                flist.append(os.path.join(root, fname))
    flist = sorted(flist)
    return flist


def get_win_encoding(language, file_path):
    """
    Determines windows-specific encoding for the file
    """
    if "_" not in language:
        language = language.lower()

    filename = get_filename(file_path)
    if filename in CONSOLE_FILES and language in ["russian", "ukrainian", "ru_RU", "uk_UA"]:
        return "cp866"

    if filename == "ee.tra" or filename.endswith("_ee.tra"):
        return "utf-8"

    if language in CHARSET_MAP:
        encoding = CHARSET_MAP[language]
        return encoding

    print(f"Failed to infer encoding for file {file_path} in language {language}")
    sys.exit(1)


def get_dst_encoding(language, file_path, from_utf8):
    """
    Return encoding to save the converted file in.
    """

    # Console messages always should be in native encoding.
    filename = get_filename(file_path)
    if from_utf8 or filename in CONSOLE_FILES:
        return get_win_encoding(language, file_path)

    return "utf-8"


def get_src_encoding(language, file_path, from_utf8):
    """
    Return encoding to read the source file in
    """
    filename = get_filename(file_path)
    if from_utf8 and filename not in CONSOLE_FILES:
        return "utf-8"
    return get_win_encoding(language, file_path)


def get_language(dirpath):
    """
    Gets language component from tra directory path
    """
    return dirpath.split(os.path.sep)[0]


def get_relpath(tra_file, tra_path):
    """
    Returns tra_file's path relative to tra_path
    """
    relpath = os.path.relpath(tra_file, start=tra_path)
    return relpath


def get_dirpath(tra_relpath):
    """
    Returns tra_file's directory component relative to tra_path
    """
    dirpath = os.path.dirname(tra_relpath)
    return dirpath


def get_filename(filepath):
    """
    Returns lowecased basename
    """
    return os.path.basename(filepath).lower()


def get_os_path(relpath, weidu_os):
    """
    Takes relative console tra file path, returns OS-specific file path for it:
    tra/setup.tra -> tra/setup-win32.tra
    """
    dirname = get_dirpath(relpath)
    filename = get_filename(relpath)
    base, ext = os.path.splitext(filename)
    filename = f"{base}-{weidu_os}{ext}"
    os_path = os.path.join(dirname, filename)
    return os_path


def main():
    """Main function"""
    tra_files = find_files(args.tra_path, "tra")
    for tra_file in tra_files:
        relpath = get_relpath(tra_file, args.tra_path)
        dirpath = get_dirpath(relpath)
        language = get_language(dirpath)
        src_encoding = get_src_encoding(language, tra_file, args.from_utf8)
        dst_encoding = get_dst_encoding(language, tra_file, args.from_utf8)
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
