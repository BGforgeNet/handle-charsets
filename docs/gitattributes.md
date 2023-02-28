## Gitattributes

To allow Github to display tra files with non-UTF-8 encoding correctly, you need to specify their encoding explicitly in `.gitattributes` file.

It's optional and is not related to action in any way.

An example:

```gitattributes
# Classic
mymod/tra/czech/**.tra                  working-tree-encoding=cp1250
mymod/tra/french/**.tra                 working-tree-encoding=cp1252
mymod/tra/german/**.tra                 working-tree-encoding=cp1252
mymod/tra/hungarian/**.tra              working-tree-encoding=cp1250
mymod/tra/italian/**.tra                working-tree-encoding=cp1252
mymod/tra/korean/**.tra                 working-tree-encoding=cp949
mymod/tra/polish/**.tra                 working-tree-encoding=cp1250
mymod/tra/portuguese/**.tra             working-tree-encoding=cp1252
mymod/tra/russian/**.tra                working-tree-encoding=cp1251
mymod/tra/spanish/**.tra                working-tree-encoding=cp1252
mymod/tra/swedish/**.tra                working-tree-encoding=cp1252
mymod/tra/schinese/**.tra               working-tree-encoding=cp936
mymod/tra/tchinese/**.tra               working-tree-encoding=cp950
mymod/tra/ukrainian/**.tra              working-tree-encoding=cp1251

# Classic or EE console, RU/UA
mymod/**/russian/**/install.tra         working-tree-encoding=cp866
mymod/**/russian/**/setup.tra           working-tree-encoding=cp866
mymod/**/ukrainian/**/install.tra       working-tree-encoding=cp866
mymod/**/ukrainian/**/setup.tra         working-tree-encoding=cp866

# EE only
mymod/tra/**/ee.tra                     working-tree-encoding=utf8
mymod/tra/**/*_ee.tra                   working-tree-encoding=utf8

# Linux console
mymod/**/setup-unix.tra                 working-tree-encoding=utf8
mymod/**/setup-osx.tra                  working-tree-encoding=utf8

# Windows console, other languages
mymod/tra_ee/czech/*-win32.tra          working-tree-encoding=cp1250
mymod/tra_ee/french/*-win32.tra         working-tree-encoding=cp1252
mymod/tra_ee/german/*-win32.tra         working-tree-encoding=cp1252
mymod/tra_ee/hungarian/*-win32.tra      working-tree-encoding=cp1250
mymod/tra_ee/italian/*-win32.tra        working-tree-encoding=cp1252
mymod/tra_ee/korean/*-win32.tra         working-tree-encoding=cp949
mymod/tra_ee/polish/*-win32.tra         working-tree-encoding=cp1250
mymod/tra_ee/portuguese/*-win32.tra     working-tree-encoding=cp1252
mymod/tra_ee/russian/*-win32.tra        working-tree-encoding=cp866
mymod/tra_ee/spanish/*-win32.tra        working-tree-encoding=cp1252
mymod/tra_ee/swedish/*-win32.tra        working-tree-encoding=cp1252
mymod/tra_ee/schinese/*-win32.tra       working-tree-encoding=cp936
mymod/tra_ee/tchinese/*-win32.tra       working-tree-encoding=cp950
mymod/tra_ee/ukrainian/*-win32.tra      working-tree-encoding=cp866
```

After the file is created, tell git to re-read existing files:
```bash
git add --renormalize .
git commit -m "renormalize tras"
```
