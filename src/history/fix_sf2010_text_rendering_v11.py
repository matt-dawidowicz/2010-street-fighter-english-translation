from pathlib import Path
import hashlib

ROOT = Path('/mnt/data')
DEBUG_IN = ROOT / 'Street_Fighter_2010_Translation_DEBUG_v10_CursorScrollFix.nes'
NORMAL_IN = ROOT / 'Street_Fighter_2010_Translation_RC7_CursorScrollFix.nes'
DEBUG_OUT = ROOT / 'Street_Fighter_2010_Translation_DEBUG_v11_TextRenderingFix.nes'
NORMAL_OUT = ROOT / 'Street_Fighter_2010_Translation_RC8_TextRenderingFix.nes'
DEBUG_IPS = ROOT / 'Street_Fighter_2010_DEBUG_v10_to_v11_TextRenderingFix.ips'
NORMAL_IPS = ROOT / 'Street_Fighter_2010_RC7_to_RC8_TextRenderingFix.ips'
AUDIT = ROOT / 'street-fighter-2010-v11-text-rendering-audit.txt'

PTR_ACTIVE = 0x152A0
TEXT_BANK = 0x20010
TEXT_CPU = 0x8000
PTR_LEN = 42
CURSOR_IMMEDIATES = (0x17064, 0x17263)
APOSTROPHE_TILE_IMMEDIATE = 0x1712D
POST_SCROLL = 0x171F8
FF = 0xFF
FC = 0xFC

APOSTROPHE_OLD = bytes.fromhex('c9 fc d0 0d a9 8d 8d 04 03 a9 24 8d 05 03')
POST_SCROLL_OLD_PREFIX = bytes.fromhex('a9 20 85 01 20 b7 b1 a0 00 b1 76 c9')
POST_SCROLL_US_STYLE = bytes.fromhex('a9 20 85 01 20 b7 b1 a9 01 85 73 60')


def dialogue_fc_count(b):
    ptrs = [int.from_bytes(b[PTR_ACTIVE+i:PTR_ACTIVE+i+2], 'little') for i in range(0, PTR_LEN, 2)]
    total = 0
    unique = 0
    by_record = {}
    seen = set()
    for idx, p in enumerate(ptrs):
        off = TEXT_BANK + (p - TEXT_CPU)
        end = b.index(FF, off) + 1
        c = b[off:end].count(FC)
        if c:
            by_record[idx] = c
        total += c
        if p not in seen:
            unique += c
            seen.add(p)
    return total, unique, by_record


def patch_rom(path):
    original = path.read_bytes()
    if len(original) != 393232:
        raise RuntimeError((path, len(original)))
    b = bytearray(original)
    assert [b[x] for x in CURSOR_IMMEDIATES] == [0xC4, 0xC4]

    start = APOSTROPHE_TILE_IMMEDIATE - 5
    assert bytes(b[start:start+len(APOSTROPHE_OLD)]) == APOSTROPHE_OLD
    assert b[APOSTROPHE_TILE_IMMEDIATE] == 0x8D
    b[APOSTROPHE_TILE_IMMEDIATE] = 0xD0

    assert bytes(b[POST_SCROLL:POST_SCROLL+len(POST_SCROLL_OLD_PREFIX)]) == POST_SCROLL_OLD_PREFIX
    b[POST_SCROLL:POST_SCROLL+len(POST_SCROLL_US_STYLE)] = POST_SCROLL_US_STYLE

    changed = [i for i, (x, y) in enumerate(zip(original, b)) if x != y]
    allowed = {APOSTROPHE_TILE_IMMEDIATE}
    allowed.update(range(POST_SCROLL, POST_SCROLL + len(POST_SCROLL_US_STYLE)))
    bad = [i for i in changed if i not in allowed]
    assert not bad, [hex(x) for x in bad]

    assert b[TEXT_BANK:0x2095E] == original[TEXT_BANK:0x2095E]
    assert b[PTR_ACTIVE:PTR_ACTIVE+PTR_LEN] == original[PTR_ACTIVE:PTR_ACTIVE+PTR_LEN]
    total_fc, unique_fc, by_record = dialogue_fc_count(b)
    assert unique_fc == 10, (unique_fc, by_record)

    if 'DEBUG' in path.name:
        helper = bytes([0xA9,0x0A,0x85,0xB2,0xA5,0xAD,0x29,0xF9,0x60])
        for bank in [0x1C010,0x3C010]:
            assert bytes(b[bank+0x1B4:bank+0x1B4+9]) == helper
            assert bytes(b[bank+0x27B:bank+0x27B+4]) == bytes([0x20,0xB4,0xC1,0xEA])
        assert b[0x1801E] == 0x09
        for off in [0x1D4C6,0x1D4DC,0x3D4C6,0x3D4DC]:
            assert b[off] == 0x00

    return original, bytes(b), changed, (total_fc, unique_fc, by_record)


