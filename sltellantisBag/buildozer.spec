[app]

title = Meu App StellantisaBag
package.name = stellantisabag
package.domain = org.stellantis

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,csv

version = 0.1

requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a.
android.accept_sdk_license = True
#android.permissions = INTERNET

[buildozer]

log_level = 2
warn_on_root = 1
