src = open(r'e:\ComfyUI\App\custom_nodes\ComfyUI-JSG-Utils\nodes\JSGRandomPromptBuilder.py', encoding='utf-8').read()
checks = [
    ('1 docstring',       'subIndexes (non-empty list)'),
    ('2 validation',      "subIndexes' must be a non-empty array"),
    ('3 sort+dedup',      'return d["index"]'),
    ('4 helpers',         '_get_subindexes_list'),
    ('5 select_raw',      'is_first = True'),
    ('6 apply_filters',   'for sub_data in _get_subindexes_list(data)'),
    ('7 combine_prompt',  'for base_name, data in sorted(parts'),
]
for label, needle in checks:
    print(label, ':', 'YES' if needle in src else 'NO')
