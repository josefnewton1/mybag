[app]

title = Meu App StellantisaBag
package.name = stellantisabag
package.domain = org.stellantis

source.dir = sltellantisBag
source.include_exts = py,png,jpg,kv,atlas,json,csv

version = 0.2

requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow,android

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icones/icone_mybag.png

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.permissions = INTERNET

p4a.branch = v2024.01.21

[buildozer]

log_level = 2
warn_on_root = 1
