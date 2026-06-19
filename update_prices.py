import re, base64, json, openpyxl, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

EXCEL_PATH = r'c:\Users\ALEJANDRO AGUERO\calculadora ppm\Planes MPP KIA - Postventa.xlsx'
HTML_PATH  = r'c:\Users\ALEJANDRO AGUERO\calculadora ppm\index.html'   # solo para referencia
DATA_PATH  = r'c:\Users\ALEJANDRO AGUERO\calculadora ppm\data.js'
DISC_FS_UL = 0.30
DISC_DUO   = 0.25

def fmt_motor(m):
    if m is None: return ''
    try: return f'{float(m):.1f}'
    except: return str(m)
def safe(s): return '' if s is None else str(s)
def normalize(s):
    s = str(s).upper().replace('(','').replace(')','')
    return ' '.join(s.split())
HTML_TO_EXCEL_MODEL = {
    'EV9 OV':        'EV9 MV',
    'TASMAN TK 4WD': 'TASMAN TK',
}
def resolve_model(raw):
    n = normalize(raw)
    return HTML_TO_EXCEL_MODEL.get(n, n)
def fuel_suffix(c):
    c = str(c).strip() if c else ''
    return c if c in ('GLP','GNV') else ''
def pair_key(h): return str(h).replace(' ','')

wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
FS_SHEET_CFG = {
    '5K':  {'fs':{'5K - 20K':'plan_20k','5K - 30K':'plan_30k'},'ul':{'20K - 50K','30K - 50K','30K - 60K','40K - 60K'}},
    '10K': {'fs':{'5K - 20K':'plan_20k','5K - 30K':'plan_30k'},'ul':{'20K - 50K','30K - 50K','30K - 60K','40K - 60K'}},
    '15K': {'fs':{'15K - 45K':'plan_20k','15K - 60K':'plan_30k'},'ul':{'30K - 60K','45K - 75K','60K - 90K','75K - 105K'}},
}
excel_fs_data = {}
excel_ul_data = {}
for sn, cfg in FS_SHEET_CFG.items():
    ws = wb[sn]
    hdr = [safe(c.value).strip() for c in ws[3]]
    col = {h:i for i,h in enumerate(hdr) if h}
    for row in ws.iter_rows(min_row=4, values_only=True):
        if row[0] is None: continue
        modelo=safe(row[1]); mstr=fmt_motor(row[2]); trans=safe(row[3])
        freq=safe(row[4]); comb=safe(row[5])
        if not modelo: continue
        key=(normalize(modelo),mstr,trans,freq,fuel_suffix(comb))
        fsp={};  
        for hc,pid in cfg['fs'].items():
            ci=col.get(hc)
            if ci is not None and row[ci] is not None: fsp[pid]=float(row[ci])
        if fsp: excel_fs_data[key]=fsp
        ulp={}
        for rh in cfg['ul']:
            ci=col.get(rh)
            if ci is not None and row[ci] is not None: ulp[rh]=float(row[ci])
        if ulp: excel_ul_data.setdefault(key,[]).append(ulp)
excel_duo_data = {}
for sn in ('5K DUO','10K DUO','15K DUO'):
    ws=wb[sn]; hdr=[safe(c.value).strip() for c in ws[3]]; col={h:i for i,h in enumerate(hdr) if h}
    pcols=[(h,i) for h,i in col.items() if '-' in h and 'K' in h.upper()]
    for row in ws.iter_rows(min_row=4,values_only=True):
        if row[0] is None: continue
        modelo=safe(row[1]); motor=fmt_motor(row[2]); trans=safe(row[3])
        freq=safe(row[4]); comb=safe(row[5])
        if not modelo: continue
        key=(modelo.lower(),motor,trans.lower(),freq,comb.lower())
        prices={pair_key(hc):float(row[ci]) for hc,ci in pcols if ci<len(row) and row[ci] is not None}
        if prices: excel_duo_data[key]=prices
