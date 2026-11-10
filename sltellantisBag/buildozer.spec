[app]

title = Meu App StellantisaBag
package.name = stellantisabag
package.domain = org.stellantis

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,csv

version = 0.1

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
#android.permissions = INTERNET
# (int) Android NDK version to use
android.ndk = 25b
# (list) Permissions
android.permissions = INTERNET, CAMERA
requirements = python3,kivy,android,jnius


# (list) Application requirements
# comma separated e.g. requirements = kivy,python3,kivy_deps,jnius,android


# (str) Icon of the application
icon.filename = %(source.dir)s/icones/icone_mybag.png


buildozer appclean

p4a.branch = v2024.01.21

[buildozer]

log_level = 2
warn_on_root = 1
