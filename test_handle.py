"""Tests for handle.py charset conversion logic."""

import os
import sys
import tempfile

import pytest

import handle


# ---------------------------------------------------------------------------
# get_language
# ---------------------------------------------------------------------------


def test_get_language_simple():
    assert handle.get_language(os.path.join("russian", "subdir")) == "russian"


def test_get_language_top_level():
    assert handle.get_language("english") == "english"


def test_get_language_locale_code():
    assert handle.get_language(os.path.join("ru_RU", "subdir")) == "ru_RU"


# ---------------------------------------------------------------------------
# get_filename
# ---------------------------------------------------------------------------


def test_get_filename_lowercases():
    assert handle.get_filename("/path/to/Setup.TRA") == "setup.tra"


def test_get_filename_already_lower():
    assert handle.get_filename("/path/component.tra") == "component.tra"


# ---------------------------------------------------------------------------
# get_win_encoding
# ---------------------------------------------------------------------------


def test_get_win_encoding_russian_console():
    # Russian console files use DOS cp866
    assert handle.get_win_encoding("russian", "setup.tra") == "cp866"
    assert handle.get_win_encoding("russian", "install.tra") == "cp866"


def test_get_win_encoding_ukrainian_console():
    assert handle.get_win_encoding("ukrainian", "setup.tra") == "cp866"


def test_get_win_encoding_ru_RU_console():
    assert handle.get_win_encoding("ru_RU", "setup.tra") == "cp866"


def test_get_win_encoding_russian_non_console():
    assert handle.get_win_encoding("russian", "component.tra") == "cp1251"


def test_get_win_encoding_english():
    assert handle.get_win_encoding("english", "component.tra") == "cp1252"


def test_get_win_encoding_case_insensitive():
    assert handle.get_win_encoding("Russian", "component.tra") == "cp1251"
    assert handle.get_win_encoding("English", "component.tra") == "cp1252"


def test_get_win_encoding_japanese():
    assert handle.get_win_encoding("japanese", "component.tra") == "cp932"


def test_get_win_encoding_ee_tra():
    assert handle.get_win_encoding("russian", "ee.tra") == "utf-8"


def test_get_win_encoding_underscore_ee_tra():
    assert handle.get_win_encoding("russian", "component_ee.tra") == "utf-8"


def test_get_win_encoding_unknown_language_raises():
    with pytest.raises(ValueError, match="klingon"):
        handle.get_win_encoding("klingon", "component.tra")


def test_get_win_encoding_locale_codes():
    assert handle.get_win_encoding("zh_CN", "component.tra") == "cp936"
    assert handle.get_win_encoding("cs_CZ", "component.tra") == "cp1250"
    assert handle.get_win_encoding("de_DE", "component.tra") == "cp1252"


# ---------------------------------------------------------------------------
# get_src_encoding
# ---------------------------------------------------------------------------


def test_get_src_encoding_console_always_utf8():
    assert handle.get_src_encoding("russian", "setup.tra", from_utf8=False) == "utf-8"
    assert handle.get_src_encoding("russian", "install.tra", from_utf8=False) == "utf-8"


def test_get_src_encoding_from_utf8_flag():
    assert handle.get_src_encoding("russian", "component.tra", from_utf8=True) == "utf-8"


def test_get_src_encoding_ansi_source():
    assert handle.get_src_encoding("russian", "component.tra", from_utf8=False) == "cp1251"


def test_get_src_encoding_english_ansi():
    assert handle.get_src_encoding("english", "component.tra", from_utf8=False) == "cp1252"


# ---------------------------------------------------------------------------
# get_dst_encoding
# ---------------------------------------------------------------------------


def test_get_dst_encoding_console_utf8_by_default():
    assert handle.get_dst_encoding("russian", "setup.tra", from_utf8=False, split_console=False) == "utf-8"
    assert handle.get_dst_encoding("english", "install.tra", from_utf8=False, split_console=False) == "utf-8"


def test_get_dst_encoding_console_split_russian():
    # split_console=True → ANSI; Russian console = cp866
    assert handle.get_dst_encoding("russian", "setup.tra", from_utf8=False, split_console=True) == "cp866"


def test_get_dst_encoding_console_split_english():
    assert handle.get_dst_encoding("english", "setup.tra", from_utf8=False, split_console=True) == "cp1252"


def test_get_dst_encoding_non_console_to_utf8():
    assert handle.get_dst_encoding("russian", "component.tra", from_utf8=False, split_console=False) == "utf-8"


def test_get_dst_encoding_from_utf8_reverse():
    assert handle.get_dst_encoding("russian", "component.tra", from_utf8=True, split_console=False) == "cp1251"


# ---------------------------------------------------------------------------
# get_relpath / get_dirpath
# ---------------------------------------------------------------------------


def test_get_relpath():
    relpath = handle.get_relpath("/tra/russian/setup.tra", "/tra")
    assert relpath == os.path.join("russian", "setup.tra")


def test_get_dirpath():
    assert handle.get_dirpath(os.path.join("russian", "setup.tra")) == "russian"


def test_get_dirpath_top_level():
    assert handle.get_dirpath("setup.tra") == ""


# ---------------------------------------------------------------------------
# get_os_path
# ---------------------------------------------------------------------------


def test_get_os_path_win32():
    result = handle.get_os_path(os.path.join("russian", "setup.tra"), "win32")
    assert result == os.path.join("russian", "setup-win32.tra")


def test_get_os_path_unix():
    result = handle.get_os_path(os.path.join("english", "install.tra"), "unix")
    assert result == os.path.join("english", "install-unix.tra")


def test_get_os_path_osx():
    result = handle.get_os_path(os.path.join("french", "setup.tra"), "osx")
    assert result == os.path.join("french", "setup-osx.tra")


