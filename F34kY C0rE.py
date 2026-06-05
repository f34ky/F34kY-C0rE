import tkinter as tk
from tkinter import colorchooser, messagebox, simpledialog
import keyboard
import threading
import time
import pyautogui
import json
import os
import sys
import datetime
import subprocess
import re

# ===== GLOBAL VARIABLES =====

menu_visible = False
menu_animation_id = None
drag_data = {"x": 0, "y": 0}

CONFIG_FILE = "F34kY_Core.json"

settings = {
    'accent': '#e94560', 'bg': '#0a0a0f', 'card': '#14141f', 'text': '#eeeeee',
    'font_family': 'Segoe UI', 'font_size': 9, 'menu_key': '\\'
}

exp = {'bhop': False, 'clicker': False, 'presser': False, 'macro': False, 'crosshair': False, 'fps': False,
       'ping': False}

# ===== BUNNY HOP =====
bhop_enabled = False
bhop_toggle = False
bhop_alt_pressed_time = 0
bhop_debounce_time = 0.2
bhop_window = None
bhop_status_label = None
bhop_thread_running = False
TICK_64_MS = 0.0156


def send_space(duration):
    keyboard.send("space")
    time.sleep(duration)


def bhop_key_check():
    global bhop_toggle, bhop_alt_pressed_time
    while bhop_enabled and bhop_thread_running:
        try:
            if keyboard.is_pressed('alt'):
                current_time = time.time()
                if current_time - bhop_alt_pressed_time > bhop_debounce_time:
                    bhop_toggle = not bhop_toggle
                    bhop_alt_pressed_time = current_time
                    if bhop_window and bhop_window.winfo_exists():
                        if bhop_toggle:
                            bhop_status_label.config(text="ENABLED", fg="#44ff44")
                        else:
                            bhop_status_label.config(text="DISABLED", fg="#ff4444")

            if bhop_toggle and keyboard.is_pressed('space') and bhop_enabled:
                send_space(TICK_64_MS * 1)
                while bhop_toggle and keyboard.is_pressed('space') and bhop_enabled:
                    send_space(TICK_64_MS * 2)
                    if keyboard.is_pressed('alt'):
                        current_time = time.time()
                        if current_time - bhop_alt_pressed_time > bhop_debounce_time:
                            bhop_toggle = not bhop_toggle
                            bhop_alt_pressed_time = current_time
                            if bhop_window and bhop_window.winfo_exists():
                                if bhop_toggle:
                                    bhop_status_label.config(text="ENABLED", fg="#44ff44")
                                else:
                                    bhop_status_label.config(text="DISABLED", fg="#ff4444")
                            break

            time.sleep(0.001)
        except:
            break


def create_bhop_window():
    global bhop_window, bhop_status_label
    if bhop_window and bhop_window.winfo_exists():
        bhop_window.destroy()

    bhop_window = tk.Toplevel(root)
    bhop_window.title("")
    bhop_window.geometry("200x100")
    bhop_window.configure(bg=settings['bg'])
    bhop_window.attributes('-topmost', True)
    bhop_window.overrideredirect(True)

    screen_width = bhop_window.winfo_screenwidth()
    bhop_window.geometry(f"200x100+{screen_width - 210}+10")

    main_frame = tk.Frame(bhop_window, bg=settings['bg'], relief='solid', bd=1)
    main_frame.pack(expand=True, fill='both', padx=2, pady=2)

    bhop_status_label = tk.Label(main_frame, text="DISABLED", font=('Arial', 14, 'bold'),
                                 fg='#ff4444', bg=settings['bg'])
    bhop_status_label.pack(expand=True, pady=(10, 5))

    info_label = tk.Label(main_frame, text="ALT - toggle\nEND - exit", font=('Arial', 8),
                          fg=settings['text'], bg=settings['bg'], justify='center')
    info_label.pack(pady=(0, 5))

    def start_move(event):
        bhop_window.x = event.x
        bhop_window.y = event.y

    def stop_move(event):
        bhop_window.x = None
        bhop_window.y = None

    def do_move(event):
        if bhop_window.x is not None:
            deltax = event.x - bhop_window.x
            deltay = event.y - bhop_window.y
            x = bhop_window.winfo_x() + deltax
            y = bhop_window.winfo_y() + deltay
            bhop_window.geometry(f"+{x}+{y}")

    bhop_window.bind('<Button-1>', start_move)
    bhop_window.bind('<ButtonRelease-1>', stop_move)
    bhop_window.bind('<B1-Motion>', do_move)


def toggle_bhop():
    global bhop_enabled, bhop_window, bhop_thread_running
    bhop_enabled = not bhop_enabled
    if bhop_enabled:
        create_bhop_window()
        bh_enable_btn.config(text="✅ ENABLED", bg=settings['accent'])
        bhop_thread_running = True
        threading.Thread(target=bhop_key_check, daemon=True).start()
    else:
        bhop_toggle = False
        bhop_thread_running = False
        if bhop_window and bhop_window.winfo_exists():
            bhop_window.destroy()
            bhop_window = None
        bh_enable_btn.config(text="▶️ DISABLED", bg=settings['card'])


# ===== AUTO CLICKER =====
clicker_enabled = False
clicker_active = False
clicker_key = 'x'
clicker_cps = 20
clicker_count = 0
clicker_window = None
clicker_status_label = None
clicker_count_label = None
clicker_thread_running = False


