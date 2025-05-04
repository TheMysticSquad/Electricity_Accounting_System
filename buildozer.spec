[app]

# (str) Title of your application
title = My Application  # Replace with your actual app title

# (str) Package name
package.name = myapp  # Replace with your desired package name (lowercase, no spaces)

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test  # Replace with your domain (reverse order)

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = kivy,python3==3.9  # Trying Python 3.9

# (str) Application versioning (method 1)
version = 0.1

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse or landscape-reverse
orientation = portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API, should be as high as possible.
android.api = 31  # Keeping a reasonable target API

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
android.ndk_api = 21  # Explicitly setting NDK API

# (str) Android NDK version to use
android.ndk = 25b  # Explicitly setting an older NDK version

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (list) Permissions
android.permissions = INTERNET  # Add necessary permissions

#
# buildozer specific
#

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
