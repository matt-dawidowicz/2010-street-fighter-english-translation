from pathlib import Path
import hashlib

ROOT=Path('/mnt/data')
DEBUG_IN=ROOT/'Street_Fighter_2010_Translation_DEBUG_v8_DialogueSystemFix.nes'
NORMAL_IN=ROOT/'Street_Fighter_2010_Translation_RC4_DialogueSystemFix.nes'
DEBUG_OUT=ROOT/'Street_Fighter_2010_Translation_DEBUG_v9_FinalProsePass.nes'
NORMAL_OUT=ROOT/'Street_Fighter_2010_Translation_RC5_FinalProsePass.nes'
DEBUG_IPS=ROOT/'Street_Fighter_2010_DEBUG_v8_to_v9_FinalProsePass.ips'
NORMAL_IPS=ROOT/'Street_Fighter_2010_RC4_to_RC5_FinalProsePass.ips'
SCRIPT_OUT=ROOT/'street-fighter-2010-v9-final-script.txt'
AUDIT_OUT=ROOT/'street-fighter-2010-v9-layout-audit.txt'
NOTES_OUT=ROOT/'street-fighter-2010-v9-translation-notes.txt'

JP=ROOT/'Street Fighter 2010 (Japan)(4).nes'
TEXT_BANK=0x20010
TEXT_CPU=0x8000
CORPUS_CLEAR_END=0x2095E
PTR_ACTIVE=0x152A0
PTR_COPY=0x212A0
PTR_LEN=42
CRAWL_START=0x14A84
CRAWL_END=0x14C15
LEGACY_LINE=0x16E57
LEGACY_LEN=19
F7=0xF7; F8=0xF8; FA=0xFA; FB=0xFB; FC=0xFC; FE=0xFE; FF=0xFF
ELLIPSIS=0x88

enc={chr(ord('A')+i):0x0A+i for i in range(26)}
enc.update({str(i):i for i in range(10)})
enc.update({' ':0x24,'.':0x8E,',':0x8D,'-':0x8F,'?':0x89,'!':0x8A})

records={
0:[('KEVIN...',True,True),('WHO ARE YOU?!',True,True),("... BALLANTINE-TYPE MX-5... A CYBORG BUILT BY THE GALAXY POLICE... DO YOU REALLY BELIEVE THAT'S WHAT YOU ARE?",True,True),('WHAT DID YOU SAY...?',True,True)],
5:[('KEVIN...',True,True),('YOU BASTARD!',True,True),("GO TO DAGOBAH, THE DESERT PLANET. I'VE HIDDEN A FLIP SHIELD GENERATOR THERE. EQUIP IT, AND YOU'LL BE ONE STEP CLOSER TO PERFECTION...",True,True)],
6:[("WHY...? EVERY TIME I'M HIT, IT FEELS LIKE SOMETHING IS CRAWLING AROUND INSIDE ME... WHY WOULD I, A CYBORG, FEEL PAIN?!",True,True)],
7:[("DOES IT HURT, KEVIN...? THAT PAIN PROVES YOU'RE NOT A CYBORG. COME TO MASSINI, THE MACHINE PLANET. ...I'LL ERASE THAT PAIN...",True,True)],
8:[('WELCOME, MY GREATEST MASTERPIECE, KEVIN.',True,True)],
9:[('YOUR GREATEST MASTERPIECE...?',True,True)],
10:[("THAT'S RIGHT. OF ALL THE PARASITES CREATED BY DR. JOSE, YOU ARE THE GREATEST.",True,False)],
11:[("...IF THE GALAXY POLICE HADN'T STORMED IN BEFORE I COULD ATTACH THE ARMORED INSECT TO YOUR HEAD, YOU WOULD HAVE BECOME MY LOYAL SERVANT...",False,True)],
12:[('ME... A PARASITE...?',True,True)],
13:[("THAT'S RIGHT. THE CREATURE IN YOUR ARMOR HAS CRAWLED INTO EVERY PORE OF YOUR BODY AND IS NOW CRAWLING AROUND INSIDE YOU.",True,True),('...',True,True)],
14:[("BUT YOU ARE NO LONGER THE GREATEST. I HAVE CREATED AN ARMORED INSECT THAT EVEN YOU ARE NO MATCH FOR!",True,True)],
15:[('ME... A PARASITE...? ...',True,True),('MX-5, MX-5. THIS IS THE GALAXY POLICE. YOUR MISSION IS COMPLETE. YOUR NEXT ASSIGNMENT FOLLOWS. A CYBORG TERRORIST HAS STRUCK ON EARTH. ARREST OR DESTROY THE PERPETRATOR.',True,True),('...',True,True)],
16:[('MX-5, READ BACK YOUR ORDERS!',True,True)],
17:[("...I READ YOU. I'M ON MY WAY...",True,True)],
18:[('MX-5, YOU ARE ORDERED TO EXTERMINATE THE PARASITES. LOCATE THE TARGET PARASITE AND DESTROY IT TO BUILD UP OPEN POWER FOR THE DIMENSIONAL DOOR. HOWEVER, OPEN POWER DROPS TO ZERO TEN SECONDS AFTER THE DOOR OPENS. IF THAT HAPPENS, YOUR BODY WILL VANISH... BE CAREFUL, KEVIN.',True,True)],
19:[('...',True,True)],
20:[("KEVIN! LET ME TEST IT ON YOUR BODY!",True,True)],
}