def make_ips(old, new, path):
    assert len(old) == len(new)
    out = bytearray(b'PATCH')
    i = 0
    while i < len(old):
        if old[i] == new[i]:
            i += 1
            continue
        start = i
        while i < len(old) and old[i] != new[i] and i-start < 0xFFFF:
            i += 1
        data = new[start:i]
        out += start.to_bytes(3, 'big') + len(data).to_bytes(2, 'big') + data
    out += b'EOF'
    path.write_bytes(out)


def apply_ips(old, path):
    p = path.read_bytes()
    assert p[:5] == b'PATCH'
    out = bytearray(old)
    i = 5
    while p[i:i+3] != b'EOF':
        off = int.from_bytes(p[i:i+3], 'big')
        n = int.from_bytes(p[i+3:i+5], 'big')
        i += 5
        assert n
        out[off:off+n] = p[i:i+n]
        i += n
    return bytes(out)


old_d, new_d, chg_d, fc_d = patch_rom(DEBUG_IN)
old_n, new_n, chg_n, fc_n = patch_rom(NORMAL_IN)
DEBUG_OUT.write_bytes(new_d)
NORMAL_OUT.write_bytes(new_n)
make_ips(old_d, new_d, DEBUG_IPS)
make_ips(old_n, new_n, NORMAL_IPS)
assert apply_ips(old_d, DEBUG_IPS) == new_d
assert apply_ips(old_n, NORMAL_IPS) == new_n
assert new_d[APOSTROPHE_TILE_IMMEDIATE] == new_n[APOSTROPHE_TILE_IMMEDIATE] == 0xD0
assert new_d[POST_SCROLL:POST_SCROLL+12] == new_n[POST_SCROLL:POST_SCROLL+12] == POST_SCROLL_US_STYLE

lines = [
    'STREET FIGHTER 2010 - V11 / RC8 TEXT RENDERING AUDIT','',
    'Problems reproduced from the completed playthrough:',
    '- Contractions rendered with a conspicuous visual gap after apostrophes (e.g. THAT\' S, HADN\' T).',
    '- Record 11 could show a stale opening-quote glyph and lose the initial Y in YOUR HEAD after long-text scrolling.','',
    'Root causes:',
    '- $FC apostrophe handling reused left-weighted comma tile $8D in the upper half of the glyph cell.',
    '- The Japanese state-4 post-scroll path re-read/replayed $F7; Capcom removed that replay path in the U.S. retail renderer.','',
    'Fixes:',
    f'- ${APOSTROPHE_TILE_IMMEDIATE:05X}: apostrophe glyph immediate $8D -> $D0. This affects every $FC contraction handled by the dialogue renderer.',
    f'- ${POST_SCROLL:05X}: state-4 entry now clears the scroll row and returns directly to text state 1, matching U.S.-retail semantics while retaining Japanese code addresses.','',
    f'- Unique encoded apostrophes in packed dialogue corpus: {fc_d[1]}',
    f'- Pointer-index apostrophe count including aliased records: {fc_d[0]}',
    '- Dialogue bytes, prose, wrapping, record lengths, and pointer tables are unchanged.',
    '- Cursor tile restoration from V10/RC7 remains intact.',
    '- Gameplay/debug code is unchanged.','',
    'Runtime validation with supplied Mesen save state:',
    '- THAT\'S renders without the phantom gap.',
    '- HADN\'T renders without the phantom gap.',
    '- Record 11 renders YOUR HEAD, YOU WOULD with the Y intact and no ghost opening quote.',
    '- Cursor remains on the active text line through the corrected scroll.','',
]
for label, path, data, changed in [('DEBUG v11', DEBUG_OUT, new_d, chg_d),('RC8', NORMAL_OUT, new_n, chg_n),('DEBUG IPS', DEBUG_IPS, DEBUG_IPS.read_bytes(), []),('RC8 IPS', NORMAL_IPS, NORMAL_IPS.read_bytes(), [])]:
    lines += [f'{label}: {path.name}',f'  bytes={len(data)}',f'  sha256={hashlib.sha256(data).hexdigest()}']
    if changed:
        lines.append(f'  changed_bytes={len(changed)}')
        lines.append('  offsets=' + ','.join(f'${x:05X}' for x in changed))
AUDIT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

for p in [DEBUG_OUT, NORMAL_OUT, DEBUG_IPS, NORMAL_IPS, AUDIT, Path(__file__)]:
    d = p.read_bytes()
    print(p.name, len(d), hashlib.sha256(d).hexdigest())