def clicker_loop():
    while clicker_enabled and clicker_thread_running:
        if clicker_active:
            pyautogui.click()
            clicker_count += 1
            if clicker_count_label:
                clicker_count_label.config(text=f"{clicker_count}")
            if clicker_window and clicker_window.winfo_exists():
                clicker_status_label.config(text=f"🔴 {clicker_count} clicks")
            time.sleep(1.0 / clicker_cps)
        time.sleep(0.01)


def toggle_clicker_auto():
    global clicker_active
    if clicker_enabled:
        clicker_active = not clicker_active
        if clicker_active:
            if clicker_window and clicker_window.winfo_exists():
                clicker_status_label.config(text="🔴 CLICKING...", fg="#4ecdc4")
        else:
            if clicker_window and clicker_window.winfo_exists():
                clicker_status_label.config(text="🟢 STOP", fg="#ffd93d")


def toggle_clicker():
    global clicker_enabled, clicker_window, clicker_status_label, clicker_count_label, clicker_thread_running, clicker_count
    clicker_enabled = not clicker_enabled
    if clicker_enabled:
        clicker_count = 0
        clicker_window, clicker_status_label = create_status_window("AUTO CLICKER", "🟢 STOP (press X)")
        info_frame = tk.Frame(clicker_window, bg=settings['accent'])
        info_frame.pack()
        clicker_count_label = tk.Label(info_frame, text="0", font=('Arial', 8), fg="#ffd93d", bg=settings['accent'])
        clicker_count_label.pack()
        cl_enable_btn.config(text="✅ ENABLED", bg=settings['accent'])
        clicker_thread_running = True
        threading.Thread(target=clicker_loop, daemon=True).start()
        keyboard.on_press_key(clicker_key, lambda e: toggle_clicker_auto())
    else:
        clicker_active = False
        clicker_thread_running = False
        if clicker_window and clicker_window.winfo_exists():
            clicker_window.destroy()
            clicker_window = None
        cl_enable_btn.config(text="▶️ DISABLED", bg=settings['card'])


def set_clicker_cps(val):
    global clicker_cps
    clicker_cps = int(float(val))
    cl_cps_label.config(text=f"{clicker_cps} CPS")


def reset_clicker_count():
    global clicker_count
    clicker_count = 0
    if clicker_count_label:
        clicker_count_label.config(text="0")


# ===== KEY PRESSER =====
presser_enabled = False
presser_active = False
presser_key = 'e'
presser_delay = 0.5
presser_window = None
presser_status_label = None
presser_thread_running = False


def presser_loop():
    while presser_enabled and presser_thread_running:
        if presser_active:
            keyboard.press(presser_key)
            time.sleep(0.05)
            keyboard.release(presser_key)
            time.sleep(presser_delay)
        time.sleep(0.01)


def toggle_presser_auto():
    global presser_active
    if presser_enabled:
        presser_active = not presser_active
        if presser_active:
            if presser_window and presser_window.winfo_exists():
                presser_status_label.config(text=f"🔴 PRESSING {presser_key.upper()}", fg="#4ecdc4")
        else:
            if presser_window and presser_window.winfo_exists():
                presser_status_label.config(text="🟢 STOP", fg="#ffd93d")


def toggle_presser():
    global presser_enabled, presser_window, presser_status_label, presser_thread_running
    presser_enabled = not presser_enabled
    if presser_enabled:
        presser_window, presser_status_label = create_status_window("KEY PRESSER",
                                                                    f"🟢 STOP (press {presser_key.upper()})")
        pr_enable_btn.config(text="✅ ENABLED", bg=settings['accent'])
        presser_thread_running = True
        threading.Thread(target=presser_loop, daemon=True).start()
        keyboard.on_press_key(presser_key, lambda e: toggle_presser_auto())
    else:
        presser_active = False
        presser_thread_running = False
        if presser_window and presser_window.winfo_exists():
            presser_window.destroy()
            presser_window = None
        pr_enable_btn.config(text="▶️ DISABLED", bg=settings['card'])


def set_presser_delay(val):
    global presser_delay
    presser_delay = float(val)
    pr_delay_label.config(text=f"{presser_delay:.1f}s")


# ===== MACRO =====
macro_recording = False
macro_steps = []
macro_playing = False
macro_rec_key = 'r'
macro_play_key = 't'
macro_window = None
macro_status_label = None
macro_rec_btn = None
macro_play_btn = None
macro_status = None


def start_rec():
    global macro_recording, macro_steps
    macro_steps = []
    macro_recording = True
    macro_status.config(text="🔴 RECORDING...", fg="#ff4444")
    macro_rec_btn.config(text="⏹️ STOP", bg="#ff4444")
    if macro_window and macro_window.winfo_exists():
        macro_status_label.config(text="🔴 RECORDING...", fg="#ff4444")

    def record_clicks():
        while macro_recording:
            if keyboard.is_pressed('enter'):
                pos = pyautogui.position()
                macro_steps.append({'x': pos.x, 'y': pos.y})
                count = len(macro_steps)
                macro_status.config(text=f"🔴 {count} clicks", fg="#ff4444")
                if macro_window and macro_window.winfo_exists():
                    macro_status_label.config(text=f"🔴 {count} clicks", fg="#ff4444")
                time.sleep(0.3)
            time.sleep(0.05)

    threading.Thread(target=record_clicks, daemon=True).start()