sep_kind={0:['fb','fb','fb'],5:['fb','fb'],13:['double'],15:['fb','fb']}
JP_SKELETON={0:(4,4,3),5:(3,3,2),6:(1,1,0),7:(1,1,0),8:(1,1,0),9:(1,1,0),10:(1,0,0),11:(0,1,0),12:(1,1,0),13:(2,2,0),14:(1,1,0),15:(3,3,2),16:(1,1,0),17:(1,1,0),18:(1,1,0),19:(1,1,0),20:(1,1,0)}

crawl_lines=['AS HUMANITY SOUGHT NEW','FRONTIERS, PEOPLE BEGAN','SETTLING OTHER PLANETS.','IN A SOCIETY OF HUMANS','AND ALIENS, CRIME GREW','EVER MORE BRUTAL.','MANY CRIMINALS TURNED','THEMSELVES INTO CYBORGS','AND GAINED GREAT POWER.','BUT IN A.D. 2010,','PARASITES EMERGED, MORE','VICIOUS AND DESTRUCTIVE','THAN CYBORGS. THEY FUSE','WITH ARMORED INSECTS TO','GAIN ENORMOUS POWER.']


def tile_width(s):
    n=0; i=0
    while i<len(s):
        if s.startswith('...',i): n+=1; i+=3
        else: n+=1; i+=1
    return n


def encode_text(s):
    out=bytearray(); i=0
    while i<len(s):
        if s.startswith('...',i): out.append(ELLIPSIS); i+=3; continue
        c=s[i]
        if c=="'": out.append(FC); i+=1; continue
        if c not in enc: raise RuntimeError(f'unsupported char {c!r} in {s!r}')
        out.append(enc[c]); i+=1
    return out


def wrap_text(s,cap=23):
    words=s.split(' '); lines=[]; cur=''
    for w in words:
        cand=w if not cur else cur+' '+w
        if tile_width(cand)<=cap: cur=cand
        else:
            if not cur or tile_width(w)>cap: raise RuntimeError(f'cannot wrap safely: {w!r} in {s!r}')
            lines.append(cur); cur=w
    if cur: lines.append(cur)
    if len(lines)==1 and tile_width(lines[0])+2>24: return wrap_text(s,22)
    return lines


def encode_group(text,open_q,close_q):
    lines=wrap_text(text); out=bytearray()
    if open_q: out.append(F7)
    for li,line in enumerate(lines):
        out+=encode_text(line)
        if li+1<len(lines): out.append(FE)
    if close_q: out.append(F8)
    return out,lines


