## Handle charsets

This is a static alternative for WeiDU `HANDLE_CHARSETS` function. Static means that rather than converting tra files at install time on user machine, this action will generate and commit them into mod repository. It has similar options, but there are differences.

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
        uses: actions/checkout@v3

      - name: Handle charsets
        uses: BGforgeNet/handle-charsets@master
        with:
          tra_path: mymod/tra
          out_path: mymod/tra_ee
          from_utf8: false
          split_console: true
          commit: true
```

#### Options

| name            | default | description                                                                                   |
| --------------- | ------- | --------------------------------------------------------------------------------------------- |
| `tra_path`      |         | Source tra directory, same as in `HANDLE_CHARSETS`.                                           |
| `out_path`      |         | Converted tra directory, same as in `HANDLE_CHARSETS`.                                        |
| `from_utf8`     | `false` | Assume that source files are in UTF-8, make reverse conversion, same as in `HANDLE_CHARSETS`. |
| `split_console` | `false` | Generate OS-specific files for console messages, see below.                                   |
| `commit`        | `true`  | Commit and push the changes.                                                                  |

#### Differences from `HANDLE_CHARSETS`

1. Less options. In particular, there's no noconvert/noreload arrays. Use `WITH_TRA`/`LOAD_TRA`/`USING` to scope your tra files to corresponding components.
2. Any file named `ee.tra` or matching `*_ee.tra` mask is inferred to be in UTF-8, even if the rest of the files are in Windows-specific encoding.
3. Files named `setup.tra` or `install.tra` are inferred to be in Windows-specific encoding, even the rest of the files are in UTF-8.
4. Files named `setup.tra` or `install.tra` in Russian or Ukrainian languages are inferred to be in `cp866` encoding, not `cp1251`. That's the correct console encoding in Windows in those languages.
5. In Linux and Mac OS, usual console encoding is UTF-8. `split_console` allows you to generate multiple OS-specific console message files with correct encoding. One `setup.tra` turns into 3 files: `setup-win32.tra`, `setup-unix.tra`, `setup-osx.tra`. Same goes for `install.tra`.

#### TP2 usage

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
    ACTION_IF GAME_IS ~bgee, bg2ee, eet, iwdee, pstee~ BEGIN
        OUTER_SPRINT lang_dir ~%MOD_FOLDER%/tra_ee~
    END ELSE BEGIN
        /* Otherwise, use original ones from tra_path. */
        OUTER_SPRINT lang_dir ~%MOD_FOLDER%/tra~
    END
END


/*
    Only console messages are loaded by default.
    We use setup-%WEIDU_OS%.tra from out_path, because has correct console encoding.
*/
LANGUAGE ~English~ ~english~ ~%MOD_FOLDER%/tra_ee/english/setup-%WEIDU_OS%.tra~
LANGUAGE ~Russian~ ~russian~ ~%MOD_FOLDER%/tra_ee/russian/setup-%WEIDU_OS%.tra~
LANGUAGE ~Spanish~ ~spanish~ ~%MOD_FOLDER%/tra_ee/spanish/setup-%WEIDU_OS%.tra~


BEGIN @1 /* My Component */
OUTER_SPRINT comp_name ~component1~
/*
    This loads component translation from correct language directory.
    Once component is installed, WITH_TRA discards %comp_name%.tra translation scope.
*/
WITH_TRA ~%lang_dir%/%comp_name%.tra~ BEGIN INCLUDE ~%components%/%comp_name%/main.tpa~ END

```

### Gitattributes

For pretty diffs, set correct [gitattributes](docs/gitattributes.md).