def stop_rec():
    global macro_recording
    macro_recording = False
    count = len(macro_steps)
    macro_status.config(text=f"✅ {count} ACTIONS", fg="#4ecdc4")
    macro_rec_btn.config(text="▶️ RECORD", bg=settings['card'])
    if macro_window and macro_window.winfo_exists():
        macro_status_label.config(text=f"✅ {count} actions", fg="#4ecdc4")


def play_macro():
    global macro_playing
    if macro_playing:
        macro_playing = False
        macro_status.config(text="⏸️ STOP", fg="#ffd93d")
        if macro_window and macro_window.winfo_exists():
            macro_status_label.config(text="⏸️ STOP", fg="#ffd93d")
        return
    if not macro_steps:
        macro_status.config(text="❌ NO RECORDING", fg="#ff4444")
        return
    macro_playing = True
    macro_status.config(text="▶️ PLAYING...", fg="#4ecdc4")
    if macro_window and macro_window.winfo_exists():
        macro_status_label.config(text="▶️ PLAYING...", fg="#4ecdc4")

    def play():
        for step in macro_steps:
            if not macro_playing:
                break
            pyautogui.click(step['x'], step['y'])
            time.sleep(0.1)
        macro_playing = False
        macro_status.config(text="✅ READY", fg="#888")
        if macro_window and macro_window.winfo_exists():
            macro_status_label.config(text="✅ READY", fg="#888")

    threading.Thread(target=play, daemon=True).start()


def toggle_macro_window():
    global macro_window, macro_status_label
    if macro_window and macro_window.winfo_exists():
        macro_window.destroy()
        macro_window = None
    else:
        macro_window, macro_status_label = create_status_window("MACRO", "⚪ READY")
        macro_status_label.config(text="⚪ READY", fg="#888")


def on_record(e):
    if macro_recording:
        stop_rec()
    else:
        start_rec()


def on_play(e):
    play_macro()


# ===== CS:GO CROSSHAIR =====
crosshair_obj = None
crosshair_enabled = False


class Crosshair:
    def __init__(self):
        self.root = tk.Toplevel()
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+0+0")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', 'black')
        self.canvas = tk.Canvas(self.root, width=w, height=h, bg='black', highlightthickness=0)
        self.canvas.pack()
        self.draw()
        self.create_status()

    def create_status(self):
        self.status = tk.Toplevel()
        self.status.geometry("180x100")
        self.status.attributes('-topmost', True)
        self.status.overrideredirect(True)
        w = self.status.winfo_screenwidth()
        self.status.geometry(f"180x100+{w // 2 - 90}+10")
        self.status.configure(bg=settings['bg'])
        f = tk.Frame(self.status, bg=settings['bg'], relief='solid', bd=1)
        f.pack(expand=True, fill='both', padx=2, pady=2)
        tk.Label(f, text="🎯 CS:GO CROSSHAIR", font=('Arial', 9, 'bold'), fg=settings['accent'], bg=settings['bg']).pack(
            pady=(5, 0))
        self.status_label = tk.Label(f, text="ACTIVE", font=('Arial', 10, 'bold'), fg='#44ff44', bg=settings['bg'])
        self.status_label.pack(expand=True)
        self.setup_drag()

    def setup_drag(self):
        def start(e): self.status.x = e.x; self.status.y = e.y

        def stop(e): self.status.x = None; self.status.y = None

        def move(e):
            if hasattr(self.status, 'x') and self.status.x is not None:
                x = self.status.winfo_x() + (e.x - self.status.x)
                y = self.status.winfo_y() + (e.y - self.status.y)
                self.status.geometry(f"+{x}+{y}")

        self.status.bind('<Button-1>', start)
        self.status.bind('<ButtonRelease-1>', stop)
        self.status.bind('<B1-Motion>', move)

    def draw(self):
        self.canvas.delete("all")
        cx = self.root.winfo_screenwidth() // 2
        cy = self.root.winfo_screenheight() // 2
        self.canvas.create_line(cx, cy - 20, cx, cy - 5, fill='#00ff00', width=3)
        self.canvas.create_line(cx, cy + 20, cx, cy + 5, fill='#00ff00', width=3)
        self.canvas.create_line(cx - 20, cy, cx - 5, cy, fill='#00ff00', width=3)
        self.canvas.create_line(cx + 20, cy, cx + 5, cy, fill='#00ff00', width=3)
        self.canvas.create_oval(cx - 2, cy - 2, cx + 2, cy + 2, fill='#00ff00')

    def stop(self):
        if self.status:
            self.status.destroy()
        if self.root:
            self.root.destroy()


def toggle_crosshair():
    global crosshair_obj, crosshair_enabled
    crosshair_enabled = not crosshair_enabled
    if crosshair_enabled:
        crosshair_obj = Crosshair()
        crosshair_enable_btn.config(text="✅ ENABLED", bg=settings['accent'])
        crosshair_status_label.config(text="✅ Active", fg='#4ecdc4')
    else:
        if crosshair_obj:
            crosshair_obj.stop()
            crosshair_obj = None
        crosshair_enable_btn.config(text="▶️ DISABLED", bg=settings['card'])
        crosshair_status_label.config(text="⚫ Inactive", fg='#888888')


# ===== FPS COUNTER =====
fps_obj = None
fps_enabled = False