def build_raw_record(idx):
    out=bytearray(); wrapped=[]; groups=records[idx]
    for gi,(text,oq,cq) in enumerate(groups):
        gb,lines=encode_group(text,oq,cq); out+=gb; wrapped.append(lines)
        if gi+1<len(groups):
            kind=sep_kind[idx][gi]
            if kind=='fb': out+=bytes([FE,FB,FE])
            elif kind=='double': out+=bytes([FE,FE])
            else: raise RuntimeError(kind)
    return out,wrapped


def insert_scroll_after_fifth_fe(raw,pre_fe=0):
    total=pre_fe+raw.count(FE)
    if total<=5: return bytearray(raw),False
    out=bytearray(); n=pre_fe; inserted=False
    for x in raw:
        out.append(x)
        if x==FE:
            n+=1
            if n==5: out.append(FA); inserted=True
    if not inserted: out=bytearray([FA])+out; inserted=True
    return out,inserted


def rendered_widths(stream):
    widths=[]; w=0
    for x in stream:
        if x==FF: break
        if x==FE: widths.append(w); w=0
        elif x in (FA,FB): pass
        else: w+=1
    widths.append(w); return widths


def build_records():
    built={}; wrapped_by={}; scroll_by={}
    for idx in records:
        if idx in (10,11): continue
        raw,wrapped=build_raw_record(idx); st,scroll=insert_scroll_after_fifth_fe(raw); st.append(FF)
        built[idx]=bytes(st); wrapped_by[idx]=wrapped; scroll_by[idx]=scroll
    r10,w10=build_raw_record(10); r11,w11=build_raw_record(11)
    s10,_=insert_scroll_after_fifth_fe(r10); assert s10.count(FA)==0
    s11,scroll11=insert_scroll_after_fifth_fe(r11,pre_fe=r10.count(FE))
    built[10]=bytes(s10+bytes([FF])); wrapped_by[10]=w10; scroll_by[10]=False
    built[11]=bytes(s11+bytes([FF])); wrapped_by[11]=w11; scroll_by[11]=scroll11
    for idx,b in built.items():
        f7,f8,fb=JP_SKELETON[idx]; assert (b.count(F7),b.count(F8),b.count(FB))==(f7,f8,fb); assert max(rendered_widths(b))<=24
    return built,wrapped_by,scroll_by

BUILT,WRAPPED,SCROLL=build_records()


def pack_records():
    blob=bytearray(); ptrs=[None]*21; offsets={}
    for idx in [0,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]:
        cpu=TEXT_CPU+len(blob)
        if cpu>=0xA000: raise RuntimeError('corpus overflow')
        offsets[idx]=(cpu,len(blob),len(BUILT[idx]))
        if idx==0:
            for i in range(5): ptrs[i]=cpu
        else: ptrs[idx]=cpu
        blob+=BUILT[idx]
    assert all(p is not None for p in ptrs); assert len(blob)<0x1000
    return bytes(blob),ptrs,offsets

BLOB,PTRS,OFFSETS=pack_records(); PTR_BYTES=b''.join(int(p).to_bytes(2,'little') for p in PTRS); assert len(PTR_BYTES)==PTR_LEN

crawl=bytearray()
for line in crawl_lines:
    assert tile_width(line)<24; crawl+=encode_text(line); crawl.append(FE)
crawl+=bytes([FE,FF]); assert crawl.count(FE)==16; assert crawl[-3:]==bytes([FE,FE,FF]); assert len(crawl)<=CRAWL_END-CRAWL_START

jp=JP.read_bytes(); jp_off=0x156A0; jp_crawl=bytearray()
for x in jp[jp_off:jp_off+0x400]:
    jp_crawl.append(x)
    if x==FF: break
assert jp_crawl.count(FE)==16
cur=0; jp_widths=[]
for x in jp_crawl:
    if x==FE: jp_widths.append(cur); cur=0
    elif x==FF: break
    else: cur+=1
assert len(jp_widths)==16 and jp_widths[-1]==0 and max(jp_widths[:-1])<24


