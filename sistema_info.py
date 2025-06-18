from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGroupBox, QTextEdit, QScrollArea, QPushButton, QFileDialog
from PyQt5.QtGui import QIcon
import sys
import psutil
import platform
import cpuinfo
import GPUtil
import wmi
import socket
import getpass
import datetime
import requests
import ctypes

class SistemaGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Información del Sistema")
        self.setGeometry(100, 100, 550, 700)
        self.icono_claro = QIcon("icono_claro.png")
        self.icono_oscuro = QIcon("icono_oscuro.png")
        self.dark_mode = not self._is_windows_light_mode()
        self.toggle_tema(inicial=True)

        layout = QVBoxLayout()
        scroll_area = QScrollArea()
        content_widget = QWidget()
        self.content_layout = QVBoxLayout()

        self.secciones = [
            ("🧠 CPU", obtener_info_cpu),
            ("🎮 GPU", obtener_info_gpu),
            ("📦 RAM", obtener_info_ram),
            ("🖥️ Placa Base", obtener_info_placa_base),
            ("💾 Discos", obtener_info_discos),
            ("🌐 Red", obtener_info_red),
            ("🧬 BIOS", obtener_info_bios),
            ("🪪 Nombre y Usuario", obtener_info_equipo),
            ("⏱️ Uptime", obtener_info_uptime)
        ]

        self.grupos = []

        for titulo, funcion in self.secciones:
            grupo = QGroupBox(titulo)
            texto = QTextEdit()
            texto.setReadOnly(True)
            texto.setText(funcion())
            inner_layout = QVBoxLayout()
            inner_layout.addWidget(texto)
            grupo.setLayout(inner_layout)
            self.content_layout.addWidget(grupo)
            self.grupos.append((titulo, texto))

        exportar_btn = QPushButton("📝 Exportar a TXT")
        exportar_btn.clicked.connect(self.exportar_a_txt)
        self.content_layout.addWidget(exportar_btn)

        exportar_pdf_btn = QPushButton("📄 Exportar a PDF")
        exportar_pdf_btn.clicked.connect(self.exportar_a_pdf)
        self.content_layout.addWidget(exportar_pdf_btn)

        content_widget.setLayout(self.content_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def _is_windows_light_mode(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 1
        except:
            return False

    def _is_dark_mode(self):
        return not self._is_windows_light_mode() if platform.system() == 'Windows' else True

    def toggle_tema(self, inicial=False):
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e1e1e;
                    color: #f0f0f0;
                    font-family: Arial;
                }
                QGroupBox {
                    border: 1px solid #444;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 3px;
                    color: #ffa500;
                }
                QTextEdit {
                    background-color: #2b2b2b;
                    border: none;
                    color: #f0f0f0;
                }
                QPushButton {
                    background-color: #007acc;
                    border: none;
                    padding: 10px;
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #005999;
                }
            """)
            self.setWindowIcon(self.icono_oscuro)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #ffffff;
                    color: #000000;
                    font-family: Arial;
                }
                QGroupBox {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 3px;
                    color: #003366;
                }
                QTextEdit {
                    background-color: #f0f0f0;
                    border: none;
                    color: #000000;
                }
                QPushButton {
                    background-color: #007acc;
                    border: none;
                    padding: 10px;
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #005999;
                }
            """)
            self.setWindowIcon(self.icono_claro)

        if not inicial:
            self.dark_mode = not self.dark_mode

    def exportar_a_txt(self):
        fecha_hora = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
        ruta_sugerida = f"info_sistema_{fecha_hora}.txt"
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Informe", ruta_sugerida, "Archivos de texto (*.txt)")
        if ruta:
            with open(ruta, 'w', encoding='utf-8') as f:
                for titulo, widget in self.grupos:
                    f.write(f"=== {titulo} ===\n")
                    f.write(widget.toPlainText() + '\n\n')

    def exportar_a_pdf(self):
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        import os

        fecha_hora = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
        ruta_sugerida = f"informe_sistema_{fecha_hora}.pdf"
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar como PDF", ruta_sugerida, "Archivos PDF (*.pdf)")
        if ruta:
            c = canvas.Canvas(ruta, pagesize=A4)
            width, height = A4
            y = height - 2 * cm

            ahora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            c.setFont("Helvetica", 10)
            c.drawRightString(width - 2 * cm, y, f"Fecha y hora: {ahora}")
            y -= 0.75 * cm

            logo_path = "logo_pdf.png"
            if os.path.exists(logo_path):
                c.drawImage(logo_path, 2 * cm, y - 2.5 * cm, width=4 * cm, preserveAspectRatio=True, mask='auto')
                y -= 3 * cm

            c.setFont("Helvetica-Bold", 14)
            c.drawString(2 * cm, y, "Informe del Sistema")
            y -= 1 * cm

            c.setFont("Helvetica", 10)
            for titulo, widget in self.grupos:
                texto = widget.toPlainText().splitlines()
                c.drawString(2 * cm, y, f"{titulo}")
                y -= 0.5 * cm
                for linea in texto:
                    if y <= 2 * cm:
                        c.showPage()
                        c.setFont("Helvetica", 10)
                        y = height - 2 * cm
                    c.drawString(2.5 * cm, y, linea)
                    y -= 0.4 * cm
                y -= 0.6 * cm

            c.save()

# Funciones de obtención de información

def obtener_info_cpu():
    info = cpuinfo.get_cpu_info()
    return info.get('brand_raw', 'No detectado')

def obtener_info_gpu():
    gpus = GPUtil.getGPUs()
    return '\n'.join(gpu.name for gpu in gpus) if gpus else 'No detectado'

def obtener_info_ram():
    ram_bytes = psutil.virtual_memory().total
    ram_gb = ram_bytes / (1024 ** 3)
    return f"{ram_gb:.2f} GB"

def obtener_info_placa_base():
    try:
        c = wmi.WMI()
        for board in c.Win32_BaseBoard():
            return f"{board.Manufacturer} {board.Product}"
    except:
        return "No detectado"

def obtener_info_discos():
    texto = ""
    for p in psutil.disk_partitions():
        try:
            u = psutil.disk_usage(p.mountpoint)
            texto += f"{p.device}: {u.used / (1024**3):.2f} GB usados de {u.total / (1024**3):.2f} GB ({u.percent}%)\n"
        except:
            continue
    return texto.strip() or "No detectado"

def obtener_info_red():
    ip_local = socket.gethostbyname(socket.gethostname())
    try:
        ip_publica = requests.get('https://api.ipify.org').text
    except:
        ip_publica = "No disponible"
    return f"IP Local: {ip_local}\nIP Pública: {ip_publica}"

def obtener_info_bios():
    try:
        w = wmi.WMI()
        bios = w.Win32_BIOS()[0]
        system = w.Win32_ComputerSystem()[0]
        return (f"Fabricante: {system.Manufacturer}\n"
                f"Modelo: {system.Model}\n"
                f"Versión BIOS: {bios.SMBIOSBIOSVersion}\n"
                f"Fecha BIOS: {bios.ReleaseDate[:8]}")
    except:
        return "No detectado"

def obtener_info_equipo():
    return (f"Equipo: {platform.node()}\n"
            f"Usuario: {getpass.getuser()}\n"
            f"Arquitectura: {platform.machine()}")

def obtener_info_uptime():
    tiempo = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    dias = tiempo.days
    horas, resto = divmod(tiempo.seconds, 3600)
    minutos, _ = divmod(resto, 60)
    return f"Encendido: {dias}d {horas}h {minutos}m"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = SistemaGUI()
    ventana.show()
    sys.exit(app.exec_())
