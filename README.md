## Handle charsets

This is a static alternative for WeiDU `HANDLE_CHARSETS` function. Static means that rather than converting tra files at
install time on user machine, this action will generate and (optionally) commit them into mod repository. It has similar
options, but there are differences.

- [Action usage](#action-usage)
- [Options](#options)
- [Differences from HANDLE_CHARSETS](#differences-from-handle_charsets)
- [TP2 usage](#tp2-usage)
- [Gitattributes](docs/gitattributes.md)

### Action usage

```yaml
name: Handle charsets
on:
  push:
    paths:
      - "mymod/tra/**.tra"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Handle charsets
        uses: BGforgeNet/handle-charsets@master
        with:
          tra_path: mymod/tra
          out_path: mymod/tra_ee
          from_utf8: false
```

By default, the files will be pushed into the repository.

Alternatively, you can disable `commit` and only run the action during packaging. However, note that Project Infinity
requires repository source code to match package contents.

### Options

| name            | default | description                                                                                   |
| --------------- | ------- | --------------------------------------------------------------------------------------------- |
| `tra_path`      |         | Source tra directory, same as in `HANDLE_CHARSETS`.                                           |
| `out_path`      |         | Converted tra directory, same as in `HANDLE_CHARSETS`.                                        |
| `from_utf8`     | `false` | Assume that source files are in UTF-8, make reverse conversion, same as in `HANDLE_CHARSETS`. |
| `commit`        | `true`  | Commit and push the changes.                                                                  |
| `split_console` | `false` | Deprecated. Generate OS-specific files for console messages, see below.                       |

### Differences from HANDLE_CHARSETS

1. Less options. In particular, there's no (no)convert/(no)reload arrays. Use `WITH_TRA`/`LOAD_TRA`/`USING` to scope
   your tra files to corresponding components.
2. Any file named `ee.tra` or matching `*_ee.tra` mask is inferred to be in UTF-8, even if the rest of the files are in
   Windows-specific encoding.

#### Console encodings

Files named `setup.tra`, `install.tra` are designated as "console files", storing component names and other strings
printed to console window.

Latest WeiDU needs UTF-8 encoded files for console messages. Therefore, `setup.tra` and `install.tra` will be UTF-8
encoded, regardless of `from_utf8` setting. That is what you generally want to use.

If you use legacy WeiDU (built for WinXP and below), you'll need ANSI-encoded files. You can set `split_console` to
`true`. That will generate multiple OS-specific console message files with corresponding encoding. One `setup.tra` turns
into 3 files: `setup-win32.tra`, `setup-unix.tra`, `setup-osx.tra`. Same goes for `install.tra`.

### TP2 usage

Example TP2 usage, with values matching those of action usage example.

```
BACKUP ~mymod/backup~
SUPPORT ""
VERSION ~v1~
NO_IF_EVAL_BUG
AUTO_EVAL_STRINGS

ALWAYS
    CLEAR_EVERYTHING
    OUTER_SPRINT components ~%MOD_FOLDER%/components~

    /* If it's an EE game, use converted utf-8 translations from out_path. */
    ACTION_IF GAME_IS ~bgee bg2ee eet iwdee pstee~ BEGIN
        OUTER_SPRINT lang_dir ~%MOD_FOLDER%/tra_ee/%LANGUAGE%~
    END ELSE BEGIN
        /* Otherwise, use original ones from tra_path. */
        OUTER_SPRINT lang_dir ~%MOD_FOLDER%/tra/%LANGUAGE%~
    END
END


/*
    Only console messages are loaded by default.
    Doesn't matter whether to use setup.tra from "tra" or "tra_ee", they are the same, UTF-8.
*/
LANGUAGE ~English~ ~english~ ~%MOD_FOLDER%/tra/english/setup.tra~
LANGUAGE ~Russian~ ~russian~ ~%MOD_FOLDER%/tra/russian/setup.tra~
LANGUAGE ~Spanish~ ~spanish~ ~%MOD_FOLDER%/tra/spanish/setup.tra~


BEGIN @1 /* My Component */
OUTER_SPRINT comp_name ~component1~
/*
    This loads component translation from correct language directory.
    Once component is installed, WITH_TRA discards %comp_name%.tra translation scope.
*/
WITH_TRA ~%lang_dir%/%comp_name%.tra~ BEGIN INCLUDE ~%components%/%comp_name%/main.tpa~ END

```
