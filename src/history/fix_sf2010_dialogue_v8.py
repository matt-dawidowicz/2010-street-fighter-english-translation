from pathlib import Path
import hashlib

ROOT=Path('/mnt/data')
DEBUG_IN=ROOT/'Street_Fighter_2010_Translation_DEBUG_v7_EternalMaxPower.nes'
NORMAL_IN=ROOT/'Street_Fighter_2010_Translation_RC3_PointerAndCrawlFix.nes'
DEBUG_OUT=ROOT/'Street_Fighter_2010_Translation_DEBUG_v8_DialogueSystemFix.nes'
NORMAL_OUT=ROOT/'Street_Fighter_2010_Translation_RC4_DialogueSystemFix.nes'
DEBUG_IPS=ROOT/'Street_Fighter_2010_DEBUG_v7_to_v8_DialogueSystemFix.ips'
NORMAL_IPS=ROOT/'Street_Fighter_2010_RC3_to_RC4_DialogueSystemFix.ips'
AUDIT_OUT=ROOT/'street-fighter-2010-dialogue-v8-audit.txt'

JP=ROOT/'Street Fighter 2010 (Japan)(4).nes'
TEXT_BANK=0x20010
TEXT_CPU=0x8000
OLD_CORPUS_END=0x2095E
PTR_ACTIVE=0x152A0
PTR_COPY=0x212A0
PTR_LEN=42
CURSOR_IMMEDIATES=(0x17064,0x17263)
CHR_GROUP=28
TILE_SIZE=16
TILE_OPEN_US=0xC1
TILE_CLOSE_US=0xC2
TILE_CURSOR=0xC4
TILE_OPEN_JP=0xF7
TILE_CLOSE_JP=0xF8
TILE_BLANK=0x24
F7=0xF7; F8=0xF8; FA=0xFA; FB=0xFB; FC=0xFC; FE=0xFE; FF=0xFF
ELLIPSIS=0x88

enc={chr(ord('A')+i):0x0A+i for i in range(26)}
enc.update({str(i):i for i in range(10)})
enc.update({' ':0x24,'.':0x8E,',':0x8D,'-':0x8F,'?':0x89,'!':0x8A})

records={
0:[('KEVIN...',True,True),('WHO ARE YOU?!',True,True),('... BALLANTINE-TYPE MX-5... A CYBORG MADE BY THE GALAXY POLICE... IS THAT WHAT YOU REALLY BELIEVE?',True,True),('WHAT DID YOU SAY...?',True,True)],
5:[('KEVIN...',True,True),('YOU BASTARD!',True,True),('GO TO DAGOBAH, THE DESERT PLANET. I HAVE HIDDEN A FLIP SHIELD GENERATOR THERE. EQUIP IT, AND YOUR STRENGTH WILL COME ONE STEP CLOSER TO PERFECTION...',True,True)],
6:[("WHY...? EVERY TIME I'M HIT, IT FEELS AS IF SOMETHING IS CRAWLING AROUND INSIDE ME... WHY DO I, A CYBORG, FEEL PAIN?!",True,True)],
7:[('DOES IT HURT, KEVIN...? THAT PAIN IS PROOF THAT YOU ARE NOT A CYBORG. COME TO MASSINI, THE MACHINE PLANET. ...I WILL ERASE THAT PAIN FOR YOU...',True,True)],
8:[('WELCOME, MY GREATEST MASTERPIECE, KEVIN.',True,True)],
9:[('YOUR GREATEST MASTERPIECE...?',True,True)],
10:[("THAT'S RIGHT. YOU ARE THE GREATEST PARASITE THAT I, DR. JOSE, HAVE CREATED.",True,False)],
11:[('...HAD THE GALAXY POLICE NOT BARGED IN BEFORE I COULD ATTACH THE ARMORED INSECT TO YOUR HEAD, YOU WOULD HAVE BECOME MY LOYAL SERVANT...',False,True)],
12:[("I'M... A PARASITE?",True,True)],
13:[("THAT'S RIGHT. THE CREATURE INSIDE YOUR ARMOR HAS ENTERED EVERY PORE OF YOUR BODY AND IS CRAWLING THROUGHOUT YOU.",True,True),('...',True,True)],
14:[('BUT EVEN YOU ARE NO LONGER THE GREATEST. I HAVE CREATED AN ARMORED INSECT SO FAR BEYOND YOU THAT YOU ARE NO MATCH FOR IT!',True,True)],
15:[("I'M A PARASITE...? ...",True,True),('MX-5, MX-5. THIS IS THE GALAXY POLICE. WE HAVE CONFIRMED YOUR MISSION IS COMPLETE. WE WILL RELAY YOUR NEXT MISSION. A CYBORG TERRORIST HAS STRUCK ON EARTH. ARREST OR DESTROY THE PERPETRATOR.',True,True),('...',True,True)],
16:[('MX-5, READ BACK YOUR ORDERS!',True,True)],
17:[("...I READ YOU. I'M ON MY WAY...",True,True)],
18:[('MX-5, YOU ARE ORDERED TO WIPE OUT THE PARASITES. SEEK OUT THE TARGET PARASITE, DESTROY IT, AND BUILD UP OPEN POWER FOR THE DIMENSIONAL DOOR. BUT TEN SECONDS AFTER THE DOOR OPENS, THE OPEN POWER WILL BE DEPLETED. IF THAT HAPPENS, YOUR BODY WILL VANISH... BE CAREFUL, KEVIN.',True,True)],
19:[('...',True,True)],
20:[("KEVIN! I'LL TEST IT ON YOUR BODY!",True,True)],
}

