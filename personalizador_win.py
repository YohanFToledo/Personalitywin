"""
Personalizador Win10 + Win11 (sin software de terceros)
- Pestana Windows 10: modo claro/oscuro, transparencia, acento, barra, fondo
- Pestana Windows 11: todo lo anterior + alinear barra (centro/izq),
  widgets, chat, vista de tareas, busqueda, efecto mica/transparencia,
  color en barras de titulo, menu inicio.
- Funciona tocando el registro oficial de Windows.
- Para generar el .exe en Windows: doble clic a build_exe.bat
"""
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
import os
import sys

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import winreg
    import ctypes

REG_PERSONALIZE = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
REG_DWM = r"SOFTWARE\Microsoft\Windows\DWM"
REG_ADVANCED = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
REG_START = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Start"


def get_reg(root, path, name, default=None):
    if not IS_WINDOWS:
        return default
    try:
        with winreg.OpenKey(root, path) as k:
            val, _ = winreg.QueryValueEx(k, name)
            return val
    except (FileNotFoundError, OSError):
        return default


def set_reg(root, path, name, value, kind=None):
    if not IS_WINDOWS:
        raise OSError("Solo funciona en Windows")
    import winreg as wr
    if kind is None:
        kind = wr.REG_DWORD
    with wr.CreateKey(root, path) as k:
        wr.SetValueEx(k, name, 0, kind, value)
    try:
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "ImmersiveColorSet")
    except Exception:
        pass


def rgb_to_accent_dword(r, g, b):
    return (0xFF << 24) | (b << 16) | (g << 8) | r


def accent_dword_to_hex(val):
    try:
        r = val & 0xFF
        g = (val >> 8) & 0xFF
        b = (val >> 16) & 0xFF
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return "#0078d4"


