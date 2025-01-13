import os
import PyInstaller.__main__


PyInstaller.__main__.run([
    "mosamatic/main.py",
    "--onefile",
    "--windowed",
    "--icon=assets/icon.ico",
    f"--add-data=assets{os.pathsep}assets",
    "--name=MyTkinterMVCApp"
])
