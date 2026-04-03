import re, json, os

PATH = r'e:\ComfyUI\App\custom_nodes\ComfyUI-JSG-Utils\nodes\JSGRandomPromptBuilder.py'
DATA_DIR = r'e:\ComfyUI\App\custom_nodes\ComfyUI-JSG-Utils\data\random_prompt_generator'

with open(PATH, 'r', encoding='utf-8') as f:
    src = f.read()

changes = ["1-3 already applied"]

# ── 4: _get_parts_list + add _get_subindexes_list ─────────────────────────────
old = (
    "# \u2500\u2500 Parts normalisation \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
    "\n"
    "def _get_parts_list(data):\n"
    '    """Return parts with a valid partsIndex (int >= 0), sorted ascending.\n'
    "\n"
    "    Parts where partsIndex is absent, not an int, or < 0 are silently skipped.\n"
    '    """\n'
    "    result = []\n"
    '    for p in (data.get("parts") or []):\n'
    "        if not isinstance(p, dict):\n"
    "            continue\n"
    '        pi = p.get("partsIndex")\n'
    "        if not (isinstance(pi, int) and pi >= 0):\n"
    "            continue\n"
    "        result.append(dict(p))\n"
    '    return sorted(result, key=lambda p: p["partsIndex"])'
)
new = (
    "# \u2500\u2500 Parts normalisation \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
    "\n"
    "def _get_subindexes_list(data):\n"
    '    """Return subIndex entries with a valid subIndex (int >= 0), sorted ascending.\n'
    "\n"
    "    Entries where subIndex is absent, not an int, or < 0 are silently skipped.\n"
    '    """\n'
    "    result = []\n"
    '    for s in (data.get("subIndexes") or []):\n'
    "        if not isinstance(s, dict):\n"
    "            continue\n"
    '        si = s.get("subIndex")\n'
    "        if not (isinstance(si, int) and si >= 0):\n"
    "            continue\n"
    "        result.append(dict(s))\n"
    '    return sorted(result, key=lambda s: s["subIndex"])\n'
    "\n"
    "\n"
    "def _get_parts_list(subindex_data):\n"
    '    """Return parts from a subIndex object with a valid partsIndex (int >= 0), sorted ascending.\n'
    "\n"
    "    Parts where partsIndex is absent, not an int, or < 0 are silently skipped.\n"
    '    """\n'
    "    result = []\n"
    '    for p in (subindex_data.get("parts") or []):\n'
    "        if not isinstance(p, dict):\n"
    "            continue\n"
    '        pi = p.get("partsIndex")\n'
    "        if not (isinstance(pi, int) and pi >= 0):\n"
    "            continue\n"
    "        result.append(dict(p))\n"
    '    return sorted(result, key=lambda p: p["partsIndex"])'
)
assert old in src, "4 NOT FOUND"
src = src.replace(old, new, 1); changes.append("4 helpers")

# ── 5: _select_raw_values body ─────────────────────────────────────────────────
old = (
    "    raw = {}\n"
    "    for base_name, data in parts:\n"
    '        index    = data["index"]\n'
    '        subindex = data["subIndex"]\n'
    '        display  = data["name"]\n'
    '        use_random = kwargs.get(f"Random {display}", True)\n'
    "        parts_list = _get_parts_list(data)\n"
    "\n"
    "        if use_random:\n"
    "            for part in parts_list:\n"
    '                pi     = part["partsIndex"]\n'
    '                values = part.get("values") or []\n'
    '                raw[(index, subindex, pi)] = (rng.choice(values) if values else "").strip()\n'
    "        else:\n"
    '            manual = (kwargs.get(f"Value {display}") or "").strip()\n'
    "            for part in parts_list:\n"
    '                pi = part["partsIndex"]\n'
    '                raw[(index, subindex, pi)] = manual if pi == 0 else ""\n'
    "\n"
    "    return raw"
)
new = (
    "    raw = {}\n"
    "    for base_name, data in parts:\n"
    '        index      = data["index"]\n'
    '        display    = data["name"]\n'
    '        use_random = kwargs.get(f"Random {display}", True)\n'
    "        subindexes = _get_subindexes_list(data)\n"
    "\n"
    "        if use_random:\n"
    "            for sub_data in subindexes:\n"
    '                si = sub_data["subIndex"]\n'
    "                for part in _get_parts_list(sub_data):\n"
    '                    pi     = part["partsIndex"]\n'
    '                    values = part.get("values") or []\n'
    '                    raw[(index, si, pi)] = (rng.choice(values) if values else "").strip()\n'
    "        else:\n"
    '            manual   = (kwargs.get(f"Value {display}") or "").strip()\n'
    "            is_first = True\n"
    "            for sub_data in subindexes:\n"
    '                si = sub_data["subIndex"]\n'
    "                for part in _get_parts_list(sub_data):\n"
    '                    pi = part["partsIndex"]\n'
    '                    raw[(index, si, pi)] = manual if is_first else ""\n'
    "                    is_first = False\n"
    "\n"
    "    return raw"
)
assert old in src, "5 NOT FOUND"
src = src.replace(old, new, 1); changes.append("5 select_raw_values")

