"""
Gestión de modelos para la calculadora KIA PPM
Uso: python manage_models.py <comando> [argumentos]

Comandos disponibles:
  list-fs                         — Lista todos los modelos Full Service
  list-ul                         — Lista todos los modelos Unlimited
  list-ds                         — Lista todos los modelos 2 Servicios (DS)
  remove-fs  "MODELO|motor|trans|freq|fuel"
  remove-ul  "MODELO|motor|trans|freq|fuel|rango"   (o sin rango para eliminar todos)
  remove-ds  "Modelo|motor|trans|freq|fuel"
  add-fs     "MODELO|motor|trans|freq|fuel"  "Nombre Display Auto"
  add-ul     "MODELO|motor|trans|freq|fuel|rango"
  add-ds     "Modelo|motor|trans|freq|fuel"  "Par1" "Par2" ...

Ejemplos:
  python manage_models.py list-fs
  python manage_models.py remove-fs "NUEVO MODELO|1.6|MT|5K|"
  python manage_models.py add-fs "NUEVO MODELO|1.6|MT|5K|" "Nuevo Modelo 1.6 MT"
  python manage_models.py add-ul "NUEVO MODELO|1.6|MT|5K||20K - 50K"
  python manage_models.py remove-ul "VIEJO MODELO|1.6|MT|10K|"   (elimina todos los rangos)
"""
import re, base64, json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_PATH = r'c:\Users\ALEJANDRO AGUERO\calculadora ppm\data.js'

PAT_D  = re.compile(r"(var D=JSON\.parse\(decodeURIComponent\(escape\(atob\(')([^']+)('\)\)\)\))")
PAT_DS = re.compile(r"(var DS=JSON\.parse\(decodeURIComponent\(escape\(atob\(')([^']+)('\)\)\)\))")

# ── I/O helpers ──────────────────────────────────────────────────────────────

def load():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        raw = f.read()
    m_D  = PAT_D.search(raw)
    m_DS = PAT_DS.search(raw)
    if not m_D or not m_DS:
        sys.exit("ERROR: No se encontraron las variables D o DS en data.js")
    D  = json.loads(base64.b64decode(m_D.group(2)).decode('utf-8'))
    DS = json.loads(base64.b64decode(m_DS.group(2)).decode('utf-8'))
    return raw, D, DS, m_D, m_DS

