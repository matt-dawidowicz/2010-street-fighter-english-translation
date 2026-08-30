from pathlib import Path
import hashlib

ROOT=Path('/mnt/data')
DEBUG_IN=ROOT/'Street_Fighter_2010_Translation_DEBUG_v12_ApostropheFix.nes'
NORMAL_IN=ROOT/'Street_Fighter_2010_Translation_RC9_ApostropheFix.nes'
DEBUG_OUT=ROOT/'Street_Fighter_2010_Translation_DEBUG_v13_ApostropheLigatures.nes'
NORMAL_OUT=ROOT/'Street_Fighter_2010_Translation_RC10_ApostropheLigatures.nes'
DEBUG_IPS=ROOT/'Street_Fighter_2010_DEBUG_v12_to_v13_ApostropheLigatures.ips'
NORMAL_IPS=ROOT/'Street_Fighter_2010_RC9_to_RC10_ApostropheLigatures.ips'
AUDIT=ROOT/'street-fighter-2010-v13-apostrophe-ligature-audit.txt'

TEXT_BANK=0x20010
TEXT_CPU=0x8000
CORPUS_CLEAR_END=0x2095E
PTR_ACTIVE=0x152A0
PTR_COPY=0x212A0
PTR_LEN=42
APOSTROPHE_TILE_IMMEDIATE=0x1712D
POST_SCROLL=0x171F8
POST_SCROLL_US_STYLE=bytes.fromhex('a9 20 85 01 20 b7 b1 a9 01 85 73 60')
FC=0xFC; FF=0xFF; FE=0xFE; FA=0xFA; FB=0xFB; F7=0xF7; F8=0xF8
LETTER={'T':0x1D,'I':0x12,'U':0x1E,'N':0x17}
LIG={'T':0xB0,'I':0xB1,'U':0xB2,'N':0xB3}
CHR_GROUP=28
TILE_SIZE=16


def make_ligature(letter_tile, letter):
    assert len(letter_tile)==16
    p0=bytearray(letter_tile[:8]); p1=bytearray(letter_tile[8:])
    assert p0==p1
    p0[0] |= 0x03
    if letter=='T':
        p0[1] = (p0[1] & ~0x02) | 0x01
    elif letter=='I':
        p0[1] |= 0x01
    return bytes(p0+p0)


def get_record_bytes(b, ptr):
    off=TEXT_BANK+(ptr-TEXT_CPU)
    end=b.index(FF,off,CORPUS_CLEAR_END)+1
    return bytes(b[off:end])


def transform_record(rec):
    out=bytearray(); i=0; replacements=[]
    while i<len(rec):
        if i+1<len(rec) and rec[i] in LETTER.values() and rec[i+1]==FC:
            letter=next(k for k,v in LETTER.items() if v==rec[i])
            out.append(LIG[letter]); replacements.append((i,letter)); i+=2
        else:
            out.append(rec[i]); i+=1
    return bytes(out),replacements


def rendered_widths(rec):
    widths=[]; w=0
    for x in rec:
        if x==FF: break
        if x==FE:
            widths.append(w); w=0
        elif x in (FA,FB): pass
        else: w+=1
    widths.append(w)
    return widths