# ── 6: _apply_filters entries build ────────────────────────────────────────────
old = (
    "    # Build flat list sorted by (index, subIndex, partsIndex)\n"
    "    all_entries = []\n"
    "    for base_name, data in parts:\n"
    '        index      = data["index"]\n'
    '        subindex   = data["subIndex"]\n'
    "        use_random = kwargs.get(f\"Random {data['name']}\", True)\n"
    "        for part in _get_parts_list(data):\n"
    "            all_entries.append((index, subindex, part[\"partsIndex\"], use_random, part))\n"
    "    all_entries.sort(key=lambda x: (x[0], x[1], x[2]))"
)
new = (
    "    # Build flat list sorted by (index, subIndex, partsIndex)\n"
    "    all_entries = []\n"
    "    for base_name, data in parts:\n"
    '        index      = data["index"]\n'
    "        use_random = kwargs.get(f\"Random {data['name']}\", True)\n"
    "        for sub_data in _get_subindexes_list(data):\n"
    '            si = sub_data["subIndex"]\n'
    "            for part in _get_parts_list(sub_data):\n"
    "                all_entries.append((index, si, part[\"partsIndex\"], use_random, part))\n"
    "    all_entries.sort(key=lambda x: (x[0], x[1], x[2]))"
)
assert old in src, "6 NOT FOUND"
src = src.replace(old, new, 1); changes.append("6 apply_filters entries")

