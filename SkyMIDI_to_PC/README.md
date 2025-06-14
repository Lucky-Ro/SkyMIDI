# SkyMIDI
这个程序连接了电钢琴和Sky光遇，可以实现在现实中弹奏Sky中的乐器

## 命令行版本已完善。安装依赖之后即可直接运行
首次运行的时候会要求用户输入自己期望的中央C键。程序将按照该中央C对应光遇中的第二排中间的‘Do’

## 也可以将命令行版本打包成可执行exe文件
### 建议重新创建一个Python虚拟环境，且不要用Anaconda！

### 命令行版本打包命令
pyinstaller -F SkyMIDI_CLI.py --clean --name SkyMIDI_CLI   --hidden-import=mido.backends.rtmidi

### GUI版本需要单独安装以下依赖
python -m pip install --upgrade --extra-index-url https://PySimpleGUI.net/install PySimpleGUI