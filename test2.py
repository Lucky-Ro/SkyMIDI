"""
MIDI 15 键 → 游戏键盘按键（零延时 + 首次中央C校准版）
"""
import sys, os, json, time, mido, pydirectinput as pdi

# ---------- PyDirectInput 设置 ----------
pdi.FAILSAFE = False
pdi.PAUSE   = 0            # 取消 0.1 s 延时

# ---------- 查找 MIDI 输入端口 ----------
ports = mido.get_input_names()
if not ports:
    print("❌ 没发现 MIDI 输入端口，请检查连接/驱动。")
    sys.exit(1)

print("可用 MIDI 端口：")
for i, name in enumerate(ports):
    print(f" [{i}] {name}")
MIDI_PORT = ports[0]       # 如需手选改这里

# ---------- 15 个键对应的字符 & 偏移 ----------
keys    = ['y','u','i','o','p','h','j','k','l',';','n','m',',','.','/']
offsets = [-12,-10,-8,-7,-5,-3,-1, 0, 2, 4, 5, 7, 9,11,12]  # 相对中心音符

CFG_FILE = 'midicenter.cfg'

def calibrate_center_note():
    print("\n🎹 请按下中央C...")
    with mido.open_input(MIDI_PORT) as port:
        for msg in port:
            if msg.type == 'note_on' and msg.velocity > 0:
                center = msg.note
                print(f"✅ 已记录中央C: {center}")
                with open(CFG_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'center': center}, f)
                return center

# ---------- 读取或校准中心音符 ----------
if os.path.exists(CFG_FILE):
    with open(CFG_FILE, 'r', encoding='utf-8') as f:
        center_note = json.load(f)['center']
    print(f"\n🎵 读取已保存中心音符: {center_note}")
else:
    center_note = calibrate_center_note()

# ---------- 生成映射表 ----------
note2key = {center_note + off: k for off, k in zip(offsets, keys)}
print("\n🎼 当前映射:")
for n, k in note2key.items():
    print(f"  MIDI {n:>3} → 键盘 '{k}'")

pressed = set()
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
print(f"\n 开始监听按键（端口: {MIDI_PORT}） Ctrl+C 退出")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 已退出")