def patch_rom(src,out):
    original=src.read_bytes()
    if len(original)!=393232: raise RuntimeError((src,len(original)))
    b=bytearray(original)
    b[TEXT_BANK:CORPUS_CLEAR_END]=bytes(CORPUS_CLEAR_END-TEXT_BANK)
    b[TEXT_BANK:TEXT_BANK+len(BLOB)]=BLOB
    b[PTR_ACTIVE:PTR_ACTIVE+PTR_LEN]=PTR_BYTES
    b[PTR_COPY:PTR_COPY+PTR_LEN]=PTR_BYTES
    b[CRAWL_START:CRAWL_END]=crawl+bytes(CRAWL_END-CRAWL_START-len(crawl))
    assert all(x==0x24 for x in b[LEGACY_LINE:LEGACY_LINE+LEGACY_LEN])
    assert bytes(b[PTR_ACTIVE:PTR_ACTIVE+PTR_LEN])==PTR_BYTES
    assert bytes(b[PTR_COPY:PTR_COPY+PTR_LEN])==PTR_BYTES
    assert PTRS[:5]==[PTRS[0]]*5
    for idx,p in enumerate(PTRS):
        off=TEXT_BANK+(p-TEXT_CPU); assert TEXT_BANK<=off<TEXT_BANK+len(BLOB); end=b.index(FF,off,TEXT_BANK+len(BLOB)+1)+1; rec=bytes(b[off:end]); srcidx=0 if 1<=idx<=4 else idx; f7,f8,fb=JP_SKELETON[srcidx]; assert (rec.count(F7),rec.count(F8),rec.count(FB))==(f7,f8,fb); assert max(rendered_widths(rec))<=24
    c=bytes(b[CRAWL_START:CRAWL_START+len(crawl)]); assert c==bytes(crawl) and c.count(FE)==16 and c[-3:]==bytes([FE,FE,FF])
    assert b[0x17064]==0x24 and b[0x17263]==0x24
    if 'DEBUG' in src.name:
        helper=bytes([0xA9,0x0A,0x85,0xB2,0xA5,0xAD,0x29,0xF9,0x60])
        for bank in [0x1C010,0x3C010]:
            assert bytes(b[bank+0x1B4:bank+0x1B4+9])==helper
            assert bytes(b[bank+0x27B:bank+0x27B+4])==bytes([0x20,0xB4,0xC1,0xEA])
        assert b[0x1801E]==0x09
        for off in [0x1D4C6,0x1D4DC,0x3D4C6,0x3D4DC]: assert b[off]==0x00
    allowed=set(range(TEXT_BANK,CORPUS_CLEAR_END)); allowed.update(range(PTR_ACTIVE,PTR_ACTIVE+PTR_LEN)); allowed.update(range(PTR_COPY,PTR_COPY+PTR_LEN)); allowed.update(range(CRAWL_START,CRAWL_END))
    changed=[i for i,(x,y) in enumerate(zip(original,b)) if x!=y]; bad=[i for i in changed if i not in allowed]; assert not bad
    out.write_bytes(b); return original,bytes(b),changed


def make_ips(old,new,path):
    assert len(old)==len(new); out=bytearray(b'PATCH'); i=0
    while i<len(old):
        if old[i]==new[i]: i+=1; continue
        s=i
        while i<len(old) and old[i]!=new[i] and i-s<0xFFFF: i+=1
        data=new[s:i]; out+=s.to_bytes(3,'big')+len(data).to_bytes(2,'big')+data
    out+=b'EOF'; path.write_bytes(out)


def apply_ips(old,patch):
    p=patch.read_bytes(); assert p[:5]==b'PATCH'; out=bytearray(old); i=5
    while p[i:i+3]!=b'EOF':
        off=int.from_bytes(p[i:i+3],'big'); n=int.from_bytes(p[i+3:i+5],'big'); i+=5
        if n: out[off:off+n]=p[i:i+n]; i+=n
        else:
            rlen=int.from_bytes(p[i:i+2],'big'); val=p[i+2]; i+=3; out[off:off+rlen]=bytes([val])*rlen
    return bytes(out)

old_d,new_d,chg_d=patch_rom(DEBUG_IN,DEBUG_OUT); old_n,new_n,chg_n=patch_rom(NORMAL_IN,NORMAL_OUT)
make_ips(old_d,new_d,DEBUG_IPS); make_ips(old_n,new_n,NORMAL_IPS); assert apply_ips(old_d,DEBUG_IPS)==new_d; assert apply_ips(old_n,NORMAL_IPS)==new_n

