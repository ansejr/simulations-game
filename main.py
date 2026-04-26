import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SELF_NAME = os.path.basename(__file__)

EXCLUDE_FILES = {SELF_NAME, "__init__.py"}

SIMULATION_FILES = sorted(
    [name for name in os.listdir(SCRIPT_DIR)
     if name.endswith(".py") and name not in EXCLUDE_FILES]
)

if not SIMULATION_FILES:
    raise RuntimeError("Nenhuma simulação em Python encontrada no diretório.")


def format_button_text(filename: str) -> str:
    name = filename.rsplit(".py", 1)[0]
    name = name.replace("_", " ")
    name = name.replace("jogo do caos", "Jogo do Caos")
    return " ".join(word.capitalize() for word in name.split())


def run_simulation(filename: str):
    script_path = os.path.join(SCRIPT_DIR, filename)

    if not os.path.isfile(script_path):
        messagebox.showerror(
            "Arquivo não encontrado",
            f"O arquivo {filename} não existe no diretório de simulações."
        )
        return

    def target():
        try:
            process = subprocess.Popen(
                [sys.executable, script_path],
                cwd=SCRIPT_DIR,
            )
            process.wait()
            if process.returncode != 0:
                messagebox.showwarning(
                    "Simulação finalizada",
                    f"A simulação {filename} foi encerrada com código {process.returncode}."
                )
        except Exception as exc:
            messagebox.showerror(
                "Erro ao iniciar a simulação",
                f"Não foi possível abrir {filename}: {exc}"
            )
        finally:
            root.after(0, restore_menu)

    hide_menu()
    threading.Thread(target=target, daemon=True).start()


def hide_menu():
    for button in buttons:
        button.config(state=tk.DISABLED)
    root.withdraw()


def restore_menu():
    root.deiconify()
    for button in buttons:
        button.config(state=tk.NORMAL)


root = tk.Tk()
root.title("Menu de Simulações")
root.geometry("820x520")
root.resizable(False, False)

frame = ttk.Frame(root, padding=20)
frame.pack(fill=tk.BOTH, expand=True)

label_title = ttk.Label(
    frame,
    text="Escolha uma simulação para executar",
    font=("Segoe UI", 18, "bold"),
)
label_title.pack(pady=(0, 20))

button_frame = ttk.Frame(frame)
button_frame.pack(fill=tk.BOTH, expand=True)

buttons = []
columns = 3
for index, script_name in enumerate(SIMULATION_FILES):
    text = format_button_text(script_name)
    button = ttk.Button(
        button_frame,
        text=text,
        command=lambda name=script_name: run_simulation(name),
    )
    row = index // columns
    column = index % columns
    button.grid(row=row, column=column, padx=12, pady=12, sticky="nsew")
    buttons.append(button)

for i in range(columns):
    button_frame.columnconfigure(i, weight=1)

footer = ttk.Label(
    frame,
    text="A janela do menu ficará oculta enquanto a simulação estiver aberta.",
    font=("Segoe UI", 10),
    foreground="#444444"
)
footer.pack(pady=(20, 0))

root.mainloop()
