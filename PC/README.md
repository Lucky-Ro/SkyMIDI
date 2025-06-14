# midi-to-sky
这个仓库中的程序连接了电钢琴和Sky光遇，可以实现在现实中弹Sky中的乐器


### 命令行版本打包命令
pyinstaller -F SkyMIDI_CLI.py --clean --name SkyMIDI_CLI   --hidden-import=mido.backends.rtmidi

### GUI版本需要单独安装以下依赖
python -m pip install --upgrade --extra-index-url https://PySimpleGUI.net/install PySimpleGUI