class FPSCounter:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.geometry("150x80")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        self.root.geometry(f"150x80+{w - 160}+{h - 90}")
        self.root.overrideredirect(True)
        self.root.configure(bg=settings['bg'])
        f = tk.Frame(self.root, bg=settings['bg'], relief='solid', bd=2)
        f.pack(expand=True, fill='both', padx=2, pady=2)
        tk.Label(f, text="FPS", font=('Arial', 9, 'bold'), fg=settings['accent'], bg=settings['bg']).pack(pady=(5, 0))
        self.label = tk.Label(f, text="0", font=('Arial', 22, 'bold'), fg='#88ff88', bg=settings['bg'])
        self.label.pack(expand=True)
        self.frames = 0
        self.last_time = time.time()
        self.running = True
        self.update()
        self.setup_drag()

    def setup_drag(self):
        def start(e): self.x = e.x; self.y = e.y

        def stop(e): self.x = None; self.y = None

        def move(e):
            if hasattr(self, 'x') and self.x is not None:
                x = self.root.winfo_x() + (e.x - self.x)
                y = self.root.winfo_y() + (e.y - self.y)
                self.root.geometry(f"+{x}+{y}")

        self.root.bind('<Button-1>', start)
        self.root.bind('<ButtonRelease-1>', stop)
        self.root.bind('<B1-Motion>', move)

    def update(self):
        if self.running:
            self.frames += 1
            if time.time() - self.last_time >= 1:
                fps = self.frames
                self.frames = 0
                self.last_time = time.time()
                color = '#88ff88' if fps >= 60 else '#ffff88' if fps >= 30 else '#ff8888'
                self.label.config(text=str(fps), fg=color)
            self.root.after(50, self.update)

    def stop(self):
        self.running = False
        if self.root:
            self.root.destroy()


def toggle_fps():
    global fps_obj, fps_enabled
    fps_enabled = not fps_enabled
    if fps_enabled:
        fps_obj = FPSCounter()
        fps_enable_btn.config(text="✅ ENABLED", bg=settings['accent'])
        fps_status_label.config(text="✅ Active", fg='#4ecdc4')
    else:
        if fps_obj:
            fps_obj.stop()
            fps_obj = None
        fps_enable_btn.config(text="▶️ DISABLED", bg=settings['card'])
        fps_status_label.config(text="⚫ Inactive", fg='#888888')


# ===== PING COUNTER =====
ping_obj = None
ping_enabled = False


def get_ping():
    try:
        result = subprocess.run(["ping", "-n", "1", "8.8.8.8"], capture_output=True, text=True, timeout=5)
        match = re.search(r"time[=<](\d+)ms", result.stdout.lower())
        return int(match.group(1)) if match else 999
    except:
        return 999


class PingCounter:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.geometry("150x80")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        self.root.geometry(f"150x80+10+{h - 90}")
        self.root.overrideredirect(True)
        self.root.configure(bg=settings['bg'])
        f = tk.Frame(self.root, bg=settings['bg'], relief='solid', bd=2)
        f.pack(expand=True, fill='both', padx=2, pady=2)
        tk.Label(f, text="PING", font=('Arial', 9, 'bold'), fg=settings['accent'], bg=settings['bg']).pack(pady=(5, 0))
        self.label = tk.Label(f, text="0ms", font=('Arial', 20, 'bold'), fg='#88ff88', bg=settings['bg'])
        self.label.pack(expand=True)
        self.running = True
        self.update()
        self.setup_drag()

    def setup_drag(self):
        def start(e): self.x = e.x; self.y = e.y

        def stop(e): self.x = None; self.y = None

        def move(e):
            if hasattr(self, 'x') and self.x is not None:
                x = self.root.winfo_x() + (e.x - self.x)
                y = self.root.winfo_y() + (e.y - self.y)
                self.root.geometry(f"+{x}+{y}")

        self.root.bind('<Button-1>', start)
        self.root.bind('<ButtonRelease-1>', stop)
        self.root.bind('<B1-Motion>', move)

    def update(self):
        if self.running:
            ping = get_ping()
            color = '#88ff88' if ping < 60 else '#ffff88' if ping < 120 else '#ff8888'
            self.label.config(text=f"{ping}ms", fg=color)
            self.root.after(2000, self.update)

    def stop(self):
        self.running = False
        if self.root:
            self.root.destroy()


def toggle_ping():
    global ping_obj, ping_enabled
    ping_enabled = not ping_enabled
    if ping_enabled:
        ping_obj = PingCounter()
        ping_enable_btn.config(text="✅ ENABLED", bg=settings['accent'])
        ping_status_label.config(text="✅ Active", fg='#4ecdc4')
    else:
        if ping_obj:
            ping_obj.stop()
            ping_obj = None
        ping_enable_btn.config(text="▶️ DISABLED", bg=settings['card'])
        ping_status_label.config(text="⚫ Inactive", fg='#888888')


# ===== COMMON FUNCTIONS =====

def create_status_window(title, status_var):
    win = tk.Toplevel(root)
    win.geometry("200x80")
    win.configure(bg=settings['accent'])
    win.attributes('-topmost', True)
    win.overrideredirect(True)
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    win.geometry(f"200x80+{screen_width - 210}+{screen_height - 100}")
    tk.Label(win, text=title, font=(settings['font_family'], 10, "bold"),
             fg="white", bg=settings['accent']).pack(pady=5)
    status_label = tk.Label(win, text=status_var, font=(settings['font_family'], 9),
                            fg="white", bg=settings['accent'])
    status_label.pack(pady=5)
    return win, status_label