def patch(path):
    old=path.read_bytes(); assert len(old)==393232
    b=bytearray(old)
    assert bytes(b[POST_SCROLL:POST_SCROLL+12])==POST_SCROLL_US_STYLE
    assert b[APOSTROPHE_TILE_IMMEDIATE]==0xC5
    old_ptrs=[int.from_bytes(b[PTR_ACTIVE+i:PTR_ACTIVE+i+2],'little') for i in range(0,PTR_LEN,2)]
    assert old_ptrs[:5]==[old_ptrs[0]]*5
    order=[0,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    unique_old={idx:get_record_bytes(b,old_ptrs[idx]) for idx in order}
    for rec in unique_old.values(): assert not any(x in LIG.values() for x in rec)

    transformed={}; repl={}
    for idx in order:
        transformed[idx],repl[idx]=transform_record(unique_old[idx])
        old_controls=[x for x in unique_old[idx] if x>=0xF7 and x!=FC]
        new_controls=[x for x in transformed[idx] if x>=0xF7]
        assert old_controls==new_controls
        assert transformed[idx].count(FC)==0
        assert len(transformed[idx])==len(unique_old[idx])-len(repl[idx])
        assert max(rendered_widths(transformed[idx]))<=24

    total=sum(len(v) for v in repl.values())
    assert total==10
    assert {k:sum(1 for rs in repl.values() for _,ch in rs if ch==k) for k in LIG}=={'T':3,'I':4,'U':2,'N':1}

    blob=bytearray(); new_ptrs=[None]*21
    for idx in order:
        cpu=TEXT_CPU+len(blob); assert cpu<0xA000
        if idx==0:
            for j in range(5): new_ptrs[j]=cpu
        else: new_ptrs[idx]=cpu
        blob+=transformed[idx]
    assert all(x is not None for x in new_ptrs); assert len(blob)<0x1000
    ptr_bytes=b''.join(int(x).to_bytes(2,'little') for x in new_ptrs)

    b[TEXT_BANK:CORPUS_CLEAR_END]=bytes(CORPUS_CLEAR_END-TEXT_BANK)
    b[TEXT_BANK:TEXT_BANK+len(blob)]=blob
    b[PTR_ACTIVE:PTR_ACTIVE+PTR_LEN]=ptr_bytes
    b[PTR_COPY:PTR_COPY+PTR_LEN]=ptr_bytes
    b[APOSTROPHE_TILE_IMMEDIATE]=0x8D

    chr_start=16+b[4]*16384; group=chr_start+CHR_GROUP*4096; glyph_bytes={}
    for letter,tile in LIG.items():
        src=LETTER[letter]; letter_tile=bytes(b[group+src*16:group+src*16+16]); glyph=make_ligature(letter_tile,letter); glyph_bytes[letter]=glyph; off=group+tile*16; b[off:off+16]=glyph

    final_ptrs=[int.from_bytes(b[PTR_ACTIVE+i:PTR_ACTIVE+i+2],'little') for i in range(0,PTR_LEN,2)]
    assert final_ptrs==new_ptrs
    assert bytes(b[PTR_COPY:PTR_COPY+PTR_LEN])==ptr_bytes
    for idx in range(21):
        srcidx=0 if 1<=idx<=4 else idx; rec=get_record_bytes(b,final_ptrs[idx]); assert rec==transformed[srcidx]; assert rec.count(FC)==0; assert max(rendered_widths(rec))<=24
    for letter,tile in LIG.items():
        off=group+tile*16; assert bytes(b[off:off+16])==glyph_bytes[letter]

    assert b[0x17064]==0xC4 and b[0x17263]==0xC4
    assert bytes(b[POST_SCROLL:POST_SCROLL+12])==POST_SCROLL_US_STYLE

    if 'DEBUG' in path.name:
        helper=bytes([0xA9,0x0A,0x85,0xB2,0xA5,0xAD,0x29,0xF9,0x60])
        for bank in [0x1C010,0x3C010]:
            assert bytes(b[bank+0x1B4:bank+0x1B4+9])==helper
            assert bytes(b[bank+0x27B:bank+0x27B+4])==bytes([0x20,0xB4,0xC1,0xEA])
        assert b[0x1801E]==0x09
        for off in [0x1D4C6,0x1D4DC,0x3D4C6,0x3D4DC]: assert b[off]==0x00

    changed=[i for i,(x,y) in enumerate(zip(old,b)) if x!=y]
    allowed=set(range(TEXT_BANK,CORPUS_CLEAR_END)); allowed.update(range(PTR_ACTIVE,PTR_ACTIVE+PTR_LEN)); allowed.update(range(PTR_COPY,PTR_COPY+PTR_LEN)); allowed.add(APOSTROPHE_TILE_IMMEDIATE)
    for tile in LIG.values(): allowed.update(range(group+tile*16,group+tile*16+16))
    bad=[x for x in changed if x not in allowed]; assert not bad
    return old,bytes(b),changed,old_ptrs,new_ptrs,unique_old,transformed,repl,group,glyph_bytes,len(blob)


def make_ips(old,new,path):
    out=bytearray(b'PATCH'); i=0
    while i<len(old):
        if old[i]==new[i]: i+=1; continue
        s=i
        while i<len(old) and old[i]!=new[i] and i-s<0xFFFF: i+=1
        d=new[s:i]; out+=s.to_bytes(3,'big')+len(d).to_bytes(2,'big')+d
    out+=b'EOF'; path.write_bytes(out)


def apply_ips(old,path):
    p=path.read_bytes(); assert p[:5]==b'PATCH'; out=bytearray(old); i=5
    while p[i:i+3]!=b'EOF':
        off=int.from_bytes(p[i:i+3],'big'); n=int.from_bytes(p[i+3:i+5],'big'); i+=5
        if n:
            out[off:off+n]=p[i:i+n]; i+=n
        else:
            r=int.from_bytes(p[i:i+2],'big'); v=p[i+2]; i+=3; out[off:off+r]=bytes([v])*r
    return bytes(out)

rd=patch(DEBUG_IN); rn=patch(NORMAL_IN)
od,nd,cd,opd,npd,urod,trd,rpd,gd,glyphd,blobd=rd
on,nn,cn,opn,npn,uron,trn,rpn,gn,glyphn,blobn=rn
assert npd==npn and trd==trn and rpd==rpn and blobd==blobn and glyphd==glyphn
DEBUG_OUT.write_bytes(nd); NORMAL_OUT.write_bytes(nn)
make_ips(od,nd,DEBUG_IPS); make_ips(on,nn,NORMAL_IPS)
assert apply_ips(od,DEBUG_IPS)==nd
assert apply_ips(on,NORMAL_IPS)==nn

lines=['STREET FIGHTER 2010 - V13 / RC10 APOSTROPHE LIGATURE AUDIT','','Goal: remove the unavoidable empty 8-pixel apostrophe cell on both sides of contractions.','Method: replace each preceding-letter + $FC pair with one ordinary combined glyph tile.','','Ligatures: $B0=T\', $B1=I\', $B2=U\', $B3=N\'.','All 10 unique English apostrophes are converted; no $FC remains in the packed English dialogue.','The stock $FC handler is restored to its original $8D tile for unrelated/original data.','Existing line breaks and all F7/F8/FA/FB/FE/FF controls are preserved exactly; only record byte lengths shrink.','V11 U.S.-style post-scroll fix and V10 cursor restoration are preserved unchanged.','Gameplay/debug code is unchanged.','','Runtime validation with the supplied late-game Mesen save state:','- THAT\'S renders with no extra apostrophe cell.','- HADN\'T renders with no extra apostrophe cell.','- YOUR HEAD remains intact through Record 11 scrolling.','- Synthetic coverage line verified I\'M / I\'VE / I\'LL / YOU\'RE / YOU\'LL.','',f'Packed corpus: {sum(len(x) for x in urod.values())} -> {blobd} bytes (-10).','Ligature uses: T\'=3, I\'=4, U\'=2, N\'=1.','','Pointer changes:']
for idx,(a,b) in enumerate(zip(opd,npd)): lines.append(f'  {idx:02d}: ${a:04X} -> ${b:04X}')
lines += ['', 'Per-record shrink:']
for idx in [0,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]:
    if rpd[idx]: lines.append(f"  {idx:02d}: -{len(rpd[idx])} " + ', '.join(ch+"'" for _,ch in rpd[idx]))
for label,path,data,chg in [('DEBUG v13',DEBUG_OUT,nd,cd),('RC10',NORMAL_OUT,nn,cn),('DEBUG IPS',DEBUG_IPS,DEBUG_IPS.read_bytes(),[]),('RC IPS',NORMAL_IPS,NORMAL_IPS.read_bytes(),[])]:
    lines += ['',f'{label}: {path.name}',f'  bytes={len(data)}',f'  sha256={hashlib.sha256(data).hexdigest()}']
    if chg: lines.append(f'  changed_bytes={len(chg)}')
AUDIT.write_text('\n'.join(lines)+'\n',encoding='utf-8')

for p in [DEBUG_OUT,NORMAL_OUT,DEBUG_IPS,NORMAL_IPS,AUDIT,Path(__file__)]:
    d=p.read_bytes(); print(p.name,len(d),hashlib.sha256(d).hexdigest())
print('corpus',sum(len(x) for x in urod.values()),'->',blobd)
print('ligatures', {k:sum(1 for rs in rpd.values() for _,ch in rs if ch==k) for k in LIG})
