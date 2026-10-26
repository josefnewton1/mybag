[app]

# (str) Title of your application
title = Meu App StellantisaBag

# (str) Package name
package.name = stellantisabag

# (str) Package domain (needed for android packaging)
package.domain = org.stellantis

# (list) Source files to include (let empty to include all files)
source.include_exts = py,png,jpg,kv,atlas,json,csv

# (list) Application requirements
# comma separated e.g. requirements = python3,kivy
requirements = python3,kivy,kivyMD

# (str) Supported orientation (portrait, landscape, all)
orientation = portrait

# (list) Permissions
#android.permissions = INTERNET

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1