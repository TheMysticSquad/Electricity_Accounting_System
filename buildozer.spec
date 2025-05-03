# buildozer.spec
[app]

# (app name)
title = MyApp

# (app package)
package.name = myapp
package.domain = org.myapp

# (version number)
version = 1.0.0

# (source files)
source.include_exts = py,png,jpg,kv,atlas,ttf,otf

# (dependencies)
# Use requirements to specify all the packages your app needs
# You can specify Kivy or other Python libraries here
requirements = python3,kivy

# (orientation)
orientation = portrait

# (other settings you might need)
fullscreen = 1

# (Android settings)
android.api = 30
android.minapi = 21
android.target = 30

# (other optional settings for Android)
# android.permissions = INTERNET,ACCESS_NETWORK_STATE