# ── 7: _combine_prompt full rewrite ────────────────────────────────────────────
old = (
    "def _combine_prompt(parts, final_values, id_lora):\n"
    '    """Step 4: group by index.\n'
    "\n"
    "    Separator logic is applied at two levels:\n"
    "\n"
    "    Part level (within a slot):\n"
    '      Normal parts (``separator: false``) are space-joined first.\n'
    '      Separator parts (``separator: true``) are comma-appended after.\n'
    '      Example: parts ["tall", "athletic", "curvy"(sep)] \u2192 "tall athletic, curvy"\n'
    "\n"
    "    Slot level (within an index):\n"
    '      Normal slots (``separator: false``) are space-joined.\n'
    '      Separator slots (``separator: true``) are comma-appended after.\n'
    '      Example: slots ["tall athletic", "freckled"(sep)] \u2192 "tall athletic, freckled"\n'
    "\n"
    "    After assembly, duplicate spaces and commas are cleaned up.\n"
    '    """\n'
    "    index_groups = {}\n"
    "    for base_name, data in parts:\n"
    '        index    = data["index"]\n'
    '        subindex = data["subIndex"]\n'
    '        is_sep   = bool(data.get("separator", False))\n'
    "\n"
    "        # \u2500\u2500 Part-level separator logic \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
    "        parts_list       = _get_parts_list(data)\n"
    "        normal_part_vals = []\n"
    "        sep_part_vals    = []\n"
    "        for p in parts_list:\n"
    '            v = final_values.get((index, subindex, p["partsIndex"]), "").strip()\n'
    "            if not v:\n"
    "                continue\n"
    '            if bool(p.get("separator", False)):\n'
    "                sep_part_vals.append(v)\n"
    "            else:\n"
    "                normal_part_vals.append(v)\n"
    "\n"
    '        normal_str = " ".join(normal_part_vals)\n'
    "        pieces     = ([normal_str] if normal_str else []) + sep_part_vals\n"
    '        slot_val   = ", ".join(pieces)\n'
    "\n"
    '        grp = index_groups.setdefault(index, {"normal": [], "sep": []})\n'
    "        if is_sep:\n"
    "            grp[\"sep\"].append((subindex, slot_val))\n"
    "        else:\n"
    "            grp[\"normal\"].append((subindex, slot_val))\n"
    "\n"
    "    index_results = []\n"
    "    for idx in sorted(index_groups.keys()):\n"
    "        grp = index_groups[idx]\n"
    '        normal_items = sorted(grp["normal"], key=lambda x: x[0])\n'
    '        sep_items    = sorted(grp["sep"],    key=lambda x: x[0])\n'
    "\n"
    '        normal_str  = " ".join(v.strip() for _, v in normal_items if v.strip())\n'
    "        sep_strings = [v.strip() for _, v in sep_items if v.strip()]\n"
    "\n"
    "        pieces   = ([normal_str] if normal_str else []) + sep_strings\n"
    '        combined = ", ".join(pieces)\n'
    "        if combined:\n"
    "            index_results.append(combined)\n"
    "\n"
    "    id_str = (id_lora or \"\").strip()\n"
    "    if id_str:\n"
    "        index_results.insert(0, id_str)\n"
    "\n"
    '    return _clean_prompt(", ".join(index_results))'
)
new = (
    "def _combine_prompt(parts, final_values, id_lora):\n"
    '    """Step 4: assemble the final prompt.\n'
    "\n"
    "    Separator logic is applied at three levels, innermost first:\n"
    "\n"
    "    Part level (within a subIndex):\n"
    "      Normal parts are space-joined; separator parts are comma-appended after.\n"
    '      Example: ["tall", "athletic", "curvy"(sep)] \u2192 "tall athletic, curvy"\n'
    "\n"
    "    SubIndex level (within an index):\n"
    "      Normal subIndexes are space-joined; separator subIndexes are comma-appended.\n"
    '      Example: ["tall athletic", "freckled"(sep)] \u2192 "tall athletic, freckled"\n'
    "\n"
    "    Index level (final output):\n"
    "      All index results are comma-joined.\n"
    "\n"
    "    After assembly, duplicate spaces and commas are cleaned up.\n"
    '    """\n'
    "    index_results = []\n"
    "    for base_name, data in sorted(parts, key=lambda x: x[1][\"index\"]):\n"
    '        index      = data["index"]\n'
    "        subindexes = _get_subindexes_list(data)\n"
    "\n"
    "        normal_sub_vals = []\n"
    "        sep_sub_vals    = []\n"
    "\n"
    "        for sub_data in subindexes:\n"
    '            si         = sub_data["subIndex"]\n'
    '            is_sep_sub = bool(sub_data.get("separator", False))\n'
    "\n"
    "            # \u2500\u2500 Part-level separator logic \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
    "            normal_part_vals = []\n"
    "            sep_part_vals    = []\n"
    "            for p in _get_parts_list(sub_data):\n"
    '                v = final_values.get((index, si, p["partsIndex"]), "").strip()\n'
    "                if not v:\n"
    "                    continue\n"
    '                if bool(p.get("separator", False)):\n'
    "                    sep_part_vals.append(v)\n"
    "                else:\n"
    "                    normal_part_vals.append(v)\n"
    "\n"
    '            normal_str = " ".join(normal_part_vals)\n'
    "            pieces     = ([normal_str] if normal_str else []) + sep_part_vals\n"
    '            sub_val    = ", ".join(pieces)\n'
    "\n"
    "            if not sub_val:\n"
    "                continue\n"
    "            if is_sep_sub:\n"
    "                sep_sub_vals.append(sub_val)\n"
    "            else:\n"
    "                normal_sub_vals.append(sub_val)\n"
    "\n"
    "        # \u2500\u2500 SubIndex-level separator logic \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
    '        normal_str   = " ".join(normal_sub_vals)\n'
    "        pieces       = ([normal_str] if normal_str else []) + sep_sub_vals\n"
    '        index_result = ", ".join(pieces)\n'
    "        if index_result:\n"
    "            index_results.append(index_result)\n"
    "\n"
    "    id_str = (id_lora or \"\").strip()\n"
    "    if id_str:\n"
    "        index_results.insert(0, id_str)\n"
    "\n"
    '    return _clean_prompt(", ".join(index_results))'
)
assert old in src, "7 NOT FOUND"
src = src.replace(old, new, 1); changes.append("7 combine_prompt")

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(src)

print("Python changes applied:", changes)

# ── 8: convert all JSON files ──────────────────────────────────────────────────
for fname in sorted(os.listdir(DATA_DIR)):
    if not fname.endswith('.json') or fname == 'example.json':
        continue
    fpath = os.path.join(DATA_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        d = json.load(f)

    if 'subIndexes' in d:
        print(f'SKIP (already converted): {fname}')
        continue

    sub_obj = {
        'subIndex':  d.get('subIndex', 0),
        'separator': d.get('separator', False),
        'parts':     d.get('parts', []),
    }
    new_d = {
        'name':       d['name'],
        'index':      d['index'],
        'separator':  False,
        'subIndexes': [sub_obj],
    }
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(new_d, f, indent=2, ensure_ascii=False)
    print(f'UPDATED: {fname}')

# ── 9: syntax check ────────────────────────────────────────────────────────────
import ast
ast.parse(open(PATH, encoding='utf-8').read())
print('Python syntax: OK')
for fname in sorted(os.listdir(DATA_DIR)):
    if fname.endswith('.json'):
        json.load(open(os.path.join(DATA_DIR, fname), encoding='utf-8'))
        print(f'JSON OK: {fname}')
