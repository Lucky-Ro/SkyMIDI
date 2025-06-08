"""
MIDI 15 键
"""
import sys, time, mido, pydirectinput as pdi

# ---------- PyDirectInput 全局设置 ----------
pdi.FAILSAFE = False   # 不触发 failsafe
pdi.PAUSE   = 0        # 取消 0.1 s 默认延时

# ---------- 枚举 MIDI 端口 ----------
ports = mido.get_input_names()
if not ports:
    print("❌ 没发现 MIDI 输入端口，先检查连接。")
    sys.exit(1)

print("可用 MIDI 端口：")
for i, name in enumerate(ports):
    print(f" [{i}] {name}")
MIDI_PORT = ports[0]   # 如需手选改这里

# ---------- 15 键映射 ----------
note2key = {
    48:'y', 50:'u', 52:'i', 53:'o', 55:'p', 57:'h', 59:'j',
    60:'k',
    62:'l', 64:';', 65:'n', 67:'m', 69:',', 71:'.', 72:'/',
}

pressed = set()        # 已按下键集合

def key_down(k):
    if k not in pressed:
        pdi.keyDown(k, _pause=False)
        pressed.add(k)

def key_up(k):
    if k in pressed:
        pdi.keyUp(k, _pause=False)
        pressed.remove(k)

# ---------- rtmidi 回调 ----------
def on_midi(msg):
    if msg.type == 'note_on' and msg.velocity > 0:
        if (k := note2key.get(msg.note)):
            key_down(k)
    elif msg.type in ('note_off', 'note_on') and msg.velocity == 0:
        if (k := note2key.get(msg.note)):
            key_up(k)

mido.open_input(MIDI_PORT, callback=on_midi)
print(f"\n🎹 开始监听：{MIDI_PORT} 按键   Ctrl+C 退出")

# 主线程什么都不干，维持进程即可
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 退出")
