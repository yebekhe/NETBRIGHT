[app]

title = DPI Tunnel
package.name = dpitunnel
package.domain = org.yebekhe

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
icon.filename = icon.png

version = 0.1
requirements = python3, kivy==2.1.0, https://github.com/kivymd/KivyMD/archive/refs/heads/master.zip

orientation = portrait
fullscreen = 0

android.archs = armeabi-v7a

android.permissions = INTERNET

[buildozer]
log_level = 2