with open(DATA_PATH,'r',encoding='utf-8') as f: html=f.read()
PAT_D =re.compile(r"(var D=JSON\.parse\(decodeURIComponent\(escape\(atob\(')([^']+)('\)\)\)\))")
PAT_DS=re.compile(r"(var DS=JSON\.parse\(decodeURIComponent\(escape\(atob\(')([^']+)('\)\)\)\))")
m_D=PAT_D.search(html); m_DS=PAT_DS.search(html)
def decode_b64(s): return json.loads(base64.b64decode(s).decode('utf-8'))
def encode_b64(o):
    raw=json.dumps(o,ensure_ascii=False,separators=(',',':'))
    return base64.b64encode(raw.encode('utf-8')).decode('ascii')
D=decode_b64(m_D.group(2)); DS=decode_b64(m_DS.group(2))
anf=[]; apu=[]; ufs=uul=uds=0
for hk,entry in D['precios_fs'].items():
    p=hk.split('|'); en=resolve_model(p[0] if p else '')
    key=(en,p[1] if len(p)>1 else '',p[2] if len(p)>2 else '',p[3] if len(p)>3 else '',p[4] if len(p)>4 else '')
    if key not in excel_fs_data: anf.append(f'[FS] {hk}'); continue
    for pid in ('plan_20k','plan_30k'):
        if pid in excel_fs_data[key] and pid in entry:
            old=entry[pid].get('ppm',0) or 0; new=round(excel_fs_data[key][pid],4)
            if old>0 and new>old: apu.append(f'[FS] {hk}/{pid}: {old:.2f}->{new:.2f}')
            entry[pid]['ppm']=new; entry[pid]['precio_usd']=round(new/(1-DISC_FS_UL),4); ufs+=1
# Rename DS Sorento (UM) 3.5 AT -> Sorento (UM) AWD (Excel 10K DUO fila 52 es AWD)
old_k='Sorento (UM)|3.5|AT|10K|Gasolina'; new_k='Sorento (UM) AWD|3.5|AT|10K|Gasolina'
if old_k in DS['precios']: DS['precios'][new_k]=DS['precios'].pop(old_k)
# Crear nuevas entradas UL 15K desde Excel (modelos no existentes en HTML)
UL_15K_NMODEL_MAP={'SPORTAGE NQ5 HEV':'SPORTAGE NQ5 (HEV)','NIRO DE HEV':'NIRO DE (HEV)','NIRO SG2 HEV':'NIRO SG2 (HEV)','NIRO SG2 EV':'NIRO SG2 (EV)','EV5 OV':'EV5 (OV)','EV9 MV':'EV9 (OV)'}
UL_15K_META={'30K - 60K':('UNLIMITED 60K','30K - 45K - 60K'),'45K - 75K':('UNLIMITED 75K','45K - 60K - 75K'),'60K - 90K':('UNLIMITED 90K','60K - 75K - 90K'),'75K - 105K':('UNLIMITED 105K','75K - 90K - 105K')}
# Eliminar entradas 15K con rangos incorrectos antes del loop UL
old_15k_rangos={'20K - 50K','30K - 50K','40K - 60K'}
old_15k_del=[k for k in list(D['precios_ul']) if k.split('|')[3:4]==['15K'] and k.split('|')[5:6] and k.split('|')[5] in old_15k_rangos]
for k in old_15k_del: del D['precios_ul'][k]
for hk,entry in D['precios_ul'].items():
    p=hk.split('|'); hmodel=p[0] if p else ''; hmotor=p[1] if len(p)>1 else ''
    htrans=p[2] if len(p)>2 else ''; hfreq=p[3] if len(p)>3 else ''
    hfuel=p[4] if len(p)>4 else ''; hrango=p[5] if len(p)>5 else ''
    en=resolve_model(hmodel)
    key=(en,hmotor,htrans,hfreq,hfuel)
    if key not in excel_ul_data: anf.append(f'[UL] {hk}'); continue
    ul=excel_ul_data[key][0]
    if hrango not in ul: anf.append(f'[UL rango] {hk}'); continue
    old=entry.get('ppm_usd',0) or 0; new=round(ul[hrango],4)
    if old>0 and new>old: apu.append(f'[UL] {hk}: {old:.2f}->{new:.2f}')
    entry['ppm_usd']=new; entry['precio_usd']=round(new/(1-DISC_FS_UL),4); uul+=1
