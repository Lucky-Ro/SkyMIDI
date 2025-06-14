import sys, time, json, threading
import mido, pydirectinput as pdi
import PySimpleGUI as sg

pdi.FAILSAFE = False
pdi.PAUSE = 0

# ---------- 15 键固定布局 ----------
keys    = ['y','u','i','o','p','h','j','k','l',';','n','m',',','.','/']
offsets = [-12,-10,-8,-7,-5,-3,-1,0,2,4,5,7,9,11,12]

CFG = 'midicenter.cfg'
center_note = None           # 运行时动态填

pressed = set()
def key_down(k):
    if k not in pressed:
        pdi.keyDown(k, _pause=False)
        pressed.add(k)
def key_up(k):
    if k in pressed:
        pdi.keyUp(k, _pause=False)
        pressed.remove(k)

running = False              # 全局开关
def midi_thread(port_name):
    with mido.open_input(port_name, callback=on_midi):
        while running: time.sleep(0.01)

def on_midi(msg):
    if not running: return
    if center_note is None: return
    if msg.type == 'note_on' and msg.velocity > 0:
        if (k := note_map.get(msg.note)): key_down(k)
    elif msg.type in ('note_off', 'note_on') and msg.velocity == 0:
        if (k := note_map.get(msg.note)): key_up(k)

# ---------- GUI ----------
sg.theme('DarkBlue3')
layout = [
    [sg.Text('MIDI 端口'), sg.Combo(mido.get_input_names(), key='PORT', size=(40,1))],
    [sg.Button('校准中央 C', key='CAL'), sg.Button('开始映射', key='START_STOP'),
     sg.Text('', size=(20,1), key='STATUS')],
    [sg.Multiline('', size=(52,8), autoscroll=True, key='LOG')]
]
window = sg.Window('Midi ➜ Keyboard Mapper', layout, finalize=True)

def log(s): window['LOG'].print(s)

note_map = {}
thread = None

while True:
    event, values = window.read(timeout=100)
    if event in (sg.WIN_CLOSED, 'Exit'):
        running = False
        break

    if event == 'CAL':
        port = values['PORT']
        if not port:
            sg.popup_error('请选择 MIDI 端口后再校准')
            continue
        log('请按下中央 C...')
        # 在临时端口阻塞等待一次 note_on
        with mido.open_input(port) as tmp:
            for msg in tmp:
                if msg.type=='note_on' and msg.velocity>0:
                    center_note = msg.note
                    json.dump({'center':center_note}, open(CFG,'w'))
                    log(f'已记录中心音符 {center_note}')
                    window['STATUS'].update(f'中心={center_note}')
                    break

        # 生成映射
        note_map = {center_note+o:k for o,k in zip(offsets,keys)}
        log('映射表生成完毕')

    if event == 'START_STOP':
        if running:
            running=False
            window['START_STOP'].update('开始映射')
            window['STATUS'].update('已停止')
            log('*** 映射已停止 ***')
        else:
            port = values['PORT']
            if not port:
                sg.popup_error('请先选择 MIDI 端口')
                continue
            if center_note is None:
                sg.popup_error('还未校准中央 C')
                continue
            running=True
            window['START_STOP'].update('停止映射')
            window['STATUS'].update('运行中')
            log('*** 开始监听 ***')
            thread = threading.Thread(target=midi_thread, args=(port,), daemon=True)
            thread.start()

window.close()
