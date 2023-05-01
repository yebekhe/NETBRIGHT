[app]

title = DPI Tunnel
package.name = dpitunnel
package.domain = org.yebekhe

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
icon.filename = icon.png

version = 0.1
requirements = https://www.python.org/ftp/python/3.11.3/Python-3.11.3.tgz , kivy==master, requests, urllib3, charset_normalizer==2.1.1, idna, openssl, https://github.com/kivymd/KivyMD/archive/master.zip

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a

android.permissions = INTERNET

[buildozer]
log_level = 2