added_15k=[]
for (em,emot,etrans,efreq,efuel),ul_list in excel_ul_data.items():
    if efreq!='15K' or em not in UL_15K_NMODEL_MAP: continue
    hmodel=UL_15K_NMODEL_MAP[em]; ul=ul_list[0]
    for rango,(paquete,km) in UL_15K_META.items():
        if rango not in ul: continue
        ppm=round(ul[rango],4)
        hkey=f'{hmodel}|{emot}|{etrans}|15K||{rango}'
        if hkey in D['precios_ul']: continue
        mparts=[hmodel.replace('(','').replace(')','').strip()]
        if emot: mparts.append(emot)
        if etrans: mparts.append(etrans)
        D['precios_ul'][hkey]={'modelo_auto':f"{' '.join(mparts)} (15K)",'paquete':paquete,'rango':rango,'precio_usd':round(ppm/(1-DISC_FS_UL),4),'ppm_usd':ppm,'descuento':30,'recargo':16.0,'cantidad_servicios':3,'vigencia':'2 años','km':km}
        added_15k.append(hkey); uul+=1
for hk,pe in DS['precios'].items():
    p=hk.split('|')
    key=(p[0].lower() if p else '',p[1] if len(p)>1 else '',p[2].lower() if len(p)>2 else '',p[3] if len(p)>3 else '',p[4].lower() if len(p)>4 else '')
    if key not in excel_duo_data: anf.append(f'[DS] {hk}'); continue
    np_=excel_duo_data[key]
    for pid,pd in pe.items():
        if pid not in np_: continue
        old=pd.get('ppm',0) or 0; new=round(np_[pid],4)
        if old>0 and new>old: apu.append(f'[DS] {hk}/{pid}: {old:.2f}->{new:.2f}')
        pd['ppm']=new; pd['regular']=round(new/(1-DISC_DUO),4); uds+=1
nb64D=encode_b64(D); nb64DS=encode_b64(DS)
hn=PAT_D.sub(lambda m:m.group(1)+nb64D+m.group(3),html)
hn=PAT_DS.sub(lambda m:m.group(1)+nb64DS+m.group(3),hn)
with open(DATA_PATH,'w',encoding='utf-8') as f: f.write(hn)
sep='='*70
print(sep); print('ACTUALIZACION DE PRECIOS PPM -- RESUMEN'); print(sep)
print(f'  FS actualizados : {ufs}')
print(f'  UL actualizados : {uul}')
print(f'  DS actualizados : {uds}')
if old_15k_del:
    print(); print(f'[INFO] UL 15K RANGOS INCORRECTOS ELIMINADOS ({len(old_15k_del)}):')
    [print(f'  {z}') for z in old_15k_del]
if added_15k:
    print(); print(f'[INFO] UL 15K NUEVAS ENTRADAS CREADAS ({len(added_15k)}):')
    [print(f'  {z}') for z in added_15k]
print(); [print(f'  {a}') for a in apu] if apu else print('[OK] Ningun precio subio.')
if apu: print(f'  ({len(apu)} casos de precios que subieron)')
print()
if anf:
    print(f'[ALERTA] SIN PRECIO EN EXCEL ({len(anf)} casos):')
    [print(f'  {a}') for a in anf]
else:
    print('[OK] Todos los modelos tienen precio en el Excel.')
print(); print('data.js actualizado exitosamente.')