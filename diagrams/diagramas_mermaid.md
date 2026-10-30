# Diagramas Mermaid

GitHub renderiza estos diagramas directamente. Las versiones SVG están en `diagrams/*.svg` y se usan
en el README y en la documentación.

## 1. Topología

```mermaid
flowchart TB
    subgraph RED["Red del laboratorio · 10.7.84.0/24"]
        direction TB
        R1["<b>R1-P4</b><br/>Router Cisco IOS<br/>Gi0/0.10 .1 · .20 .65 · .99 .129<br/>Cliente RADIUS"]
        SW1["<b>SW1-P4</b><br/>Switch L2<br/>SVI Vlan99 10.7.84.130<br/>Port-security · BPDU guard"]
        SRV["<b>SRV1-P4</b><br/>Windows Server 2019/2022<br/>10.7.84.66/26<br/>AD DS · DNS · NPS"]

        R1 ---|"Trunk 802.1Q · VLAN 10,20,99 · nativa 999"| SW1
        SW1 ---|"Access VLAN 20"| SRV
    end

    CON["Consola / AUX"] -.->|"AAA RADIUS"| R1
    CON -.->|"AAA RADIUS"| SW1
    ADM["Administrador<br/>SSH desde 10.7.84.64/26"] -->|"TCP 22 · login local"| R1
    ADM -->|"TCP 22 · login local"| SW1
    R1 -->|"UDP 1812/1813"| SRV
    SW1 -->|"UDP 1812/1813"| SRV
```

## 2. Secuencia AAA

```mermaid
sequenceDiagram
    autonumber
    participant A as Administrador
    participant C as R1 / SW1
    participant N as NPS 10.7.84.66
    participant D as AD DS p4.redes.local

    A->>C: login en consola / auxiliar
    C->>N: Access-Request (UDP 1812) · NAS-IP .129/.130
    N->>D: valida credenciales y grupos
    D-->>N: OK + GRP_NIVEL0 / 5 / 10
    N-->>C: Access-Accept + Cisco-AV-Pair shell:priv-lvl=N
    C-->>A: prompt con privilegio N
    C->>N: Accounting Start/Stop + comandos 15 (UDP 1813)
    N-->>N: Evento 6272/6273/6274 + log de contabilidad

    Note over C,N: Si NPS no responde (timeout 5 s)<br/>fallback local admin.p4 (nivel 15)
```

## 3. Decisión de autorización

```mermaid
flowchart LR
    U["Usuario escribe<br/>credenciales"] --> Q{"¿NPS responde?"}
    Q -->|"Sí"| G{"¿Grupo AD?"}
    G -->|"GRP_NIVEL0"| L0["shell:priv-lvl=0"]
    G -->|"GRP_NIVEL5"| L5["shell:priv-lvl=5"]
    G -->|"GRP_NIVEL10"| L10["shell:priv-lvl=10"]
    G -->|"Sin grupo"| DENY["Access-Reject"]
    Q -->|"No (timeout)"| LOCAL["Base local<br/>admin.p4 = nivel 15"]
    L0 --> P["Prompt con nivel efectivo"]
    L5 --> P
    L10 --> P
    LOCAL --> P
```
