[app]
title           = MealPlanner
package.name    = mealplanner
package.domain  = org.mealplanner
source.dir      = .
source.include_exts = py,kv,png,jpg,atlas

version         = 1.0.0

# KivyMD installed from its exact PyPI-hosted sdist URL (not a plain "kivymd==1.2.0"
# pin) so buildozer's pip dependency-resolution pre-check doesn't try to fetch an
# "android" platform wheel for Kivy itself (which doesn't exist on PyPI) and fail
# for every kivymd version. Note: KivyMD's repo has no git tag for 1.2.0, so the
# GitHub archive URL 404s - the PyPI file URL is the reliable equivalent.
requirements = python3==3.11.0,hostpython3==3.11.0,kivy==2.3.0,https://files.pythonhosted.org/packages/20/81/0b1154f5e581d5910702d9fadb3217f56cb186f72c8b36de0271e7ff9b5c/kivymd-1.2.0.tar.gz,peewee,qrcode,pillow,pyzbar,requests,urllib3,certifi,chardet,idna,filetype,six
fullscreen      = 0

# buildozer's real default when this is unset is landscape (not portrait, despite
# what the spec template's comment suggests) - set explicitly to avoid that.
orientation     = portrait

# Minimum API 21 (Android 5.0), target API 33
android.minapi  = 21
android.api     = 33
# Bumped from 25b: newer p4a recipes (e.g. libthorvg) assume NDK 26.1+'s
# "lib/clang/..." layout, not the "lib64/clang/..." layout NDK 25b still uses -
# this matches RECOMMENDED_NDK_VERSION in p4a's develop branch.
android.ndk     = 28c

android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# python-for-android bootstrap
p4a.bootstrap   = sdl2

# Local override of the "kivy" recipe (see p4a-recipes/kivy/__init__.py) - relaxes
# an incompatible-function-pointer-types error in cgl_gl.c that NDK 28c's newer
# clang enforces strictly but Kivy 2.3.x's generated GL bindings don't satisfy.
p4a.local_recipes = p4a-recipes

# Pinned to a develop-branch commit that fixes a p4a bug where "pip install -U pip"
# inside the auto-created build venv can leave mixed files from two pip versions,
# causing ImportError (e.g. "cannot import name 'open_rich_spinner'") on rebuilds.
# Not yet in a tagged release (latest release is 2026.5.9, predates the fix).
p4a.branch      = develop
p4a.commit      = d2ee8c54d9d42375a95f18159e950a119671cf63

# Architectures
android.archs   = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1