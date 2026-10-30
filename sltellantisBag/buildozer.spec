[app]

title = Meu App StellantisaBag
package.name = stellantisabag
package.domain = org.stellantis

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,csv

version = 0.1


orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
#android.permissions = INTERNET

# (list) Permissions
android.permissions = INTERNET, CAMERA

# (list) Application requirements
# comma separated e.g. requirements = kivy,python3,kivy_deps,jnius,android
requirements = python3,kivy,pyjnius,android

# (int) Target Android API, should be as high as possible.
# android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

buildozer appclean
buildozer -v android debug

p4a.branch = v2024.01.21

[buildozer]

log_level = 2
warn_on_root = 1
