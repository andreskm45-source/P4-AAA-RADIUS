#!/usr/bin/env python3
"""
Genera la portada del video y las imagenes marcador de posicion (placeholders)
del repositorio P4.

Autor : Rafael Andres Reyes De La Cruz - 2025-0784
Uso   : python scripts/tools/generar_imagenes.py
Requisitos: Pillow  (pip install pillow)

Las imagenes de images/ son marcadores: deben reemplazarse por capturas reales
del laboratorio conservando el mismo nombre de archivo.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)

INK = (15, 23, 42)
MUTED = (100, 116, 139)
BG = (248, 250, 252)
BLUE = (29, 78, 216)
RED = (220, 38, 38)
WHITE = (255, 255, 255)


def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def centered(draw, text, y, f, fill):
    w = draw.textlength(text, font=f)
    draw.text(((1280 - w) / 2, y), text, font=f, fill=fill)


def portada():
    im = Image.new("RGB", (1280, 720), WHITE)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1280, 720], fill=(241, 245, 249))
    d.rectangle([60, 60, 1220, 660], fill=WHITE, outline=BLUE, width=3)
    d.rectangle([60, 60, 1220, 80], fill=BLUE)

    centered(d, "SEGURIDAD DE REDES", 150, font(30, True), BLUE)
    centered(d, "P4 - AAA con RADIUS, AD y NPS", 205, font(54, True), INK)
    centered(d, "Router y switch Cisco autenticados contra Windows NPS", 285, font(26), MUTED)
    centered(d, "Niveles 0 / 5 / 10  ·  SSH  ·  Auditoria", 330, font(26), MUTED)

    # Boton de reproduccion
    cx, cy, r = 640, 455, 62
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    d.polygon([(cx - 20, cy - 32), (cx - 20, cy + 32), (cx + 36, cy)], fill=WHITE)
    centered(d, "VIDEO DEMOSTRATIVO", 545, font(24, True), RED)

    centered(d, "Rafael Andres Reyes De La Cruz  ·  Matricula 2025-0784", 610, font(24, True), INK)
    im.save(IMG / "portada_video.png", "PNG")
    print("OK  images/portada_video.png")


PLACEHOLDERS = [
    ("01_topologia_pnetlab.png", "Topologia en PNetLab"),
    ("02_r1_show_run_aaa.png", "R1: show running-config | section aaa"),
    ("03_sw1_show_run_aaa.png", "SW1: show running-config | section aaa"),
    ("04_consola_nivel0.png", "Consola R1: login usr.nivel0 (nivel 0)"),
    ("05_consola_nivel5.png", "Consola R1: login usr.nivel5 (nivel 5)"),
    ("06_consola_nivel10.png", "Consola R1: login usr.nivel10 (nivel 10)"),
    ("07_consola_admin_fallback.png", "Consola R1: admin.p4 con NPS detenido"),
    ("08_ssh_local_ok.png", "SSH desde SRV1 con admin.p4"),
    ("09_telnet_denegado.png", "Telnet rechazado (transporte no permitido)"),
    ("10_nps_clientes.png", "NPS: clientes RADIUS P4-R1 y P4-SW1"),
    ("11_nps_politicas.png", "NPS: politicas de red por grupo"),
    ("12_nps_vsa_privlvl.png", "NPS: VSA Cisco shell:priv-lvl"),
    ("13_nps_evento_6272.png", "Visor de eventos: 6272 acceso concedido"),
    ("14_nps_evento_6273.png", "Visor de eventos: 6273 acceso denegado"),
    ("15_show_aaa_servers.png", "R1: show aaa servers / show radius statistics"),
    ("16_show_logging.png", "R1: show logging (AAA y RADIUS)"),
    ("17_ad_grupos.png", "AD: grupos GRP_NIVEL0/5/10"),
    ("18_ad_usuarios.png", "AD: usuarios y pertenencia a grupos"),
    ("19_fecha_hora_video.png", "Fecha y hora visibles durante el video"),
    ("20_ping_validacion.png", "Ping SRV1 -> R1 / SW1 por VLAN 99"),
]


def placeholder(name, caption):
    im = Image.new("RGB", (1280, 720), (226, 232, 240))
    d = ImageDraw.Draw(im)
    d.rectangle([24, 24, 1256, 696], fill=BG, outline=(148, 163, 184), width=3)
    d.rectangle([24, 24, 1256, 96], fill=(71, 85, 105))
    d.text((48, 46), "EVIDENCIA PENDIENTE", font=font(28, True), fill=WHITE)
    d.text((48, 130), caption, font=font(34, True), fill=INK)
    d.text((48, 200), f"Archivo: images/{name}", font=font(22), fill=MUTED)
    d.text((48, 250), "Reemplace esta imagen por la captura real del laboratorio", font=font(22), fill=MUTED)
    d.text((48, 282), "conservando exactamente el mismo nombre de archivo.", font=font(22), fill=MUTED)
    d.text((48, 360), "Sugerencia: recorte solo la ventana relevante, sin datos personales", font=font(18), fill=MUTED)
    d.text((48, 388), "y con la fecha/hora del sistema visible cuando aplique.", font=font(18), fill=MUTED)
    im.save(IMG / name, "PNG")


if __name__ == "__main__":
    portada()
    for n, c in PLACEHOLDERS:
        placeholder(n, c)
    print(f"OK  {len(PLACEHOLDERS)} marcadores en images/")