# ---------------------------------------------------------------------------
# find_files
# ---------------------------------------------------------------------------


def test_find_files_finds_tra(tmp_path):
    (tmp_path / "russian").mkdir()
    (tmp_path / "russian" / "setup.tra").write_text("@1 = ~hello~")
    (tmp_path / "russian" / "component.tra").write_text("@1 = ~world~")
    (tmp_path / "russian" / "readme.txt").write_text("ignore me")

    result = handle.find_files(str(tmp_path), "tra")
    assert len(result) == 2
    assert all(f.endswith(".tra") for f in result)


def test_find_files_sorted(tmp_path):
    (tmp_path / "b.tra").write_text("")
    (tmp_path / "a.tra").write_text("")
    result = handle.find_files(str(tmp_path), "tra")
    assert result == sorted(result)


def test_find_files_recursive(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "nested.tra").write_text("")
    (tmp_path / "top.tra").write_text("")
    result = handle.find_files(str(tmp_path), "tra")
    assert len(result) == 2


def test_find_files_case_insensitive_ext(tmp_path):
    (tmp_path / "file.TRA").write_text("")
    result = handle.find_files(str(tmp_path), "tra")
    assert len(result) == 1


def test_find_files_empty_dir(tmp_path):
    assert handle.find_files(str(tmp_path), "tra") == []


# ---------------------------------------------------------------------------
# resave_file
# ---------------------------------------------------------------------------


def test_resave_file_converts_encoding(tmp_path):
    src = tmp_path / "src" / "file.tra"
    src.parent.mkdir()
    src.write_text("@1 = ~Привет~", encoding="cp1251")

    dst = tmp_path / "out" / "file.tra"
    handle.resave_file(str(src), "cp1251", str(dst), "utf-8")

    content = dst.read_text(encoding="utf-8")
    assert "Привет" in content
    assert content.startswith("// Do not edit.")


def test_resave_file_creates_dst_dir(tmp_path):
    src = tmp_path / "file.tra"
    src.write_text("@1 = ~hello~", encoding="utf-8")
    dst = tmp_path / "deep" / "nested" / "file.tra"

    handle.resave_file(str(src), "utf-8", str(dst), "utf-8")

    assert dst.exists()


def test_resave_file_prepends_comment(tmp_path):
    src = tmp_path / "file.tra"
    src.write_text("@1 = ~hello~", encoding="utf-8")
    dst = tmp_path / "out.tra"

    handle.resave_file(str(src), "utf-8", str(dst), "utf-8")

    content = dst.read_text(encoding="utf-8")
    assert content.startswith(handle.COMMENT_NO_MANUAL)


def test_resave_file_dst_path_is_file_not_dir(tmp_path):
    """If dst path exists as a file (not dir), it should be overwritten cleanly."""
    src = tmp_path / "src.tra"
    src.write_text("new content", encoding="utf-8")
    dst = tmp_path / "dst.tra"
    dst.write_text("old content", encoding="utf-8")

    handle.resave_file(str(src), "utf-8", str(dst), "utf-8")

    assert "new content" in dst.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# main — integration
# ---------------------------------------------------------------------------


def test_main_basic_conversion(tmp_path, monkeypatch):
    tra_path = tmp_path / "tra"
    out_path = tmp_path / "out"
    (tra_path / "russian").mkdir(parents=True)
    (tra_path / "russian" / "component.tra").write_text("@1 = ~Привет~", encoding="cp1251")

    monkeypatch.setattr(
        sys,
        "argv",
        ["handle.py", "--tra-path", str(tra_path), "--out-path", str(out_path)],
    )
    handle.main()

    result = (out_path / "russian" / "component.tra").read_text(encoding="utf-8")
    assert "Привет" in result
    assert result.startswith("// Do not edit.")


def test_main_console_file_always_utf8(tmp_path, monkeypatch):
    tra_path = tmp_path / "tra"
    out_path = tmp_path / "out"
    (tra_path / "russian").mkdir(parents=True)
    (tra_path / "russian" / "setup.tra").write_text("@1 = ~Привет~", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        ["handle.py", "--tra-path", str(tra_path), "--out-path", str(out_path)],
    )
    handle.main()

    result = (out_path / "russian" / "setup.tra").read_text(encoding="utf-8")
    assert "Привет" in result


def test_main_split_console(tmp_path, monkeypatch):
    tra_path = tmp_path / "tra"
    out_path = tmp_path / "out"
    (tra_path / "russian").mkdir(parents=True)
    (tra_path / "russian" / "setup.tra").write_text("@1 = ~Привет~", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "handle.py",
            "--tra-path",
            str(tra_path),
            "--out-path",
            str(out_path),
            "--split-console",
        ],
    )
    handle.main()

    assert (out_path / "russian" / "setup-win32.tra").exists()
    assert (out_path / "russian" / "setup-unix.tra").exists()
    assert (out_path / "russian" / "setup-osx.tra").exists()

    win32 = (out_path / "russian" / "setup-win32.tra").read_text(encoding="cp866")
    assert "Привет" in win32
    unix = (out_path / "russian" / "setup-unix.tra").read_text(encoding="utf-8")
    assert "Привет" in unix


def test_main_from_utf8(tmp_path, monkeypatch):
    tra_path = tmp_path / "tra"
    out_path = tmp_path / "out"
    (tra_path / "russian").mkdir(parents=True)
    (tra_path / "russian" / "component.tra").write_text("@1 = ~Привет~", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "handle.py",
            "--tra-path",
            str(tra_path),
            "--out-path",
            str(out_path),
            "--from-utf8",
        ],
    )
    handle.main()

    result = (out_path / "russian" / "component.tra").read_text(encoding="cp1251")
    assert "Привет" in result