def save_config():
    data = {
        'accent': settings['accent'], 'bg': settings['bg'], 'card': settings['card'],
        'font_family': settings['font_family'], 'font_size': settings['font_size'],
        'menu_key': settings['menu_key'],
        'clicker': {'key': clicker_key, 'cps': clicker_cps},
        'presser': {'key': presser_key, 'delay': presser_delay}
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)


def load_config():
    global settings, clicker_key, clicker_cps, presser_key, presser_delay
    if not os.path.exists(CONFIG_FILE):
        save_config()
        return
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
        settings['accent'] = data.get('accent', '#e94560')
        settings['bg'] = data.get('bg', '#0a0a0f')
        settings['card'] = data.get('card', '#14141f')
        settings['font_family'] = data.get('font_family', 'Segoe UI')
        settings['font_size'] = data.get('font_size', 9)
        settings['menu_key'] = data.get('menu_key', '\\')
        clicker_key = data.get('clicker', {}).get('key', 'x')
        clicker_cps = data.get('clicker', {}).get('cps', 20)
        presser_key = data.get('presser', {}).get('key', 'e')
        presser_delay = data.get('presser', {}).get('delay', 0.5)
        apply_style()
        update_keys()
        setup_hotkeys()
    except:
        pass


def apply_style():
    root.configure(bg=settings['bg'])
    header.configure(bg=settings['accent'])
    title.configure(bg=settings['accent'], font=(settings['font_family'], 11, "bold"))
    status_bar.configure(bg=settings['accent'], font=(settings['font_family'], 8))


def update_keys():
    try:
        cl_key_label.config(text=f"{clicker_key.upper()}")
        pr_key_label.config(text=f"{presser_key.upper()}")
    except:
        pass


def setup_hotkeys():
    try:
        keyboard.unhook_all()
        keyboard.add_hotkey(settings['menu_key'], toggle_menu)
        keyboard.on_press_key(macro_rec_key, on_record)
        keyboard.on_press_key(macro_play_key, on_play)
    except:
        pass


def start_move(event):
    drag_data["x"] = event.x
    drag_data["y"] = event.y


def do_move(event):
    x = root.winfo_x() + (event.x - drag_data["x"])
    y = root.winfo_y() + (event.y - drag_data["y"])
    root.geometry(f"+{x}+{y}")


def animate_menu_open():
    global menu_animation_id
    current_x = root.winfo_x()
    target_x = 50
    if current_x < target_x:
        new_x = min(current_x + 30, target_x)
        root.geometry(f"340x700+{new_x}+100")
        menu_animation_id = root.after(8, animate_menu_open)
    else:
        menu_animation_id = None


def animate_menu_close():
    global menu_animation_id, menu_visible
    current_x = root.winfo_x()
    target_x = -340
    if current_x > target_x:
        new_x = max(current_x - 30, target_x)
        root.geometry(f"340x700+{new_x}+100")
        menu_animation_id = root.after(8, animate_menu_close)
    else:
        menu_visible = False
        root.withdraw()
        menu_animation_id = None


def toggle_menu():
    global menu_visible, menu_animation_id
    if menu_animation_id:
        root.after_cancel(menu_animation_id)
    if not menu_visible:
        menu_visible = True
        root.deiconify()
        animate_menu_open()
    else:
        animate_menu_close()


def toggle_expand(func_name, content_frame, btn):
    exp[func_name] = not exp[func_name]
    if exp[func_name]:
        content_frame.pack(fill=tk.X, padx=8, pady=(0, 6))
        btn.config(text=f"▼ {btn.original_text}")
    else:
        content_frame.pack_forget()
        btn.config(text=f"▶ {btn.original_text}")


def shutdown_program():
    global bhop_enabled, clicker_enabled, presser_enabled
    if messagebox.askyesno("Exit", "Close F34kY Core?"):
        bhop_enabled = False
        clicker_enabled = False
        presser_enabled = False
        if bhop_window and bhop_window.winfo_exists():
            bhop_window.destroy()
        if clicker_window and clicker_window.winfo_exists():
            clicker_window.destroy()
        if presser_window and presser_window.winfo_exists():
            presser_window.destroy()
        if macro_window and macro_window.winfo_exists():
            macro_window.destroy()
        if crosshair_obj:
            crosshair_obj.stop()
        if fps_obj:
            fps_obj.stop()
        if ping_obj:
            ping_obj.stop()
        root.quit()
        root.destroy()
        os._exit(0)