sep_kind={0:['fb','fb','fb'],5:['fb','fb'],13:['double'],15:['fb','fb']}
JP_SKELETON={0:(4,4,3),5:(3,3,2),6:(1,1,0),7:(1,1,0),8:(1,1,0),9:(1,1,0),10:(1,0,0),11:(0,1,0),12:(1,1,0),13:(2,2,0),14:(1,1,0),15:(3,3,2),16:(1,1,0),17:(1,1,0),18:(1,1,0),19:(1,1,0),20:(1,1,0)}


def tile_width(s):
    n=0; i=0
    while i<len(s):
        if s.startswith('...',i): n+=1; i+=3
        else: n+=1; i+=1
    return n


def wrap_text(s, cap=23):
    words=s.split(' '); lines=[]; cur=''
    for w in words:
        cand=w if not cur else cur+' '+w
        if tile_width(cand)<=cap: cur=cand
        else:
            if not cur or tile_width(w)>cap: raise RuntimeError(f'cannot wrap word safely: {w!r}')
            lines.append(cur); cur=w
    if cur: lines.append(cur)
    if len(lines)==1 and tile_width(lines[0])+2>24: return wrap_text(s,22)
    return lines


def encode_text(s):
    out=bytearray(); i=0
    while i<len(s):
        if s.startswith('...',i): out.append(ELLIPSIS); i+=3; continue
        c=s[i]
        if c=="'": out.append(FC); i+=1; continue
        try: out.append(enc[c])
        except KeyError: raise RuntimeError(f'unsupported character {c!r} in {s!r}')
        i+=1
    return out


def encode_group(text,open_q,close_q):
    lines=wrap_text(text); out=bytearray()
    if open_q: out.append(F7)
    for li,line in enumerate(lines):
        out += encode_text(line)
        if li+1<len(lines): out.append(FE)
    if close_q: out.append(F8)
    return out,lines


def build_raw_record(idx):
    groups=records[idx]; out=bytearray(); wrapped=[]
    for gi,(text,oq,cq) in enumerate(groups):
        gb,lines=encode_group(text,oq,cq); out+=gb; wrapped.append(lines)
        if gi+1<len(groups):
            kind=sep_kind[idx][gi]
            if kind=='fb': out+=bytes([FE,FB,FE])
            elif kind=='double': out+=bytes([FE,FE])
            else: raise RuntimeError(kind)
    return out,wrapped


