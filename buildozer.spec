[app]
title = ABAWERA INVESTOR
package.name = abawerainvestor
package.domain = com.abaweradevsinc
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,sqlite
source.include_patterns = assets/*,data/*
source.exclude_exts = spec
source.exclude_dirs = tests, bin, venv, .git
source.exclude_patterns = license,images/*/*.jpg

version = 1.0.0
requirements = python3,kivy==2.3.1,kivymd==1.1.1,requests,sqlalchemy,typing_extensions,certifi,urllib3,chardet,idna,pillow
orientation = portrait
fullscreen = 0
# android.presplash_color removed
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a
android.allow_backup = True
# android.apptheme removed for AGP compat
android.logcat_filters = *:S python:D kivy:D
android.debug = 1

[buildozer]
log_level = 2
warn_on_root = 1