def open_settings():
    win = tk.Toplevel(root)
    win.geometry("350x550")
    win.configure(bg=settings['bg'])
    win.attributes('-topmost', True)
    win.overrideredirect(True)

    header_win = tk.Frame(win, bg=settings['accent'], height=30)
    header_win.pack(fill=tk.X)

    def start_move_win(event):
        drag_data["x"] = event.x
        drag_data["y"] = event.y

    def do_move_win(event):
        x = win.winfo_x() + (event.x - drag_data["x"])
        y = win.winfo_y() + (event.y - drag_data["y"])
        win.geometry(f"+{x}+{y}")

    header_win.bind('<Button-1>', start_move_win)
    header_win.bind('<B1-Motion>', do_move_win)

    tk.Label(header_win, text="⚙️ SETTINGS", font=(settings['font_family'], 11, "bold"),
             fg="white", bg=settings['accent']).pack(pady=5)

    close_btn = tk.Button(header_win, text="✕", command=win.destroy,
                          bg=settings['accent'], fg="white", relief=tk.FLAT)
    close_btn.pack(side=tk.RIGHT, padx=5, pady=2)

    canvas = tk.Canvas(win, bg=settings['bg'], highlightthickness=0)
    scroll = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scrollable_set = tk.Frame(canvas, bg=settings['bg'])
    scrollable_set.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_set, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)
    canvas.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    # COLORS
    f1 = tk.LabelFrame(scrollable_set, text="🎨 COLORS", bg=settings['bg'], fg=settings['accent'])
    f1.pack(fill=tk.X, padx=15, pady=5)

    def change_accent():
        c = colorchooser.askcolor()[1]
        if c:
            settings['accent'] = c
            apply_style()
            save_config()

    def change_bg():
        c = colorchooser.askcolor()[1]
        if c:
            settings['bg'] = c
            apply_style()
            save_config()

    def change_card():
        c = colorchooser.askcolor()[1]
        if c:
            settings['card'] = c
            apply_style()
            save_config()

    tk.Button(f1, text="Accent Color", command=change_accent,
              bg=settings['accent'], fg="white", relief=tk.FLAT).pack(pady=3, padx=10, fill=tk.X)
    tk.Button(f1, text="Background Color", command=change_bg,
              bg=settings['bg'], fg="white", relief=tk.FLAT).pack(pady=3, padx=10, fill=tk.X)
    tk.Button(f1, text="Card Color", command=change_card,
              bg=settings['card'], fg="white", relief=tk.FLAT).pack(pady=3, padx=10, fill=tk.X)

    # FONT
    f2 = tk.LabelFrame(scrollable_set, text="🔤 FONT", bg=settings['bg'], fg=settings['accent'])
    f2.pack(fill=tk.X, padx=15, pady=5)

    fonts = ['Segoe UI', 'Arial', 'Verdana', 'Tahoma', 'Consolas', 'Courier New', 'Impact']
    font_var = tk.StringVar(value=settings['font_family'])
    font_menu = tk.OptionMenu(f2, font_var, *fonts, command=lambda x: change_font(x))
    font_menu.config(bg=settings['card'], fg=settings['text'], relief=tk.FLAT)
    font_menu.pack(pady=3, padx=10, fill=tk.X)

    size_var = tk.IntVar(value=settings['font_size'])
    size_scale = tk.Scale(f2, from_=7, to=14, orient=tk.HORIZONTAL, variable=size_var,
                          bg=settings['bg'], fg=settings['accent'], highlightthickness=0,
                          command=lambda x: change_font_size(int(x)))
    size_scale.pack(pady=3, padx=10, fill=tk.X)

    def change_font(f):
        settings['font_family'] = f
        apply_style()
        save_config()

    def change_font_size(s):
        settings['font_size'] = s
        apply_style()
        save_config()

    # HOTKEYS
    f3 = tk.LabelFrame(scrollable_set, text="⌨️ HOTKEYS", bg=settings['bg'], fg=settings['accent'])
    f3.pack(fill=tk.X, padx=15, pady=5)

    def make_key_row(text, key_name, current_key):
        frame = tk.Frame(f3, bg=settings['bg'])
        frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(frame, text=text, bg=settings['bg'], fg=settings['text'], width=14, anchor='w').pack(side=tk.LEFT)
        lbl = tk.Label(frame, text=current_key.upper(), bg=settings['bg'], fg=settings['accent'], width=8)
        lbl.pack(side=tk.LEFT, padx=10)

        def bind():
            nonlocal current_key

            def on_key(e):
                k = e.keysym.lower()
                if k == 'escape':
                    w.destroy()
                    return
                if key_name == 'menu_key':
                    settings['menu_key'] = k
                elif key_name == 'clicker_key':
                    clicker_key = k
                elif key_name == 'presser_key':
                    presser_key = k
                lbl.config(text=k.upper())
                save_config()
                setup_hotkeys()
                w.destroy()

            w = tk.Toplevel(win)
            w.geometry("300x150")
            w.configure(bg=settings['bg'])
            w.attributes('-topmost', True)
            w.overrideredirect(True)
            w_header = tk.Frame(w, bg=settings['accent'], height=25)
            w_header.pack(fill=tk.X)
            tk.Button(w_header, text="✕", command=w.destroy,
                      bg=settings['accent'], fg="white", relief=tk.FLAT).pack(side=tk.RIGHT)
            tk.Label(w, text="Press any key...\nESC - cancel", font=(settings['font_family'], 12),
                     fg=settings['text'], bg=settings['bg']).pack(expand=True)
            w.bind('<Key>', on_key)

        tk.Button(frame, text="Change", command=bind,
                  bg=settings['accent'], fg="white", relief=tk.FLAT, padx=10).pack(side=tk.RIGHT)

    make_key_row("Menu", 'menu_key', settings['menu_key'])
    make_key_row("Auto Clicker", 'clicker_key', clicker_key)
    make_key_row("Key Presser", 'presser_key', presser_key)

    # RESET
    f4 = tk.LabelFrame(scrollable_set, text="⚠️ RESET", bg=settings['bg'], fg=settings['accent'])
    f4.pack(fill=tk.X, padx=15, pady=5)

    def reset():
        if messagebox.askyesno("Reset", "Reset all settings? Program will restart."):
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            os.execl(sys.executable, sys.executable, *sys.argv)

    tk.Button(f4, text="🔄 RESET ALL", command=reset,
              bg="#e74c3c", fg="white", relief=tk.FLAT).pack(pady=3, padx=10, fill=tk.X)

    tk.Button(scrollable_set, text="CLOSE", command=win.destroy,
              bg=settings['accent'], fg="white", relief=tk.FLAT).pack(pady=10, padx=15, fill=tk.X)