def set_wallpaper(path):
    if IS_WINDOWS and os.path.isfile(path):
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personalizador Win10 + Win11")
        self.geometry("540x700")
        self.resizable(False, False)

        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except Exception:
            pass
        style.configure("TButton", padding=8, font=("Segoe UI", 10))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 15, "bold"))
        style.configure("TNotebook.Tab", padding=(14, 8), font=("Segoe UI", 10, "bold"))

        container = ttk.Frame(self, padding=14)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="✨ Personalizador Windows", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            container,
            text="Elige tu sistema arriba. Solo usa el registro oficial, sin terceros.",
            foreground="gray",
        ).pack(anchor="w", pady=(0, 8))

        if not IS_WINDOWS:
            ttk.Label(
                container,
                text="⚠️ Estás fuera de Windows: es modo vista previa. Copia el .exe o .py a tu Windows para aplicar.",
                foreground="red",
                wraplength=500,
                font=("Segoe UI", 9),
            ).pack(pady=4)

        # ===== NOTEBOOK con 2 pestañas =====
        self.nb = ttk.Notebook(container)
        self.nb.pack(fill="both", expand=True)

        self.tab10 = ttk.Frame(self.nb, padding=10)
        self.tab11 = ttk.Frame(self.nb, padding=10)
        self.nb.add(self.tab10, text="  🪟 Windows 10  ")
        self.nb.add(self.tab11, text="  🪟 Windows 11  ")

        self.build_tab10()
        self.build_tab11()

        # Botonera común
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Aplicar pestaña actual", command=self.aplicar_actual).pack(
            side="left", expand=True, fill="x", padx=(0, 6)
        )
        ttk.Button(btn_frame, text="Restablecer", command=self.restablecer).pack(
            side="left", expand=True, fill="x", padx=(6, 0)
        )
        ttk.Label(
            container,
            text="Tip: si la barra no cambia al instante, cierra sesión y vuelve a entrar.",
            foreground="gray",
            font=("Segoe UI", 8),
            justify="center",
        ).pack()

    # ---------- helpers UI ----------
    def color_row(self, parent, initial_hex):
        row = ttk.Frame(parent)
        row.pack(fill="x")
        hx = tk.StringVar(value=initial_hex)
        prev = tk.Canvas(row, width=40, height=24, highlightthickness=1, highlightbackground="#999")
        prev.pack(side="left")
        prev.create_rectangle(0, 0, 40, 24, fill=initial_hex, outline="")

        def elegir():
            c = colorchooser.askcolor(color=hx.get(), title="Elige color de acento")
            if c and c[1]:
                hx.set(c[1])
                prev.delete("all")
                prev.create_rectangle(0, 0, 40, 24, fill=c[1], outline="")

        ttk.Label(row, textvariable=hx, font=("Consolas", 10)).pack(side="left", padx=10)
        ttk.Button(row, text="Elegir color...", command=elegir).pack(side="right")
        return hx, prev

    def fondo_row(self, parent):
        card = ttk.LabelFrame(parent, text="  Fondo de pantalla  ", padding=10)
        card.pack(fill="x", pady=6)
        fp = tk.StringVar(value="Ningún archivo seleccionado")
        ttk.Button(
            card,
            text="Seleccionar imagen...",
            command=lambda: fp.set(
                filedialog.askopenfilename(
                    title="Elige fondo",
                    filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp")],
                )
                or fp.get()
            ),
        ).pack(anchor="w")
        ttk.Label(card, textvariable=fp, font=("Segoe UI", 8), foreground="gray", wraplength=440).pack(
            anchor="w", pady=4
        )
        return fp

    # ---------- PESTAÑA WIN10 ----------
    def build_tab10(self):
        c1 = ttk.LabelFrame(self.tab10, text="  Tema  ", padding=10)
        c1.pack(fill="x", pady=5)

        apps = get_reg(None, REG_PERSONALIZE, "AppsUseLightTheme", 1) if IS_WINDOWS else 1
        self.w10_modo = tk.StringVar(value="Claro" if apps == 1 else "Oscuro")
        ttk.Label(c1, text="Modo de aplicaciones:").pack(anchor="w")
        f = ttk.Frame(c1)
        f.pack(fill="x", pady=4)
        ttk.Radiobutton(f, text="Claro", variable=self.w10_modo, value="Claro").pack(side="left", padx=10)
        ttk.Radiobutton(f, text="Oscuro", variable=self.w10_modo, value="Oscuro").pack(side="left", padx=10)

        sys_light = get_reg(None, REG_PERSONALIZE, "SystemUsesLightTheme", 1) if IS_WINDOWS else 1
        self.w10_sistema = tk.BooleanVar(value=(sys_light == 0))
        ttk.Checkbutton(
            c1, text="Modo oscuro también en Barra e Inicio", variable=self.w10_sistema
        ).pack(anchor="w")

        trans = get_reg(None, REG_PERSONALIZE, "EnableTransparency", 1) if IS_WINDOWS else 1
        self.w10_trans = tk.BooleanVar(value=bool(trans))
        ttk.Checkbutton(c1, text="Efectos de transparencia", variable=self.w10_trans).pack(anchor="w")

        c2 = ttk.LabelFrame(self.tab10, text="  Color de acento  ", padding=10)
        c2.pack(fill="x", pady=5)
        acc = get_reg(None, REG_PERSONALIZE, "AccentColor", 0xFFD47800) if IS_WINDOWS else 0xFFD47800
        init_hex = accent_dword_to_hex(acc)
        self.w10_color, self.w10_prev = self.color_row(c2, init_hex)

        barra = get_reg(None, REG_PERSONALIZE, "ColorPrevalence", 0) if IS_WINDOWS else 0
        self.w10_barra = tk.BooleanVar(value=bool(barra))
        ttk.Checkbutton(c2, text="Mostrar color en Inicio y Barra de tareas", variable=self.w10_barra).pack(
            anchor="w", pady=(6, 0)
        )

        self.w10_fondo = self.fondo_row(self.tab10)

    # ---------- PESTAÑA WIN11 ----------
    def build_tab11(self):
        c1 = ttk.LabelFrame(self.tab11, text="  Tema Windows 11  ", padding=10)
        c1.pack(fill="x", pady=5)

        apps = get_reg(None, REG_PERSONALIZE, "AppsUseLightTheme", 1) if IS_WINDOWS else 1
        self.w11_modo = tk.StringVar(value="Claro" if apps == 1 else "Oscuro")
        ttk.Label(c1, text="Modo:").pack(anchor="w")
        f = ttk.Frame(c1)
        f.pack(fill="x", pady=4)
        ttk.Radiobutton(f, text="Claro", variable=self.w11_modo, value="Claro").pack(side="left", padx=10)
        ttk.Radiobutton(f, text="Oscuro", variable=self.w11_modo, value="Oscuro").pack(side="left", padx=10)

        sys_light = get_reg(None, REG_PERSONALIZE, "SystemUsesLightTheme", 1) if IS_WINDOWS else 1
        self.w11_sistema = tk.BooleanVar(value=(sys_light == 0))
        ttk.Checkbutton(c1, text="Oscuro también en Barra e Inicio", variable=self.w11_sistema).pack(anchor="w")

        trans = get_reg(None, REG_PERSONALIZE, "EnableTransparency", 1) if IS_WINDOWS else 1
        self.w11_trans = tk.BooleanVar(value=bool(trans))
        ttk.Checkbutton(
            c1, text="Transparencia y Mica (efecto Win11)", variable=self.w11_trans
        ).pack(anchor="w")

        c2 = ttk.LabelFrame(self.tab11, text="  Color de acento Win11  ", padding=10)
        c2.pack(fill="x", pady=5)
        acc = get_reg(None, REG_PERSONALIZE, "AccentColor", 0xFFD47800) if IS_WINDOWS else 0xFFD47800
        self.w11_color, self.w11_prev = self.color_row(c2, accent_dword_to_hex(acc))

        barra = get_reg(None, REG_PERSONALIZE, "ColorPrevalence", 0) if IS_WINDOWS else 0
        self.w11_barra = tk.BooleanVar(value=bool(barra))
        ttk.Checkbutton(c2, text="Acento en Inicio y Barra de tareas", variable=self.w11_barra).pack(anchor="w")

        dwm_prev = get_reg(None, REG_DWM, "ColorPrevalence", 0) if IS_WINDOWS else 0
        self.w11_titulos = tk.BooleanVar(value=bool(dwm_prev))
        ttk.Checkbutton(c2, text="Acento en barras de título y bordes", variable=self.w11_titulos).pack(anchor="w")
        ttk.Label(
            c2,
            text="En Win11 hay 2 interruptores: Inicio/barra + títulos. Activa ambos si quieres todo teñido.",
            foreground="gray",
            font=("Segoe UI", 8),
            wraplength=440,
        ).pack(anchor="w")

        c3 = ttk.LabelFrame(self.tab11, text="  Barra de tareas Win11  ", padding=10)
        c3.pack(fill="x", pady=5)

        alin = get_reg(None, REG_ADVANCED, "TaskbarAl", 1) if IS_WINDOWS else 1
        self.w11_alin = tk.StringVar(value="Centro" if alin == 1 else "Izquierda")
        ttk.Label(c3, text="Alineación de iconos:").pack(anchor="w")
        fa = ttk.Frame(c3)
        fa.pack(fill="x", pady=3)
        ttk.Radiobutton(fa, text="Centro", variable=self.w11_alin, value="Centro").pack(side="left", padx=10)
        ttk.Radiobutton(fa, text="Izquierda", variable=self.w11_alin, value="Izquierda").pack(side="left", padx=10)

        # Widgets, Chat, Vista tareas, Búsqueda
        self.w11_widgets = tk.BooleanVar(
            value=bool(get_reg(None, REG_ADVANCED, "TaskbarDa", 1) if IS_WINDOWS else 1)
        )
        self.w11_chat = tk.BooleanVar(
            value=bool(get_reg(None, REG_ADVANCED, "TaskbarMn", 1) if IS_WINDOWS else 0)
        )
        self.w11_taskview = tk.BooleanVar(
            value=bool(get_reg(None, REG_ADVANCED, "ShowTaskViewButton", 1) if IS_WINDOWS else 1)
        )
        # SearchboxTaskbarMode: 0 ocultar, 1 icono, 2 cuadro... depende build. 1 por defecto.
        search_mode = get_reg(None, REG_ADVANCED, "SearchboxTaskbarMode", 1) if IS_WINDOWS else 1
        self.w11_search = tk.BooleanVar(value=(search_mode != 0))

        ttk.Checkbutton(c3, text="Mostrar Widgets en la barra", variable=self.w11_widgets).pack(anchor="w")
        ttk.Checkbutton(c3, text="Mostrar Chat (Teams)", variable=self.w11_chat).pack(anchor="w")
        ttk.Checkbutton(c3, text="Botón Vista de tareas", variable=self.w11_taskview).pack(anchor="w")
        ttk.Checkbutton(c3, text="Mostrar botón de Búsqueda", variable=self.w11_search).pack(anchor="w")

        c4 = ttk.LabelFrame(self.tab11, text="  Menú Inicio  ", padding=10)
        c4.pack(fill="x", pady=5)
        self.w11_recent = tk.BooleanVar(
            value=bool(get_reg(None, REG_START, "ShowRecentList", 1) if IS_WINDOWS else 1)
        )
        ttk.Checkbutton(c4, text="Mostrar archivos usados recientemente en Inicio", variable=self.w11_recent).pack(
            anchor="w"
        )

        self.w11_fondo = self.fondo_row(self.tab11)

    # ---------- aplicar ----------
    def hex_to_rgb(self, hx):
        hx = hx.lstrip("#")
        return int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)

    def aplicar_actual(self):
        idx = self.nb.index(self.nb.select())
        if idx == 0:
            self.aplicar_w10()
        else:
            self.aplicar_w11()

    def aplicar_w10(self):
        if not IS_WINDOWS:
            messagebox.showinfo(
                "Demo",
                "Modo vista previa.\nCopia este programa a tu Windows 10/11 o usa el .exe para aplicar.",
            )
            return
        try:
            apps_light = 1 if self.w10_modo.get() == "Claro" else 0
            sys_light = 0 if self.w10_sistema.get() else 1
            set_reg(winreg.HKEY_CURRENT_USER, REG_PERSONALIZE, "AppsUseLightTheme", apps_light)
            set_reg(winreg.HKEY_CURRENT_USER, REG_PERSONALIZE, "SystemUsesLightTheme", sys_light)
            set_reg(
                winreg.HKEY_CURRENT_USER,
                REG_PERSONALIZE,
                "EnableTransparency",
                1 if self.w10_trans.get() else 0,
            )
            set_reg(
                winreg.HKEY_CURRENT_USER,
                REG_PERSONALIZE,
                "ColorPrevalence",
                1 if self.w10_barra.get() else 0,
            )
            r, g, b = self.hex_to_rgb(self.w10_color.get())
            acc = rgb_to_accent_dword(r, g, b)
            set_reg(winreg.HKEY_CURRENT_USER, REG_PERSONALIZE, "AccentColor", acc)
            try:
                set_reg(winreg.HKEY_CURRENT_USER, REG_DWM, "ColorizationColor", acc)
                set_reg(winreg.HKEY_CURRENT_USER, REG_DWM, "ColorizationAfterglow", acc)
            except Exception:
                pass
            if os.path.isfile(self.w10_fondo.get()):
                set_wallpaper(self.w10_fondo.get())
            messagebox.showinfo("Listo", "Estilo Windows 10 aplicado ✅")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo aplicar:\n{e}")

    def aplicar_w11(self):
        if not IS_WINDOWS:
            messagebox.showinfo(
                "Demo",
                "Modo vista previa.\nCopia este programa a tu Windows 11 o usa el .exe para aplicar.",
            )
            return
        try:
            apps_light = 1 if self.w11_modo.get() == "Claro" else 0
            sys_light = 0 if self.w11_sistema.get() else 1
            set_reg(winreg.HKEY_CURRENT_USER, REG_PERSONALIZE, "AppsUseLightTheme", apps_light)
            set_reg(winreg.HKEY_CURRENT_USER, REG_PERSONALIZE, "SystemUsesLightTheme", sys_light)
            set_reg(
                winreg.HKEY_CURRENT_USER,
                REG_PERSONALIZE,
                "EnableTransparency",
                1 if self.w11_trans.get() else 0,
            )
            set_reg(
                winreg.HKEY_CURRENT_USER,
                REG_PERSONALIZE,
                "ColorPrevalence",
                1 if self.w11_barra.get() else 0,
            )
            # Título y bordes (DWM)
            set_reg(
                winreg.HKEY_CURRENT_USER,
                REG_DWM,
                "ColorPrevalence",
                1 if self.w11_titulos.get() else 0,
            )

            r, g, b = self.hex_to_rgb(self.w11_color.get())
            acc = rgb_to_accent_dword(r, g, b)
            set_reg(winreg.HKEY_CURRENT_USER, REG_PERSONALIZE, "AccentColor", acc)
            try:
                set_reg(winreg.HKEY_CURRENT_USER, REG_DWM, "ColorizationColor", acc)
                set_reg(winreg.HKEY_CURRENT_USER, REG_DWM, "ColorizationAfterglow", acc)
                set_reg(winreg.HKEY_CURRENT_USER, REG_DWM, "AccentColor", acc)
            except Exception:
                pass

            # Barra Win11
            set_reg(
                winreg.HKEY_CURRENT_USER,
                REG_ADVANCED,
                "TaskbarAl",
                1 if self.w11_alin.get() == "Centro" else 0,
            )
            set_reg(winreg.HKEY_CURRENT_USER, REG_ADVANCED, "TaskbarDa", 1 if self.w11_widgets.get() else 0)
            set_reg(winreg.HKEY_CURRENT_USER, REG_ADVANCED, "TaskbarMn", 1 if self.w11_chat.get() else 0)
            set_reg(
                winreg.HKEY_CURRENT_USER,
                REG_ADVANCED,
                "ShowTaskViewButton",
                1 if self.w11_taskview.get() else 0,
            )
            set_reg(
                winreg.HKEY_CURRENT_USER,
                REG_ADVANCED,
                "SearchboxTaskbarMode",
                1 if self.w11_search.get() else 0,
            )
            # Inicio
            try:
                set_reg(
                    winreg.HKEY_CURRENT_USER,
                    REG_START,
                    "ShowRecentList",
                    1 if self.w11_recent.get() else 0,
                )
            except Exception:
                pass

            if os.path.isfile(self.w11_fondo.get()):
                set_wallpaper(self.w11_fondo.get())

            # Reiniciar Explorer para que la barra aplique alineación/widgets al instante
            try:
                os.system("taskkill /f /im explorer.exe >nul 2>&1 & start explorer.exe >nul 2>&1")
            except Exception:
                pass

            messagebox.showinfo(
                "Listo",
                "Estilo Windows 11 aplicado ✅\nLa barra se reinicia para aplicar la alineación.",
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo aplicar:\n{e}")

    def restablecer(self):
        idx = self.nb.index(self.nb.select())
        if idx == 0:
            self.w10_modo.set("Claro")
            self.w10_sistema.set(False)
            self.w10_trans.set(True)
            self.w10_color.set("#0078d4")
            self.w10_barra.set(False)
            self.w10_fondo.set("Ningún archivo seleccionado")
        else:
            self.w11_modo.set("Claro")
            self.w11_sistema.set(False)
            self.w11_trans.set(True)
            self.w11_color.set("#0078d4")
            self.w11_barra.set(False)
            self.w11_titulos.set(False)
            self.w11_alin.set("Centro")
            self.w11_widgets.set(True)
            self.w11_chat.set(False)
            self.w11_taskview.set(True)
            self.w11_search.set(True)
            self.w11_recent.set(True)
            self.w11_fondo.set("Ningún archivo seleccionado")


if __name__ == "__main__":
    app = App()
    app.mainloop()
