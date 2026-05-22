# Ethnicity Category

## Purpose

The ethnicity category creates ethnicity origin wording and compatible skin-tone wording as separate prompt elements from universal generators.

Before adding or changing any Ethnicity value, builder, generator, state, tag, condition, or validation, check `context/random-prompt-builder-v2-category-relations.md`. Update that central relation map immediately if the change creates or changes any relation with Body, Clothing, Style, Subject, or ethnicity-internal compatibility.

Current builder pattern:

- `builder.ethnicity.base_mix` owns `{base}` and `{mix}` and produces the ethnicity origin phrase;
- `builder.ethnicity.skin_tone` owns `{skin_tone}` and produces a separate skin-tone prompt element after `ethnicity.base` exists;
- `generator.ethnicity.base` sets `ethnicity.base`;
- `generator.ethnicity.mix` and `generator.ethnicity.skin_tone` filter by `ethnicity.base`.
- the base/mix builder exports `{base}` and `{mix}` into `ethnicity.base` and `ethnicity.mix`; the skin-tone builder exports `{skin_tone}` into `ethnicity.skin_tone`.
- Keep skin tone separate from the ethnicity origin phrase. Combining origin and skin-tone in one long sentence can become less logical for the image model to follow.
- Skin-tone prompt values should explicitly include `skin color`, such as `light olive skin color`, so the model receives the value as color wording rather than a vague skin descriptor.
- Ethnicity variation should be increased through neutral base heritage/subregion labels, optional mixed-heritage labels, and compatible skin-color tint ranges.
- Do not add stereotype facial-feature, body-shape, clothing, attractiveness, or style assumptions to ethnicity values. Those belong in their own categories only when explicitly requested and documented.

Ethnicity generators must remain universal. They must use state/tag conditions, not builder-slot conditions.

Current scale:

- `generator.ethnicity.base`: expanded broad and subregional heritage/ethnicity labels.
- `generator.ethnicity.mix`: mirrors the base list as optional mixed-heritage wording while filtering out the selected base.
- `generator.ethnicity.skin_tone`: expanded compatible `skin color` tint values with broader per-base compatibility so repeated bases can still vary visually.

## Current State

- `ethnicity.base`
- `ethnicity.mix`
- `ethnicity.skin_tone`

See `context/random-prompt-builder-v2-states.md` for the authoritative state index.