def insert_scroll_after_fifth_fe(raw, pre_fe=0):
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
        f7,f8,fb=JP_SKELETON[idx]
        assert (b.count(F7),b.count(F8),b.count(FB))==(f7,f8,fb)
        assert max(rendered_widths(b))<=24
    return built,wrapped_by,scroll_by

BUILT,WRAPPED,SCROLL=build_records()


def pack_records():
    blob=bytearray(); ptrs=[None]*21; offsets={}
    for idx in [0,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]:
        cpu=TEXT_CPU+len(blob)
        if cpu>=0xA000: raise RuntimeError('English corpus overflowed 8 KiB bank')
        offsets[idx]=(cpu,len(blob),len(BUILT[idx]))
        if idx==0:
            for i in range(5): ptrs[i]=cpu
        else: ptrs[idx]=cpu
        blob+=BUILT[idx]
    assert all(p is not None for p in ptrs)
    return bytes(blob),ptrs,offsets

BLOB,PTRS,OFFSETS=pack_records(); PTR_BYTES=b''.join(int(p).to_bytes(2,'little') for p in PTRS)


def original_jp_skeleton_check():
    data=JP.read_bytes(); ptrs=[int.from_bytes(data[PTR_ACTIVE+i:PTR_ACTIVE+i+2],'little') for i in range(0,PTR_LEN,2)]
    assert ptrs[:5]==[ptrs[0]]*5
    for idx in JP_SKELETON:
        p=ptrs[idx]; off=0x14010+(p-0x8000); a=bytearray()
        for x in data[off:off+0x300]:
            a.append(x)
            if x==FF: break
        assert (a.count(F7),a.count(F8),a.count(FB))==JP_SKELETON[idx]
        if FA in a: assert a[:a.index(FA)].count(FE)==5
original_jp_skeleton_check()