script=['STREET FIGHTER 2010 - FINAL PROSE PASS V9','','OPENING CRAWL',*crawl_lines,'','DIALOGUE']
for idx in range(21):
    srcidx=0 if 1<=idx<=4 else idx; script.append(f'RECORD {idx:02d}' + (' (aliases record 00)' if 1<=idx<=4 else ''))
    if idx==srcidx:
        for text,_,_ in records[srcidx]: script.append(text)
    script.append('')
SCRIPT_OUT.write_text('\n'.join(script),encoding='utf-8')

audit=['STREET FIGHTER 2010 - V9 LAYOUT AUDIT','',f'Packed dialogue corpus: {len(BLOB)} bytes, CPU $8000-${TEXT_CPU+len(BLOB)-1:04X}',f'Opening crawl: {len(crawl)} bytes; 15 visible rows + 1 empty row; FE count={crawl.count(FE)}','All crawl rows are <24 tiles; dialogue rows are <=24 tiles including quote controls.','F7/F8/FB counts remain matched to the original Japanese record skeleton.','Renderer/CHR/cursor/gameplay/debug code are unchanged from v8/RC4 bases.','','CRAWL WIDTHS']
for row in crawl_lines: audit.append(f'[{tile_width(row):2d}] {row}')
audit.append('')
for idx in range(21):
    srcidx=0 if 1<=idx<=4 else idx; rec=BUILT[srcidx]; p=PTRS[idx]; audit.append(f'Record {idx:02d}: ${p:04X} bytes={len(rec):3d} FE={rec.count(FE):2d} FA={rec.count(FA)} FB={rec.count(FB)} F7/F8={rec.count(F7)}/{rec.count(F8)}')
    if idx==srcidx:
        for gi,g in enumerate(WRAPPED[srcidx]):
            audit.append(f'  utterance {gi+1}:')
            for row in g: audit.append(f'    [{tile_width(row):2d}] {row}')
AUDIT_OUT.write_text('\n'.join(audit)+'\n',encoding='utf-8')

NOTES_OUT.write_text('''STREET FIGHTER 2010 - V9 TRANSLATION NOTES\n\nPrinciples\n- Japanese game script remains the primary source.\n- The Japanese manual is used as canonical terminology/context, not as license to add story material absent from the game.\n- Natural English is preferred when it does not change meaning.\n- Original utterance boundaries, quote controls, pauses, and renderer scrolling behavior are preserved.\n\nManual-confirmed terminology\n- Parasite\n- Armored Insect\n- Galaxy Police\n- Open Power\n- Dimensional Door\n- Flip Shield\n\nKey prose revisions\n- 'made by' -> 'built by the Galaxy Police' in the Ballantine-type reveal.\n- Dagobah instruction now reads 'you'll be one step closer to perfection,' matching the Japanese wording and Jose's perfection motif.\n- Kevin's pain dialogue consistently retains 'pain' as a repeated story motif.\n- Jose's pore/body explanation is rendered as a concrete biological invasion rather than vague armor language.\n- Final mission briefing uses 'exterminate,' 'Open Power,' and 'Dimensional Door' in line with the Japanese text/manual.\n- 'Me... a Parasite...?' restores the clipped shock of Japanese 'ore... parasite...?' rather than expanding it into a full sentence.\n\nUnresolved proper noun\n- BALLANTINE-TYPE remains the best-supported reading of バランタイン型. The manual does not supply a Latin spelling.\n''',encoding='utf-8')

print('dialogue bytes',len(BLOB),'crawl bytes',len(crawl)); print('pointers',' '.join(f'{p:04X}' for p in PTRS)); print('changed debug bytes',len(chg_d),'normal',len(chg_n))
for p in [DEBUG_OUT,NORMAL_OUT,DEBUG_IPS,NORMAL_IPS,SCRIPT_OUT,AUDIT_OUT,NOTES_OUT,Path(__file__)]:
    d=p.read_bytes(); print(p.name,len(d),hashlib.sha256(d).hexdigest())
