rm -rf build dist

pyinstaller launcher.spec
pyinstaller app.spec

cd dist
tar cvfz AS-DynApp.tar.gz AS-DynApp.app