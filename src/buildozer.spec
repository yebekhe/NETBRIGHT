[app]

title = DPI Tunnel
package.name = dpitunnel
package.domain = org.yebekhe

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
icon.filename = icon.png

version = 0.1
requirements = python3, kivy==master, requests, urllib3, charset_normalizer==2.1.1, idna, openssl, https://github.com/kivymd/KivyMD/archive/master.zip

orientation = portrait
fullscreen = 0
android.archs = armeabi-v7a

android.permissions = INTERNET

[buildozer]
log_level = 2
