#!/usr/bin/env python3
"""Extrae ventanas de transcripcion alrededor de un termino, con marca de tiempo."""
import json,sys,re,unicodedata,os
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def norm(s):
    s=unicodedata.normalize('NFKD',(s or '').lower())
    s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]+',' ',s)).strip()
def cargar(vid):
    d=json.load(open(f'{BASE}/transcripts/{vid}.es.json3'))
    seg=[]
    for e in d['events']:
        if 'segs' not in e: continue
        t=''.join(s['utf8'] for s in e['segs']).replace('\n',' ')
        if t.strip(): seg.append((e['tStartMs']//1000, re.sub(r'\s+',' ',t).strip()))
    return seg
def texto(seg): return ' '.join(t for _,t in seg)
if __name__=='__main__':
    vid,term=sys.argv[1],sys.argv[2]
    win=int(sys.argv[3]) if len(sys.argv)>3 else 700
    seg=cargar(vid); full=texto(seg); fn=norm(full)
    # mapa posicion->timestamp
    pos=0; marcas=[]
    for ts,t in seg:
        marcas.append((len(norm(full[:pos+len(t)])),ts)); pos+=len(t)+1
    tn=norm(term)
    for m in re.finditer(re.escape(tn),fn):
        ts=next((s for p,s in marcas if p>=m.start()),0)
        a=max(0,m.start()-win); b=min(len(fn),m.end()+win)
        print(f"\n--- [{ts//60:02d}:{ts%60:02d}] ---\n...{fn[a:b]}...")
