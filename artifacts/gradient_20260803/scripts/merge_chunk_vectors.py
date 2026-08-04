#!/usr/bin/env python3
"""
merge_chunk_vectors.py — count-weighted merge of chunk extraction GGUFs.
Per Lyra's green light (2026-08-03): mean is associative; count-weighted merge
of chunk directions = exact global mean-diff. Frozen method untouched.
Usage: merge_chunk_vectors.py out.gguf chunk1.gguf chunk2.gguf ...
Weights = per-chunk pair counts, read from a manifest file if given:
  merge_chunk_vectors.py out.gguf --manifest chunks.json chunk1.gguf ...
manifest: {"chunk1.gguf": 307, ...}  (if absent, equal weights)
"""
import struct, sys, json, numpy as np

def read_str(data, pos):
    n = struct.unpack_from('<Q', data, pos)[0]; pos += 8
    return data[pos:pos+n].decode('utf-8', errors='replace'), pos+n

def parse(path):
    data = open(path, 'rb').read()
    assert data[:4] == b'GGUF', 'not gguf'
    n_tensors = struct.unpack_from('<Q', data, 8)[0]
    n_kv = struct.unpack_from('<Q', data, 16)[0]
    pos = 24
    for _ in range(n_kv):
        key, pos = read_str(data, pos)
        ktype = struct.unpack_from('<I', data, pos)[0]; pos += 4
        if ktype == 8:
            _, pos = read_str(data, pos)
        elif ktype == 9:
            atype = struct.unpack_from('<I', data, pos)[0]; pos += 4
            n = struct.unpack_from('<Q', data, pos)[0]; pos += 8
            if atype == 8:
                for _ in range(n): _, pos = read_str(data, pos)
            else:
                pos += n * (1 if atype in (0,1) else 2 if atype in (2,3) else 4 if atype in (4,5,6) else 8)
        else:
            pos += {0:1,1:1,2:2,3:2,4:4,5:4,6:4,7:1,10:8,11:8,12:8}[ktype]
    tensors = []
    for t in range(n_tensors):
        name, pos = read_str(data, pos)
        n_dims = struct.unpack_from('<I', data, pos)[0]; pos += 4
        dims = struct.unpack_from('<' + 'Q'*n_dims, data, pos); pos += 8*n_dims
        dtype = struct.unpack_from('<I', data, pos)[0]; pos += 4
        offset = struct.unpack_from('<Q', data, pos)[0]; pos += 8
        tensors.append((name, dtype, dims, offset))
    data_start = (pos + 31) // 32 * 32
    return data, data_start, tensors

def main():
    args = sys.argv[1:]
    out_path = args[0]
    manifest_path = None
    if '--manifest' in args:
        mi = args.index('--manifest')
        manifest_path = args[mi+1]
        args = args[:mi] + args[mi+2:]
    chunk_paths = args[1:]
    if not chunk_paths:
        print("no chunks given", file=sys.stderr); sys.exit(1)

    weights = None
    if manifest_path:
        with open(manifest_path) as f:
            weights = json.load(f)

    parsed = [parse(p) for p in chunk_paths]
    ref_data, ref_start, ref_tensors = parsed[0]
    offmap = {t[0]: t[3] for t in ref_tensors}

    merged = {}
    for name, dtype, dims, offset in ref_tensors:
        n = int(np.prod(dims))
        arrs, wts = [], []
        for (data, data_start, tensors), cp in zip(parsed, chunk_paths):
            if name not in offmap:  # tensor may be missing in some chunk (flaky layer)
                continue
            toff = data_start + offmap[name]
            arrs.append(np.frombuffer(data, dtype=np.float32, count=n, offset=toff))
            wts.append(weights.get(cp, 1.0) if weights else 1.0)
        if not arrs:
            merged[name] = np.zeros(n, dtype=np.float32)
            continue
        wsum = sum(wts)
        merged[name] = sum(a * w for a, w in zip(arrs, wts)) / wsum

    out = bytearray(ref_data)
    for name, dtype, dims, offset in ref_tensors:
        n = int(np.prod(dims))
        abs_off = ref_start + offset
        if len(merged[name]) == n:
            out[abs_off:abs_off+4*n] = merged[name].astype(np.float32).tobytes()

    with open(out_path, 'wb') as f:
        f.write(bytes(out))
    print(f"merged {len(chunk_paths)} chunks -> {out_path} ({len(out)} bytes)")

if __name__ == '__main__':
    main()
