import tkinter as tk
from tkinter import ttk, messagebox, font
import random
import psutil
import pyautogui
import threading
import time
import urllib.request
import keyboard  # Billentyűfigyeléshez

# --- Konfiguráció ---
JELSZO = "Zora2002"
ONEDRIVE_STATE_URL = "https://raw.githubusercontent.com/babadam2002/numberapp.exe/main/engedely.py"

# --- Globális állapotok ---
generalas_aktiv = True
autoklikker_aktiv = False

# --- Szám generálók ---
def generate_szenzor():
    n1 = round(random.uniform(0.1, 4.9), 1)
    n2 = round(random.uniform(0.1, 4.9), 1)
    return f"{str(n1).replace('.', ',')}/{str(n2).replace('.', ',')}"

def generate_scu1():
    while True:
        num = random.uniform(0.000, 0.199)
        rounded = round(num, 3)
        if rounded == 0.0:
            return "0,000"
        if 0.010 <= rounded <= 0.100:
            if random.random() < 0.9:
                return f"{rounded:.3f}".replace('.', ',')
        else:
            if random.random() < 0.1:
                return f"{rounded:.3f}".replace('.', ',')

def generate_scu2():
    n = random.randint(45, 84)
    return f"45,{n}"

# --- Notepad számláló ---
def count_notepad_instances():
    count = 0
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'notepad' in proc.info['name'].lower():
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return count

# --- OneDrive állapot ellenőrzése ---
def is_program_enabled():
    try:
        with urllib.request.urlopen(ONEDRIVE_STATE_URL) as response:
            content = response.read().decode().strip().lower()
            return content == "on"
    except Exception as e:
        print(f"Hiba a OneDrive fájl lekérésekor: {e}")
        return False

# --- Szám választása ---
def generate_number():
    choice = selected_option.get()
    if choice == "Szenzor":
        return generate_szenzor()
    elif choice == "SCU1":
        return generate_scu1()
    elif choice == "SCU2":
        return generate_scu2()
    else:
        return None

# --- Gépelés emulálása ---
def do_typing(number_str):
#  pyautogui.click()  # 1. egérkattintás a fókuszhoz
    pyautogui.press('tab')
    time.sleep(0.5)
    pyautogui.press('tab')
    time.sleep(0.5)
    pyautogui.write(number_str, interval=0.05)
    time.sleep(0.1)
    for _ in range(4):
        pyautogui.press('tab')
        time.sleep(0.05)
    pyautogui.press('enter')

# --- Generálás ki/be kapcsolása ---
def toggle_generalas():
    global generalas_aktiv
    generalas_aktiv = not generalas_aktiv
    new_text = "Generálás leállítása" if generalas_aktiv else "Generálás elindítása"
    generalas_button.config(text=new_text)
    print(f"Generálás {'elindítva' if generalas_aktiv else 'leállítva'}")

# --- Autoklikker Ctrl toggle ---
def ctrl_toggle_autoklikker():
    global autoklikker_aktiv
    while True:
        keyboard.wait('ctrl')
        autoklikker_aktiv = not autoklikker_aktiv
        print(f"Auto-klikker {'bekapcsolva' if autoklikker_aktiv else 'kikapcsolva'}")
        time.sleep(0.3)

# --- Autoklikker működtetése ---
def run_autoklikker():
    while True:
        if autoklikker_aktiv:
            pyautogui.click()
        time.sleep(0.5)

# --- Státusz frissítések ---
def update_autoklikker_label():
    status = "bekapcsolva" if autoklikker_aktiv else "kikapcsolva"
    autoklikker_label.config(text=f"Auto-klikker: {status}")
    main_window.after(500, update_autoklikker_label)

# --- Monitorozás ---
def monitor_and_type():
    action_done = False
    while True:
        if not is_program_enabled():
            try:
                main_window.after(0, main_window.destroy)
            except Exception:
                pass
            break

        notepad_count = count_notepad_instances()
        if generalas_aktiv and not action_done and notepad_count >= 2:
            number = generate_number()
            if number:
                do_typing(number)
                action_done = True
        elif notepad_count < 2:
            action_done = False

        time.sleep(1)

# --- Jelszó ellenőrzés ---
def check_password(event=None):
    if password_entry.get() == JELSZO:
        password_window.destroy()
        start_main_app()
    else:
        messagebox.showerror("Hibás jelszó", "Hibás jelszó, próbáld újra!")

# --- Főalkalmazás ---
def start_main_app():
    global selected_option, main_window, autoklikker_label, generalas_button
    main_window = tk.Tk()
    main_window.title("Számgenerátor")
    main_window.geometry("370x290")

    selected_option = tk.StringVar(value="Szenzor")

    frame = ttk.Frame(main_window, padding=20)
    frame.pack(fill='both', expand=True)

    ttk.Label(frame, text="Számgenerátor", font=("Segoe UI", 22, "bold")).pack(anchor='w', pady=(0,10))

    ttk.Radiobutton(frame, text="Szenzor (pl. 0,3/2,9)", variable=selected_option, value="Szenzor").pack(anchor='w')
    ttk.Radiobutton(frame, text="SCU 1. (pl. 0,080)", variable=selected_option, value="SCU1").pack(anchor='w')
    ttk.Radiobutton(frame, text="SCU 2. (pl. 45,65)", variable=selected_option, value="SCU2").pack(anchor='w')

    generalas_button = ttk.Button(frame, text="Generálás leállítása", command=toggle_generalas)
    generalas_button.pack(pady=(15, 5))

    autoklikker_label = ttk.Label(frame, text="Auto-klikker: kikapcsolva", font=("Segoe UI", 10, "italic"))
    autoklikker_label.pack(pady=(10, 0))

    # Szálak elindítása
    threading.Thread(target=monitor_and_type, daemon=True).start()
    threading.Thread(target=run_autoklikker, daemon=True).start()
    threading.Thread(target=ctrl_toggle_autoklikker, daemon=True).start()
    update_autoklikker_label()

    main_window.mainloop()

# --- Jelszó ablak ---
password_window = tk.Tk()
password_window.title("Jelszó")
password_window.geometry("400x300")
password_window.resizable(False, False)

title_font = font.Font(family="Segoe UI", size=16, weight="bold")
entry_font = font.Font(family="Segoe UI", size=14)

frame = tk.Frame(password_window)
frame.place(relx=0.5, rely=0.5, anchor="center")

label = tk.Label(frame, text="Add meg a jelszót:", font=title_font)
label.pack(pady=(0,15))

password_entry = tk.Entry(frame, show="*", font=entry_font, width=20)
password_entry.pack(pady=(0,15))
password_entry.focus()

enter_button = tk.Button(frame, text="Belépés", font=entry_font, command=check_password, width=10)
enter_button.pack()

password_entry.bind("<Return>", check_password)

password_window.mainloop()
