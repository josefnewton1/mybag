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
requirements = python3,kivy,android,jnius


# (list) Application requirements
# comma separated e.g. requirements = kivy,python3,kivy_deps,jnius,android


# (str) Icon of the application
icon.filename = %(source.dir)s/icones/icone_mybag.png

# (str) Presplash of the application (Tela de carregamento inicial)
presplash.filename = %(source.dir)s/icones/carregamento.1.gif

buildozer appclean

p4a.branch = v2024.01.21

[buildozer]

log_level = 2
warn_on_root = 1
