#!/usr/bin/env python3
"""
Genera los diagramas SVG del repositorio P4.

Autor : Rafael Andres Reyes De La Cruz - 2025-0784
Uso   : python scripts/tools/generar_diagramas.py
Salida: diagrams/topologia.svg, diagrams/flujo_aaa.svg,
        diagrams/niveles_privilegio.svg
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "diagrams"
OUT.mkdir(exist_ok=True)

INK = "#0f172a"
MUTED = "#475569"
SOFT = "#64748b"
LINE = "#cbd5e1"
PANEL = "#f8fafc"
WHITE = "#ffffff"
BLUE = "#1d4ed8"
TEAL = "#0f766e"
VIOLET = "#7c3aed"
GREEN = "#059669"
AMBER = "#d97706"
RED = "#dc2626"
SANS = "Segoe UI, Inter, Arial, sans-serif"
MONO = "Consolas, Courier New, monospace"


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SVG:
    def __init__(self, w, h, bg=WHITE):
        self.w, self.h = w, h
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img">',
            "<defs>",
            '<marker id="arw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" '
            'markerHeight="6.5" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{SOFT}"/></marker>',
            '<marker id="arwB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" '
            'markerHeight="6.5" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>',
            '<marker id="arwR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" '
            'markerHeight="6.5" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker>',
            "</defs>",
            f'<rect width="{w}" height="{h}" fill="{bg}"/>',
        ]

    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill=WHITE, stroke=None, rx=0, sw=1.2, dash=None,
             opacity=None):
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'
        if stroke:
            s += f' stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            s += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            s += f' opacity="{opacity}"'
        self.add(s + "/>")

    def text(self, x, y, t, size=13, fill=INK, weight=400, anchor="start",
             family=SANS, ls=None, opacity=None):
        s = (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
             f'fill="{fill}" font-weight="{weight}" text-anchor="{anchor}"')
        if ls:
            s += f' letter-spacing="{ls}"'
        if opacity is not None:
            s += f' opacity="{opacity}"'
        self.add(s + f">{esc(t)}</text>")

    def line(self, x1, y1, x2, y2, color=LINE, width=1.4, dash=None, marker=None,
             cap="round"):
        s = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
             f'stroke-width="{width}" stroke-linecap="{cap}"')
        if dash:
            s += f' stroke-dasharray="{dash}"'
        if marker:
            s += f' marker-end="url(#{marker})"'
        self.add(s + "/>")

    def path(self, d, fill="none", stroke=LINE, width=1.6, dash=None, marker=None):
        s = (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" '
             f'stroke-linejoin="round" stroke-linecap="round"')
        if dash:
            s += f' stroke-dasharray="{dash}"'
        if marker:
            s += f' marker-end="url(#{marker})"'
        self.add(s + "/>")

    def circle(self, cx, cy, r, fill=WHITE, stroke=None, sw=1.4):
        s = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"'
        if stroke:
            s += f' stroke="{stroke}" stroke-width="{sw}"'
        self.add(s + "/>")

    def arrow(self, x1, y1, x2, y2, color=SOFT, width=1.6, dash=None, marker="arw"):
        self.line(x1, y1, x2, y2, color, width, dash, marker)

    def save(self, name):
        self.add("</svg>")
        (OUT / name).write_text("\n".join(self.parts), encoding="utf-8")
        print("OK ", name)


def header(s, title, subtitle, badge, right=1440):
    s.text(60, 54, title, 27, INK, 700)
    s.text(60, 82, subtitle, 14, MUTED)
    s.rect(right - 260, 30, 260, 40, "#eef2ff", "#c7d2fe", 20)
    s.text(right - 130, 56, badge, 13, "#3730a3", 700, "middle")
    s.line(60, 104, right, 104, "#e2e8f0", 1.2)


def card(s, x, y, w, h, color, name, platform, rows, tag_w=74):
    s.rect(x, y, w, h, WHITE, color, 12, 1.8)
    s.add(f'<path d="M{x+12},{y} h{w-24} a12,12 0 0 1 12,12 v32 h-{w} v-32 '
          f'a12,12 0 0 1 12,-12 z" fill="{color}"/>')
    s.text(x + 18, y + 30, name, 17, WHITE, 700)
    s.text(x + w - 18, y + 30, platform, 10.5, "#e2e8f0", 400, "end")
    for i, (txt, tag) in enumerate(rows):
        yy = y + 62 + i * 24
        s.text(x + 16, yy, txt, 11.6, "#334155", 400, family=MONO)
        if tag:
            s.text(x + w - 16, yy, tag, 10, color, 700, "end")


# ---------------------------------------------------------------------------
# 1. TOPOLOGIA
# ---------------------------------------------------------------------------
def topologia():
    s = SVG(1500, 900)

    header(
        s,
        "Laboratorio P4 — AAA con RADIUS, Active Directory y NPS",
        "Autor: Rafael Andrés Reyes De La Cruz · Matrícula 2025-0784 · PNetLab · Seguridad de Redes",
        "Red 10.7.84.0/24",
    )

    # --- Router ---
    card(
        s, 60, 124, 340, 170, BLUE, "R1-P4", "Cisco IOS 15.x",
        [
            ("G0/0.10  10.7.84.1/26", "VLAN 10"),
            ("G0/0.20  10.7.84.65/26", "VLAN 20"),
            ("G0/0.99  10.7.84.129/26", "VLAN 99"),
            ("RADIUS 10.7.84.66 · grupo RAD-P4", ""),
            ("AAA solo en con / aux · VTY local", ""),
        ],
    )

    # --- Switch ---
    card(
        s, 60, 420, 340, 262, TEAL, "SW1-P4", "Catalyst 2960 / IOU",
        [
            ("SVI Vlan99  10.7.84.130/26", "MGMT"),
            ("Gi0/1  trunk 802.1Q → R1", ""),
            ("Gi0/2  access VLAN 20 → SRV1", ""),
            ("Gi0/3  access VLAN 10 (demo)", ""),
            ("Gi0/4-24  parking VLAN 999", ""),
            ("Port-security · BPDU guard · DHCP snoop", ""),
            ("SSH solo desde 10.7.84.64/26", ""),
        ],
    )

    # --- Enlace troncal ---
    s.line(230, 294, 230, 420, TEAL, 5)
    s.circle(230, 294, 5, TEAL)
    s.circle(230, 420, 5, TEAL)
    s.rect(246, 316, 250, 66, "#ecfdf5", "#a7f3d0", 8)
    s.text(258, 338, "TRUNK 802.1Q", 11.5, "#065f46", 700)
    s.text(258, 356, "Gi0/1 ↔ Gi0/1 · VLAN 10,20,99", 10.5, "#047857")
    s.text(258, 372, "nativa 999 (sin uso)", 10.5, "#047857")

    # --- Panel flujo AAA ---
    s.rect(500, 118, 940, 250, PANEL, LINE, 14, 1.2)
    s.text(520, 146, "Flujo AAA — autenticación y autorización en consola y auxiliar", 14.5, INK, 700)
    s.text(520, 168, "VTY: login local + SSH  →  los usuarios de Active Directory no entran por SSH", 11.5, SOFT)

    chips = [
        ("Consola / AUX", "línea con AAA", RED),
        ("R1 / SW1", "cliente RADIUS", BLUE),
        ("NPS", "10.7.84.66:1812", VIOLET),
        ("AD DS", "p4.redes.local", TEAL),
        ("Privilegio", "0 · 5 · 10", GREEN),
    ]
    cw, gap, x0, y0, ch = 156, 26, 528, 190, 86
    for i, (title, sub, color) in enumerate(chips):
        x = x0 + i * (cw + gap)
        s.rect(x, y0, cw, ch, WHITE, color, 10, 1.6)
        s.rect(x, y0, cw, 6, color, None, 3)
        s.text(x + cw / 2, y0 + 40, title, 12.5, INK, 700, "middle")
        s.text(x + cw / 2, y0 + 60, sub, 10.5, MUTED, 400, "middle")
        if i < len(chips) - 1:
            s.arrow(x + cw + 4, y0 + ch / 2, x + cw + gap - 4, y0 + ch / 2, SOFT, 1.6)

    s.text(528, 312, "Access-Request (UDP 1812) → Access-Accept + Cisco-AV-Pair shell:priv-lvl=N → Eventos 6272/6273", 11, MUTED)
    s.text(528, 334, "Accounting exec/commands (UDP 1813) → registro de inicio, fin y comandos de nivel 15", 11, MUTED)
    s.text(528, 356, "Si NPS no responde (timeout 5 s): fallback local admin.p4 (nivel 15) en consola/auxiliar", 11, "#b45309", 600)

    # --- Servidor ---
    card(
        s, 1000, 420, 380, 262, VIOLET, "SRV1-P4", "Windows Server 2019/2022",
        [
            ("10.7.84.66/26 · GW 10.7.84.65", "VLAN 20"),
            ("AD DS + DNS · p4.redes.local", ""),
            ("NPS · RADIUS UDP 1812 / 1813", ""),
            ("GRP_NIVEL0 · GRP_NIVEL5 · GRP_NIVEL10", ""),
            ("Eventos 6272 / 6273 / 6274 + log", ""),
            ("NTP w32time (UDP 123)", ""),
            ("SSH cliente: admin.p4 → R1 / SW1", ""),
        ],
    )

    # --- Enlace de acceso ---
    s.path("M400,664 H1000", stroke=VIOLET, width=4, marker="arw")
    s.text(410, 652, "Gi0/2 · access · VLAN 20 · 10.7.84.64/26", 11, "#6d28d9", 600)

    # --- Segmentación ---
    s.rect(430, 430, 530, 182, PANEL, LINE, 12, 1.2)
    s.text(448, 458, "Segmentación L2 / L3", 13, INK, 700)
    vlans = [
        ("VLAN 10  ·  USUARIOS    10.7.84.0/26    GW .1", BLUE),
        ("VLAN 20  ·  SERVIDORES  10.7.84.64/26   GW .65", VIOLET),
        ("VLAN 99  ·  GESTIÓN     10.7.84.128/26  GW .129", GREEN),
        ("VLAN 999 ·  NATIVA      sin IP (parking)", SOFT),
    ]
    for i, (t, color) in enumerate(vlans):
        yy = 486 + i * 30
        s.rect(448, yy - 11, 8, 16, color, None, 2)
        s.text(466, yy, t, 11.2, "#334155", 400, family=MONO)

    # --- Tabla IP ---
    s.text(60, 698, "Plan de direccionamiento", 12, INK, 700)
    cols = [(60, 90), (150, 210), (360, 210), (570, 190), (760, 680)]
    heads = ["VLAN", "Nombre", "Subred", "Gateway", "Uso / dispositivo"]
    s.rect(60, 706, 1380, 34, INK, None, 6)
    for (x, w), h in zip(cols, heads):
        s.text(x + 14, 728, h, 11.5, WHITE, 700)
    rows = [
        ("10", "USUARIOS", "10.7.84.0/26", "10.7.84.1", "DHCP .20–.62 · puerto Gi0/3 para PC de prueba"),
        ("20", "SERVIDORES", "10.7.84.64/26", "10.7.84.65", "SRV1-P4 10.7.84.66 · AD DS + DNS + NPS"),
        ("99", "GESTION-AAA", "10.7.84.128/26", "10.7.84.129", "R1 .129 · SW1 .130 · tráfico RADIUS y SSH"),
        ("999", "NATIVA", "10.7.84.192/26", "—", "Parking: puertos no usados, sin hosts"),
    ]
    for i, row in enumerate(rows):
        yy = 740 + i * 32
        s.rect(60, yy, 1380, 32, WHITE if i % 2 == 0 else PANEL)
        for (x, w), val in zip(cols, row):
            s.text(x + 14, yy + 21, val, 11.5, "#334155", 400,
                   family=MONO if x >= 360 else SANS)
        s.line(60, yy + 32, 1440, yy + 32, "#e2e8f0", 1)

    s.text(60, 884, "Matrícula 2025-0784 → 10.7.84.0/24, segmentada en /26 · Diagrama generado por scripts/tools/generar_diagramas.py",
           10.5, SOFT)
    s.save("topologia.svg")


# ---------------------------------------------------------------------------
# 2. FLUJO AAA (secuencia)
# ---------------------------------------------------------------------------
def flujo_aaa():
    s = SVG(1400, 830)
    header(
        s,
        "Flujo AAA entre el administrador, los equipos Cisco y el servidor NPS",
        "Secuencia de autenticación, autorización y auditoría · Lab P4 · 2025-0784",
        "RADIUS · NPS",
        right=1340,
    )

    people = [
        ("Administrador", "consola / auxiliar", 150, INK),
        ("R1 / SW1", "cliente RADIUS", 400, BLUE),
        ("NPS", "10.7.84.66", 650, VIOLET),
        ("AD DS", "p4.redes.local", 900, TEAL),
        ("Auditoría", "Eventos + log", 1150, AMBER),
    ]
    for name, sub, x, color in people:
        s.rect(x - 95, 130, 190, 56, WHITE, color, 8, 1.6)
        s.rect(x - 95, 130, 190, 5, color, None, 2)
        s.text(x, 160, name, 13, INK, 700, "middle")
        s.text(x, 176, sub, 10, MUTED, 400, "middle")
        s.line(x, 186, x, 700, "#cbd5e1", 1.2, dash="4 5")

    # Fases
    phases = [("AUTENTICACIÓN", 205, 120, BLUE), ("AUTORIZACIÓN", 355, 120, VIOLET),
              ("AUDITORÍA", 505, 150, AMBER)]
    for label, y, h, color in phases:
        s.rect(36, y, 6, h, color, None, 3)
        s.add(f'<text x="30" y="{y + h/2}" font-family="{SANS}" font-size="9.5" '
              f'font-weight="700" fill="{color}" text-anchor="middle" '
              f'transform="rotate(-90 30 {y + h/2})" letter-spacing="1.5">{label}</text>')

    msgs = [
        (225, 150, 400, "1. login en consola/auxiliar (usuario + contraseña)", False, SOFT),
        (285, 400, 650, "2. Access-Request · UDP 1812 · NAS-IP .129 / .130", False, BLUE),
        (345, 650, 900, "3. valida credenciales y grupos del usuario", False, VIOLET),
        (405, 900, 650, "4. credenciales OK + GRP_NIVEL0 / 5 / 10", True, TEAL),
        (465, 650, 400, "5. Access-Accept + Cisco-AV-Pair shell:priv-lvl=N", True, VIOLET),
        (525, 400, 150, "6. prompt con privilegio N (0, 5 o 10)", True, BLUE),
        (590, 400, 650, "7. Accounting Start / Stop + comandos nivel 15 · UDP 1813", False, AMBER),
        (650, 650, 1150, "8. Evento 6272/6273/6274 + log de contabilidad", False, AMBER),
    ]
    for y, x1, x2, label, dashed, color in msgs:
        s.arrow(x1 + (8 if x2 > x1 else -8), y, x2 - (8 if x2 > x1 else -8), y,
                color, 1.7, "6 5" if dashed else None, "arw")
        mid = (x1 + x2) / 2
        wlabel = len(label) * 5.55 + 14
        s.rect(mid - wlabel / 2, y - 21, wlabel, 16, WHITE, None, 4)
        s.text(mid, y - 9, label, 10.6, "#334155", 600, "middle")

    s.rect(300, 700, 1000, 66, "#fffbeb", "#fcd34d", 10, 1.2)
    s.text(318, 726, "Escenario alterno — NPS sin respuesta (timeout 5 s)", 12, "#92400e", 700)
    s.text(318, 746, "El método RAD-P4 devuelve error y se usa el siguiente método: base local. admin.p4 (nivel 15) mantiene el acceso de emergencia por consola/auxiliar.",
           10.8, "#78350f")
    s.text(300, 800, "Los usuarios RADIUS nunca se validan en la VTY: el SSH usa login local y está restringido a 10.7.84.64/26.",
           10.5, SOFT)

    s.save("flujo_aaa.svg")


# ---------------------------------------------------------------------------
# 3. NIVELES DE PRIVILEGIO
# ---------------------------------------------------------------------------
def niveles():
    s = SVG(1400, 780)
    header(
        s,
        "Modelo de autorización: niveles de privilegio 0 / 5 / 10 / 15",
        "El grupo de Active Directory se traduce en el nivel efectivo del IOS · Lab P4 · 2025-0784",
        "Grupos AD → IOS",
        right=1340,
    )

    levels = [
        ("0", "Invitado", "GRP_NIVEL0 · RADIUS", RED,
         ["Sin comandos de configuración ni show", "Solo enable / disable / help / exit"]),
        ("5", "Monitoreo", "GRP_NIVEL5 · RADIUS", AMBER,
         ["show version · show ip interface brief", "ping · traceroute · show logging"]),
        ("10", "Operador", "GRP_NIVEL10 · RADIUS", BLUE,
         ["show running-config · show aaa servers", "configure terminal · write memory"]),
        ("15", "Administrador", "admin.p4 · LOCAL", GREEN,
         ["Todos los comandos", "SSH (VTY) y respaldo si NPS cae"]),
    ]
    for i, (num, title, src, color, cmds) in enumerate(levels):
        y = 128 + i * 146
        s.rect(60, y, 760, 128, WHITE, color, 12, 1.8)
        s.rect(60, y, 12, 128, color, None, 6)
        s.circle(128, y + 64, 34, "#f8fafc", color, 2.5)
        s.text(128, y + 74, num, 26, color, 700, "middle")
        s.text(182, y + 40, title, 18, INK, 700)
        s.text(182, y + 62, src, 11, color, 700)
        s.text(182, y + 90, cmds[0], 11.5, "#334155", 400, family=MONO)
        s.text(182, y + 110, cmds[1], 11.5, "#334155", 400, family=MONO)

    # Panel derecho
    s.rect(860, 128, 480, 596, PANEL, LINE, 14, 1.2)
    s.text(884, 160, "Quién puede hacer qué", 15, INK, 700)

    heads = ["Usuario", "Grupo", "Nivel", "Con/Aux", "SSH"]
    xs = [884, 1000, 1140, 1200, 1280]
    s.rect(880, 180, 440, 30, INK, None, 6)
    for x, h in zip(xs, heads):
        s.text(x + (6 if h != "Usuario" else 4), 200, h, 10.5, WHITE, 700,
               "middle" if h != "Usuario" else "start")

    users = [
        ("usr.nivel0", "GRP_NIVEL0", "0", "sí", "no", RED),
        ("usr.nivel5", "GRP_NIVEL5", "5", "sí", "no", AMBER),
        ("usr.nivel10", "GRP_NIVEL10", "10", "sí", "no", BLUE),
        ("admin.p4", "LOCAL", "15", "fallback", "sí", GREEN),
    ]
    for i, (u, g, n, con, ssh, color) in enumerate(users):
        yy = 210 + i * 34
        s.rect(880, yy, 440, 34, WHITE if i % 2 == 0 else "#f1f5f9")
        s.text(884, yy + 22, u, 11, "#334155", 400, family=MONO)
        s.text(1006, yy + 22, g, 10.5, color, 700, "middle")
        s.text(1146, yy + 22, n, 11.5, INK, 700, "middle")
        s.text(1206, yy + 22, con, 10.5, "#334155", 400, "middle")
        s.text(1286, yy + 22, ssh, 10.5, "#334155", 400, "middle")

    notes = [
        ("Regla de oro", GREEN, 380),
        ("El secreto de enable solo lo conoce el administrador.", MUTED, 406),
        ("Un usuario de nivel 10 no puede escalar sin ese secreto.", MUTED, 426),
        ("La VTY no usa RADIUS: los usuarios de AD no pueden entrar por SSH.", MUTED, 456),
        ("El SSH se limita a la VLAN de servidores (10.7.84.64/26).", MUTED, 476),
        ("Si NPS no responde, la consola cae al usuario local de nivel 15.", MUTED, 506),
        ("Toda sesión de consola/aux genera accounting (inicio, fin y", MUTED, 536),
        ("comandos de nivel 15).", MUTED, 556),
        ("Auditoría", AMBER, 586),
        ("NPS registra 6272 (concedido), 6273 (denegado) y", MUTED, 612),
        ("6274 (descartado).", MUTED, 632),
        ("El dispositivo registra intentos fallidos y exitosos.", MUTED, 662),
    ]
    for text_, color, y in notes:
        weight = 700 if color != MUTED else 400
        size = 12.5 if weight == 700 else 10.8
        s.text(884, y, text_, size, color, weight)

    s.text(60, 742, "El nivel efectivo lo devuelve el servidor RADIUS en el atributo shell:priv-lvl; el nivel 15 local es el respaldo de emergencia.",
           10.5, SOFT)
    s.save("niveles_privilegio.svg")


if __name__ == "__main__":
    topologia()
    flujo_aaa()
    niveles()
