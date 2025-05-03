[app]
version = 1.0.0
title = MyKivyApp
package.name = mykivyapp
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Put all your dependencies here
requirements = python3,kivy,kivymd,kivy_garden.matplotlib,matplotlib,pandas,requests

# This is needed for garden packages
garden_requirements = matplotlib

android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 0