# ===== INTERFACE =====

root = tk.Tk()
root.geometry("340x700")
root.configure(bg=settings['bg'])
root.attributes('-topmost', True)
root.overrideredirect(True)
root.withdraw()

header = tk.Frame(root, bg=settings['accent'], height=35)
header.pack(fill=tk.X)
header.bind('<Button-1>', start_move)
header.bind('<B1-Motion>', do_move)

close_main_btn = tk.Button(header, text="✕", command=shutdown_program,
                           bg=settings['accent'], fg="white", relief=tk.FLAT)
close_main_btn.pack(side=tk.RIGHT, padx=5, pady=5)

title = tk.Label(header, text="✦ F34kY CORE ✦", font=(settings['font_family'], 12, "bold"),
                 fg="white", bg=settings['accent'])
title.pack(pady=8)
title.bind('<Button-1>', start_move)
title.bind('<B1-Motion>', do_move)

canvas = tk.Canvas(root, bg=settings['bg'], highlightthickness=0)
scroll = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable = tk.Frame(canvas, bg=settings['bg'])
scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable, anchor="nw")
canvas.configure(yscrollcommand=scroll.set)
canvas.pack(side="left", fill="both", expand=True)
scroll.pack(side="right", fill="y")


def create_foldable_card(title_text, expand_name):
    card = tk.Frame(scrollable, bg=settings['card'], relief=tk.FLAT, bd=1)
    card.pack(fill=tk.X, padx=8, pady=4)
    header_btn = tk.Button(card, text=f"▶ {title_text}",
                           bg=settings['card'], fg=settings['accent'],
                           relief=tk.FLAT, anchor='w', padx=10,
                           font=(settings['font_family'], 9, "bold"))
    header_btn.pack(fill=tk.X, pady=4)
    header_btn.original_text = title_text
    content = tk.Frame(card, bg=settings['card'])

    def on_click():
        toggle_expand(expand_name, content, header_btn)

    header_btn.config(command=on_click)
    return card, content


# 1. BUNNY HOP
card1, bh_content = create_foldable_card("🐰 BUNNY HOP", 'bhop')
bh_enable_btn = tk.Button(bh_content, text="▶️ DISABLED", command=toggle_bhop,
                          bg=settings['card'], fg="white", relief=tk.FLAT, height=1)
bh_enable_btn.pack(fill=tk.X, padx=10, pady=3)
tk.Label(bh_content, text="🔧 ALT - toggle | END - exit\nSPACE - jump (when enabled)",
         bg=settings['card'], fg="#888", font=(settings['font_family'], 7)).pack(pady=2)

# 2. AUTO CLICKER
card2, cl_content = create_foldable_card("🖱️ AUTO CLICKER", 'clicker')
cl_enable_btn = tk.Button(cl_content, text="▶️ DISABLED", command=toggle_clicker,
                          bg=settings['card'], fg="white", relief=tk.FLAT, height=1)
cl_enable_btn.pack(fill=tk.X, padx=10, pady=3)
f_row = tk.Frame(cl_content, bg=settings['card'])
f_row.pack(fill=tk.X, padx=10, pady=2)
tk.Label(f_row, text="CPS:", bg=settings['card'], fg="#888").pack(side=tk.LEFT)
cl_cps_label = tk.Label(f_row, text="20", bg=settings['card'], fg=settings['accent'], width=5)
cl_cps_label.pack(side=tk.LEFT)
cl_slider = tk.Scale(f_row, from_=5, to=100, orient=tk.HORIZONTAL, command=set_clicker_cps,
                     bg=settings['card'], fg=settings['accent'], highlightthickness=0, length=160)
cl_slider.set(20)
cl_slider.pack(side=tk.LEFT, padx=5)
f_row2 = tk.Frame(cl_content, bg=settings['card'])
f_row2.pack(fill=tk.X, padx=10, pady=2)
tk.Label(f_row2, text="CLICKS:", bg=settings['card'], fg="#888").pack(side=tk.LEFT)
cl_cnt_label = tk.Label(f_row2, text="0", bg=settings['card'], fg="#ffd93d", width=6)
cl_cnt_label.pack(side=tk.LEFT)
tk.Button(f_row2, text="RESET", command=reset_clicker_count, bg="#333", fg="white", relief=tk.FLAT, padx=5).pack(
    side=tk.LEFT, padx=5)
cl_key_label = tk.Label(cl_content, text=f"🔧 Press {clicker_key.upper()} - start/stop",
                        bg=settings['card'], fg="#888", font=(settings['font_family'], 7))
cl_key_label.pack(pady=2)

# 3. KEY PRESSER
card3, pr_content = create_foldable_card("⌨️ KEY PRESSER", 'presser')
pr_enable_btn = tk.Button(pr_content, text="▶️ DISABLED", command=toggle_presser,
                          bg=settings['card'], fg="white", relief=tk.FLAT, height=1)