def patch_rom(src_path,out_path):
    original=src_path.read_bytes()
    if len(original)!=393232: raise RuntimeError((src_path,len(original)))
    b=bytearray(original); assert b[4]==0x10 and b[5]==0x10
    b[TEXT_BANK:OLD_CORPUS_END]=bytes(OLD_CORPUS_END-TEXT_BANK)
    b[TEXT_BANK:TEXT_BANK+len(BLOB)]=BLOB
    b[PTR_ACTIVE:PTR_ACTIVE+PTR_LEN]=PTR_BYTES
    b[PTR_COPY:PTR_COPY+PTR_LEN]=PTR_BYTES
    chr_start=16+b[4]*16384; group=chr_start+CHR_GROUP*4096
    open_us=bytes(b[group+TILE_OPEN_US*TILE_SIZE:group+(TILE_OPEN_US+1)*TILE_SIZE])
    close_us=bytes(b[group+TILE_CLOSE_US*TILE_SIZE:group+(TILE_CLOSE_US+1)*TILE_SIZE])
    blank=bytes(b[group+TILE_BLANK*TILE_SIZE:group+(TILE_BLANK+1)*TILE_SIZE])
    assert blank==bytes(16)
    b[group+TILE_OPEN_JP*TILE_SIZE:group+(TILE_OPEN_JP+1)*TILE_SIZE]=open_us
    b[group+TILE_CLOSE_JP*TILE_SIZE:group+(TILE_CLOSE_JP+1)*TILE_SIZE]=close_us
    pattern=bytes([0xA9,0xC4,0x8D,0xFD,0x02,0xA9,0x02,0x8D,0xFE,0x02])
    found=[]; start=0
    while True:
        j=original.find(pattern,start)
        if j<0: break
        found.append(j); start=j+1
    assert found==[0x17063,0x17262]
    for imm in CURSOR_IMMEDIATES: assert b[imm]==TILE_CURSOR; b[imm]=TILE_BLANK
    assert bytes(b[PTR_ACTIVE:PTR_ACTIVE+PTR_LEN])==PTR_BYTES
    assert bytes(b[PTR_COPY:PTR_COPY+PTR_LEN])==PTR_BYTES
    for idx,p in enumerate(PTRS):
        off=TEXT_BANK+(p-TEXT_CPU); assert TEXT_BANK<=off<TEXT_BANK+len(BLOB)
        b.index(FF,off,TEXT_BANK+len(BLOB)+1)
    for idx in JP_SKELETON:
        p=PTRS[idx]; off=TEXT_BANK+(p-TEXT_CPU); end=b.index(FF,off)+1; rec=bytes(b[off:end]); f7,f8,fb=JP_SKELETON[idx]
        assert (rec.count(F7),rec.count(F8),rec.count(FB))==(f7,f8,fb); assert max(rendered_widths(rec))<=24
    assert b[0x14A84:0x14C15]==original[0x14A84:0x14C15]
    if 'DEBUG' in src_path.name:
        helper=bytes([0xA9,0x0A,0x85,0xB2,0xA5,0xAD,0x29,0xF9,0x60])
        for bank in [0x1C010,0x3C010]:
            assert bytes(b[bank+0x1B4:bank+0x1B4+9])==helper
            assert bytes(b[bank+0x27B:bank+0x27B+4])==bytes([0x20,0xB4,0xC1,0xEA])
        assert b[0x1801E]==0x09
        for off in [0x1D4C6,0x1D4DC,0x3D4C6,0x3D4DC]: assert b[off]==0x00
    allowed=set(range(TEXT_BANK,OLD_CORPUS_END)); allowed.update(range(PTR_ACTIVE,PTR_ACTIVE+PTR_LEN)); allowed.update(range(PTR_COPY,PTR_COPY+PTR_LEN)); allowed.update(CURSOR_IMMEDIATES)
    allowed.update(range(group+TILE_OPEN_JP*TILE_SIZE,group+(TILE_OPEN_JP+1)*TILE_SIZE)); allowed.update(range(group+TILE_CLOSE_JP*TILE_SIZE,group+(TILE_CLOSE_JP+1)*TILE_SIZE))
    changed=[i for i,(x,y) in enumerate(zip(original,b)) if x!=y]; bad=[i for i in changed if i not in allowed]; assert not bad
    out_path.write_bytes(b); return original,bytes(b),changed


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
make_ips(old_d,new_d,DEBUG_IPS); make_ips(old_n,new_n,NORMAL_IPS)
assert apply_ips(old_d,DEBUG_IPS)==new_d; assert apply_ips(old_n,NORMAL_IPS)==new_n
lines=['STREET FIGHTER 2010 - DIALOGUE SYSTEM FIX V8 AUDIT','',f'Packed corpus: {len(BLOB)} bytes, CPU $8000-${TEXT_CPU+len(BLOB)-1:04X}','Records 1-4 alias record 0, matching the Japanese ROM.','F7/F8 controls retained but their CHR glyphs now use C1/C2 English curly-quote art.','C4 cursor sprite tile replaced with blank tile $24 at both renderer setup sites.','FB counts match the Japanese original; artificial 3-line English pages removed.','FA scrolling is inserted after the fifth cumulative FE whenever English needs further lines.','']
for idx in range(21):
    srcidx=0 if 1<=idx<=4 else idx; rec=BUILT[srcidx]; p=PTRS[idx]
    lines.append(f'Record {idx:02d}: ${p:04X}  bytes={len(rec):3d}  FE={rec.count(FE):2d}  FA={rec.count(FA)}  FB={rec.count(FB)}  F7/F8={rec.count(F7)}/{rec.count(F8)}')
    if idx==srcidx:
        for gi,g in enumerate(WRAPPED[srcidx]):
            lines.append(f'  utterance {gi+1}:')
            for row in g: lines.append(f'    [{tile_width(row):2d}] {row}')
AUDIT_OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
for p in [DEBUG_OUT,NORMAL_OUT,DEBUG_IPS,NORMAL_IPS,AUDIT_OUT,Path(__file__)]:
    d=p.read_bytes(); print(p.name,len(d),hashlib.sha256(d).hexdigest())