def save(raw, D, DS, m_D, m_DS):
    def enc(o):
        return base64.b64encode(
            json.dumps(o, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        ).decode('ascii')
    hn = PAT_D.sub(lambda m: m.group(1) + enc(D)  + m.group(3), raw)
    hn = PAT_DS.sub(lambda m: m.group(1) + enc(DS) + m.group(3), hn)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        f.write(hn)
    print("data.js guardado correctamente.")

# ── Cascade rebuilders ───────────────────────────────────────────────────────

def rebuild_fs_cascade(D):
    """Reconstruye D.cascade desde D.precios_fs."""
    c = {}
    for key in D['precios_fs']:
        p = key.split('|')
        m, mo, t, f = p[0], p[1], p[2], p[3]
        fuel = p[4] if len(p) > 4 else ''
        c.setdefault(m, {}).setdefault(mo, {}).setdefault(t, {}).setdefault(f, set()).add(fuel)
    for m in c:
        for mo in c[m]:
            for t in c[m][mo]:
                for f in c[m][mo][t]:
                    c[m][mo][t][f] = sorted(c[m][mo][t][f])
    D['cascade'] = c

def rebuild_ul_cascade(D):
    """Reconstruye D.cascade_ul y D.ul_rangos desde D.precios_ul."""
    cu, ur = {}, {}
    for key in D['precios_ul']:
        p = key.split('|')
        m, mo, t, f, fuel = p[0], p[1], p[2], p[3], p[4]
        rango = p[5] if len(p) > 5 else ''
        cu.setdefault(m, {}).setdefault(mo, {}).setdefault(t, {}).setdefault(f, set()).add(fuel)
        base_key = '|'.join(p[:5])
        ur.setdefault(base_key, set()).add(rango)
    for m in cu:
        for mo in cu[m]:
            for t in cu[m][mo]:
                for f in cu[m][mo][t]:
                    cu[m][mo][t][f] = sorted(cu[m][mo][t][f])
    for k in ur:
        ur[k] = sorted(ur[k])
    D['cascade_ul'] = cu
    D['ul_rangos'] = ur

def rebuild_ds_cascade(DS):
    """Reconstruye DS.cascade desde DS.precios."""
    c = {}
    for key in DS['precios']:
        p = key.split('|')
        m, mo, t, f = p[0], p[1], p[2], p[3]
        fuel = p[4] if len(p) > 4 else ''
        c.setdefault(m, {}).setdefault(mo, {}).setdefault(t, {}).setdefault(f, set()).add(fuel)
    for m in c:
        for mo in c[m]:
            for t in c[m][mo]:
                for f in c[m][mo][t]:
                    c[m][mo][t][f] = sorted(c[m][mo][t][f])
    DS['cascade'] = c

# ── KM defaults por frecuencia ───────────────────────────────────────────────

KM_DEFAULTS = {
    '5K':  {'plan_20k': {'km': '5K - 20K',  'vigencia': '2 años', 'servicios': 4},
             'plan_30k': {'km': '5K - 30K',  'vigencia': '3 años', 'servicios': 6}},
    '10K': {'plan_20k': {'km': '5K - 20K',  'vigencia': '2 años', 'servicios': 4},
             'plan_30k': {'km': '5K - 30K',  'vigencia': '3 años', 'servicios': 6}},
    '15K': {'plan_20k': {'km': '15K - 30K - 45K',        'vigencia': '2 años', 'servicios': 3},
             'plan_30k': {'km': '15K - 30K - 45K - 60K', 'vigencia': '3 años', 'servicios': 4}},
}

# ── Comandos: LIST ───────────────────────────────────────────────────────────

def cmd_list_fs():
    _, D, _, _, _ = load()
    keys = sorted(D['precios_fs'].keys())
    print(f"Full Service — {len(keys)} modelos:\n")
    for k in keys:
        e = D['precios_fs'][k]
        p20 = e.get('plan_20k', {})
        p30 = e.get('plan_30k', {})
        ppm20 = p20.get('ppm', 0) or 0
        ppm30 = p30.get('ppm', 0) or 0
        disp = e.get('modelo_auto', k.split('|')[0])
        print(f"  {k}")
        print(f"    Display: {disp}")
        print(f"    Plan 20K: ppm={ppm20:.4f}   Plan 30K: ppm={ppm30:.4f}")

def cmd_list_ul():
    _, D, _, _, _ = load()
    keys = sorted(D['precios_ul'].keys())
    print(f"Unlimited — {len(keys)} entradas:\n")
    for k in keys:
        e = D['precios_ul'][k]
        ppm = e.get('ppm_usd', 0) or 0
        print(f"  {k}   ppm={ppm:.4f}   paquete={e.get('paquete','?')}")

def cmd_list_ds():
    _, _, DS, _, _ = load()
    keys = sorted(DS['precios'].keys())
    print(f"2 Servicios (DS) — {len(keys)} modelos:\n")
    for k in keys:
        e = DS['precios'][k]
        pares = list(e.keys())
        print(f"  {k}   pares: {', '.join(pares)}")

# ── Comandos: REMOVE ─────────────────────────────────────────────────────────

def cmd_remove_fs(key):
    raw, D, DS, m_D, m_DS = load()
    if key not in D['precios_fs']:
        sys.exit(f"ERROR: '{key}' no existe en precios_fs.")
    del D['precios_fs'][key]
    D['servicios_fs'].pop(key, None)
    rebuild_fs_cascade(D)
    save(raw, D, DS, m_D, m_DS)
    print(f"Eliminado de FS: {key}")

def cmd_remove_ul(key):
    raw, D, DS, m_D, m_DS = load()
    # Si la clave incluye rango (6 partes), eliminar solo esa entrada
    parts = key.split('|')
    if len(parts) >= 6 and parts[5]:
        if key not in D['precios_ul']:
            sys.exit(f"ERROR: '{key}' no existe en precios_ul.")
        del D['precios_ul'][key]
        D['servicios_ul'].pop(key, None)
        print(f"Eliminado de UL: {key}")
    else:
        # Eliminar todas las entradas del modelo (ignorar rango)
        prefix = '|'.join(parts[:5]) + '|'
        to_del = [k for k in D['precios_ul'] if k.startswith(prefix)]
        if not to_del:
            sys.exit(f"ERROR: Ninguna entrada UL empieza con '{prefix}'.")
        for k in to_del:
            del D['precios_ul'][k]
            D['servicios_ul'].pop(k, None)
            print(f"Eliminado de UL: {k}")
    rebuild_ul_cascade(D)
    save(raw, D, DS, m_D, m_DS)

def cmd_remove_ds(key):
    raw, D, DS, m_D, m_DS = load()
    if key not in DS['precios']:
        sys.exit(f"ERROR: '{key}' no existe en DS.precios.")
    del DS['precios'][key]
    rebuild_ds_cascade(DS)
    save(raw, D, DS, m_D, m_DS)
    print(f"Eliminado de DS: {key}")

# ── Comandos: ADD ────────────────────────────────────────────────────────────

def cmd_add_fs(key, display_name=None):
    raw, D, DS, m_D, m_DS = load()
    if key in D['precios_fs']:
        sys.exit(f"ERROR: '{key}' ya existe en precios_fs. Usa update_prices.py para actualizar precios.")
    parts = key.split('|')
    modelo, freq = parts[0], parts[3] if len(parts) > 3 else '5K'
    nombre = display_name or modelo
    defs = KM_DEFAULTS.get(freq, KM_DEFAULTS['5K'])
    D['precios_fs'][key] = {
        'modelo_auto': nombre,
        'plan_20k': {'ppm': 0, 'precio_usd': 0, 'km': defs['plan_20k']['km'], 'vigencia': defs['plan_20k']['vigencia'], 'servicios': defs['plan_20k']['servicios']},
        'plan_30k': {'ppm': 0, 'precio_usd': 0, 'km': defs['plan_30k']['km'], 'vigencia': defs['plan_30k']['vigencia'], 'servicios': defs['plan_30k']['servicios']},
    }
    rebuild_fs_cascade(D)
    save(raw, D, DS, m_D, m_DS)
    print(f"Agregado a FS: {key}  (display: {nombre})")
    print("IMPORTANTE: los precios son 0. Corre update_prices.py para poblar los precios desde el Excel.")

def cmd_add_ul(key):
    raw, D, DS, m_D, m_DS = load()
    if key in D['precios_ul']:
        sys.exit(f"ERROR: '{key}' ya existe en precios_ul.")
    parts = key.split('|')
    modelo = parts[0]
    motor  = parts[1] if len(parts) > 1 else ''
    trans  = parts[2] if len(parts) > 2 else ''
    freq   = parts[3] if len(parts) > 3 else '5K'
    rango  = parts[5] if len(parts) > 5 else '20K - 50K'
    nombre = f"{modelo}{' '+motor if motor else ''}{' '+trans if trans else ''} ({freq})"
    D['precios_ul'][key] = {
        'modelo_auto': nombre,
        'paquete':     f"UNLIMITED {rango.split('-')[-1].strip()}",
        'rango':       rango,
        'precio_usd':  0,
        'ppm_usd':     0,
        'descuento':   30,
        'recargo':     16.0,
        'cantidad_servicios': 3,
        'vigencia':    '2 años',
        'km':          rango.replace(' - ', ' - '),
    }
    rebuild_ul_cascade(D)
    save(raw, D, DS, m_D, m_DS)
    print(f"Agregado a UL: {key}")
    print("IMPORTANTE: los precios son 0. Corre update_prices.py para poblar los precios desde el Excel.")

def cmd_add_ds(key, *pares):
    raw, D, DS, m_D, m_DS = load()
    if key in DS['precios']:
        sys.exit(f"ERROR: '{key}' ya existe en DS.precios.")
    if not pares:
        sys.exit("ERROR: debes indicar al menos un par, ej: \"20K-50K\" \"30K-60K\"")
    # Acepta pares separados por coma o como argumentos individuales
    pares_flat = []
    for p in pares:
        for sub in p.split(','):
            sub = sub.strip()
            if sub:
                pares_flat.append(sub)
    pares = pares_flat
    DS['precios'][key] = {par: {'ppm': 0, 'regular': 0} for par in pares}
    rebuild_ds_cascade(DS)
    save(raw, D, DS, m_D, m_DS)
    print(f"Agregado a DS: {key}  pares: {list(pares)}")
    print("IMPORTANTE: los precios son 0. Corre update_prices.py para poblar los precios desde el Excel.")

# ── Main ─────────────────────────────────────────────────────────────────────

USAGE = __doc__

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(USAGE); sys.exit(0)
    cmd = args[0]
    if   cmd == 'list-fs':   cmd_list_fs()
    elif cmd == 'list-ul':   cmd_list_ul()
    elif cmd == 'list-ds':   cmd_list_ds()
    elif cmd == 'remove-fs':
        if len(args) < 2: sys.exit("Uso: python manage_models.py remove-fs \"CLAVE\"")
        cmd_remove_fs(args[1])
    elif cmd == 'remove-ul':
        if len(args) < 2: sys.exit("Uso: python manage_models.py remove-ul \"CLAVE\"")
        cmd_remove_ul(args[1])
    elif cmd == 'remove-ds':
        if len(args) < 2: sys.exit("Uso: python manage_models.py remove-ds \"CLAVE\"")
        cmd_remove_ds(args[1])
    elif cmd == 'add-fs':
        if len(args) < 2: sys.exit("Uso: python manage_models.py add-fs \"CLAVE\" \"Nombre Display\"")
        cmd_add_fs(args[1], args[2] if len(args) > 2 else None)
    elif cmd == 'add-ul':
        if len(args) < 2: sys.exit("Uso: python manage_models.py add-ul \"CLAVE|con|rango\"")
        cmd_add_ul(args[1])
    elif cmd == 'add-ds':
        if len(args) < 3: sys.exit("Uso: python manage_models.py add-ds \"CLAVE\" \"Par1\" \"Par2\"")
        cmd_add_ds(args[1], *args[2:])
    else:
        print(f"Comando desconocido: '{cmd}'\n")
        print(USAGE)
        sys.exit(1)
