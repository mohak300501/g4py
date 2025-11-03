import PyInstaller.__main__

pyinstaller_args = [
    '--onefile',  'g4dl.py'
]

PyInstaller.__main__.run(pyinstaller_args)