pr_enable_btn.pack(fill=tk.X, padx=10, pady=3)
f_row = tk.Frame(pr_content, bg=settings['card'])
f_row.pack(fill=tk.X, padx=10, pady=2)
tk.Label(f_row, text="DELAY:", bg=settings['card'], fg="#888").pack(side=tk.LEFT)
pr_delay_label = tk.Label(f_row, text="0.5", bg=settings['card'], fg=settings['accent'], width=5)
pr_delay_label.pack(side=tk.LEFT)
pr_slider = tk.Scale(f_row, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, command=set_presser_delay,
                     bg=settings['card'], fg=settings['accent'], highlightthickness=0, length=160)
pr_slider.set(0.5)
pr_slider.pack(side=tk.LEFT, padx=5)
pr_key_label = tk.Label(pr_content, text=f"🔧 Press {presser_key.upper()} - start/stop",
                        bg=settings['card'], fg="#888", font=(settings['font_family'], 7))
pr_key_label.pack(pady=2)

# 4. CS:GO CROSSHAIR
card4, crosshair_content = create_foldable_card("🎯 CS:GO CROSSHAIR", 'crosshair')
crosshair_enable_btn = tk.Button(crosshair_content, text="▶️ DISABLED", command=toggle_crosshair,
                                 bg=settings['card'], fg="white", relief=tk.FLAT, height=1)
crosshair_enable_btn.pack(fill=tk.X, padx=10, pady=3)
tk.Label(crosshair_content, text="🔧 Green crosshair in center of screen",
         bg=settings['card'], fg="#888", font=(settings['font_family'], 7)).pack(pady=2)
crosshair_status_label = tk.Label(crosshair_content, text="⚫ Inactive", bg=settings['card'], fg="#888")
crosshair_status_label.pack()

# 5. FPS COUNTER
card5, fps_content = create_foldable_card("📊 FPS COUNTER", 'fps')
fps_enable_btn = tk.Button(fps_content, text="▶️ DISABLED", command=toggle_fps,
                           bg=settings['card'], fg="white", relief=tk.FLAT, height=1)
fps_enable_btn.pack(fill=tk.X, padx=10, pady=3)
tk.Label(fps_content, text="🔧 Bottom-right corner\nGreen (>60) / Yellow (30-60) / Red (<30)",
         bg=settings['card'], fg="#888", font=(settings['font_family'], 7)).pack(pady=2)
fps_status_label = tk.Label(fps_content, text="⚫ Inactive", bg=settings['card'], fg="#888")
fps_status_label.pack()

# 6. PING COUNTER
card6, ping_content = create_foldable_card("📶 PING COUNTER", 'ping')
ping_enable_btn = tk.Button(ping_content, text="▶️ DISABLED", command=toggle_ping,
                            bg=settings['card'], fg="white", relief=tk.FLAT, height=1)
ping_enable_btn.pack(fill=tk.X, padx=10, pady=3)
tk.Label(ping_content, text="🔧 Bottom-left corner\nGreen (<60) / Yellow (60-120) / Red (>120)",
         bg=settings['card'], fg="#888", font=(settings['font_family'], 7)).pack(pady=2)
ping_status_label = tk.Label(ping_content, text="⚫ Inactive", bg=settings['card'], fg="#888")
ping_status_label.pack()

# 7. MACRO
card7, m_content = create_foldable_card("🎬 MACRO", 'macro')
macro_rec_btn = tk.Button(m_content, text="▶️ RECORD", command=start_rec,
                          bg=settings['card'], fg="white", relief=tk.FLAT, height=1)
macro_rec_btn.pack(fill=tk.X, padx=10, pady=3)
macro_play_btn = tk.Button(m_content, text="▶️ PLAY", command=play_macro,
                           bg=settings['card'], fg="white", relief=tk.FLAT, height=1)
macro_play_btn.pack(fill=tk.X, padx=10, pady=3)
macro_status = tk.Label(m_content, text="READY", bg=settings['card'], fg="#888")
macro_status.pack()
tk.Button(m_content, text="🌊 SHOW/HIDE WINDOW", command=toggle_macro_window,
          bg=settings['accent'], fg="white", relief=tk.FLAT).pack(fill=tk.X, padx=10, pady=3)
tk.Label(m_content, text=f"🔧 R - RECORD (ENTER click) | T - PLAY",
         bg=settings['card'], fg="#888", font=(settings['font_family'], 7)).pack(pady=2)

# SETTINGS AT BOTTOM
set_card = tk.Frame(scrollable, bg=settings['accent'])
set_card.pack(fill=tk.X, padx=8, pady=8)

settings_btn = tk.Button(set_card, text="⚙️ SETTINGS", command=open_settings,
                         bg=settings['accent'], fg="white", relief=tk.FLAT, height=1)
settings_btn.pack(fill=tk.X, padx=10, pady=3)

menu_key_label = tk.Label(set_card, text=f"MENU: {settings['menu_key']}",
                          bg=settings['accent'], fg="white", font=(settings['font_family'], 8))
menu_key_label.pack(pady=2)

exit_btn = tk.Button(set_card, text="⛔ EXIT", command=shutdown_program,
                     bg="#e74c3c", fg="white", relief=tk.FLAT, height=1)
exit_btn.pack(fill=tk.X, padx=10, pady=3)

status_bar = tk.Label(root, text="✅ F34kY CORE v3.0", bg=settings['accent'], fg="white")
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# ===== START =====
load_config()
setup_hotkeys()
update_keys()


root.mainloop()
