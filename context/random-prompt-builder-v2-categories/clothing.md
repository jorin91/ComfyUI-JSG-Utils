# Clothing Category

## Purpose

The clothing category now uses a small authored-prompt structure instead of many random clothing item/aspect layers.

Before adding or changing any Clothing value, builder, generator, state, tag, condition, or validation, check `context/random-prompt-builder-v2-category-relations.md`. Update that central relation map immediately if the change creates or changes any relation with Body Detail, Action, Pose, Subject/Content, or future Environment logic.

The nude/clothed state remains. Broad clothing styles remain. All former coat, shirt, bottom, underwear, swimwear, footwear, socks, color, and aspect scaffolds have been removed from V2 clothing.

## Current Builder Order

`data/random_prompt_builder_v2/categories/clothing.json` resolves clothing builders in this order:

1. `builder.clothing.coverage`
2. `builder.clothing.style`
3. `builder.clothing.whole`
4. `builder.clothing.upper_body`
5. `builder.clothing.lower_body`

`builder.clothing.coverage` is the route selector:

- `nude` emits `nude`, validates on `subject.adult=true`, `content.nsfw_allowed=true`, and `environment.clothing.theme.nude=true`, then sets `clothing.coverage=nude`;
- `clothed` validates on `content.sfw_allowed=true`, emits no text, and sets `clothing.coverage=clothed`.

Every prompt-bearing clothing builder after coverage validates on `clothing.coverage=clothed`.

Clothing existence is intentionally separate from `clothing.coverage`. The clothed coverage route only means the SFW-gated clothed route was selected; it does not prove that a clothing prompt was emitted.

Current clothing-to-pose existence state:

- None active. Clothing-adjustment moved to Action, and current Pose wording is static body placement that can work over clothing or without clothing.

Do not recreate Clothing-to-Pose states unless a concrete future Pose value truly requires a garment, underwear, swimwear, nudity, or exact covered/exposed body state.

Current clothing-to-action existence states:

- `clothing.action.exist`: set by prompt-bearing clothing builders when they produce non-empty clothing text and Action needs to know clothing exists.
- `clothing.action.upper_body.exist`: set by prompt-bearing style/whole/upper-body clothing builders when Action needs upper-body clothing.
- `clothing.action.lower_body.exist`: set by prompt-bearing style/whole/lower-body clothing builders when Action needs lower-body clothing.
- `clothing.action.underwear.exist`: set by concrete generator values that explicitly imply underwear and Action needs that fact.
- `clothing.action.swimwear.exist`: set by concrete generator values that explicitly imply swimwear and Action needs that fact.

## Kept Style Route

`builder.clothing.style` still draws from `generator.clothing.style`.

When a real style is selected, the style builder exports the chosen `{style}` slot into `clothing.style`. This state marks that the clothing category already has a broad complete outfit direction.

The style builder also sets `clothing.action.exist=true`, `clothing.action.upper_body.exist=true`, and `clothing.action.lower_body.exist=true` at builder level, but only when the selected style route emits non-empty text. Empty style skips must not set target-specific clothing existence.

Every real style value validates against an Environment-owned clothing theme state. This is soft setting direction, not a strict social dress-code system. Environment location values write broad accepted themes under `environment.clothing.theme.*`, the blank/no-location fallback accepts every theme, and Environment must resolve before Clothing so those states already exist.

The `underwear outfit` value sets `clothing.action.underwear.exist=true` and is additionally gated by `subject.adult=true` plus `content.nsfw_allowed=true`. The `swimwear outfit` value sets `clothing.action.swimwear.exist=true`.

`clothing.style` may intentionally skip through its generator-level empty options. In that case `clothing.coverage=clothed` remains set, but no broad style state is written and authored clothing routes may try to fill clothing if their generators contain real values. Do not add a duplicate builder-level empty value to generator-backed clothing template builders.

Current style values are broad outfit/style directions rather than exact clothing prompts:

- underwear outfit;
- swimwear outfit;
- everyday outfit;
- sportswear;
- evening wear;
- sleepwear;
- pajamas;
- leisurewear;
- workwear;
- party outfit;
- spring outfit;
- summer outfit;
- autumn outfit;
- winter outfit.

Styles are intentionally broad. They should not grow into detailed outfit sentences. A selected style leaves concrete clothing variation to the image model.

If `clothing.style` state exists, the authored clothing routes must skip. Detailed authored clothing belongs in the whole/upper/lower generators only when style did not provide clothing output.

Only style values that explicitly imply underwear or swimwear set the matching `clothing.action.underwear.exist` or `clothing.action.swimwear.exist` states.

Current style-to-theme mapping:

- underwear outfit: `environment.clothing.theme.underwear_swimwear` plus adult/NSFW gate;
- swimwear outfit: `environment.clothing.theme.underwear_swimwear`;
- sportswear: `environment.clothing.theme.sport`;
- sleepwear and pajamas: `environment.clothing.theme.sleep`;
- workwear: `environment.clothing.theme.work`;
- everyday outfit and leisurewear: `environment.clothing.theme.casual`;
- spring, summer, autumn, and winter outfit: `environment.clothing.theme.seasonal`;
- evening wear and party outfit: `environment.clothing.theme.party`.

## New Authored Clothing Routes

The new empty generator scaffold is:

- `generator.clothing.sfw.whole`
- `generator.clothing.nsfw.whole`
- `generator.clothing.sfw.upper_body`
- `generator.clothing.nsfw.upper_body`
- `generator.clothing.sfw.lower_body`
- `generator.clothing.nsfw.lower_body`

Values in these generators are complete authored prompt fragments. A value may contain commas and should be logically complete on its own, for example an entire layered clothing situation rather than a single item plus unrelated random aspects.

Validation contract:

- `builder.clothing.whole` requires `clothing.coverage=clothed` and `clothing.style` to be missing.
- `builder.clothing.upper_body` requires `clothing.coverage=clothed`, `clothing.style` to be missing, and `clothing.whole` to be missing.
- `builder.clothing.lower_body` requires `clothing.coverage=clothed`, `clothing.style` to be missing, and `clothing.whole` to be missing.

This means clothing resolves as `style OR whole OR upper+lower`. A style value wins over all authored values. A whole-body authored outfit wins over separate upper/lower authored values. Upper and lower are only allowed when neither style nor whole-body clothing prompt has been selected.

Builder-level Action-targeted states on authored clothing routes:

- non-empty `builder.clothing.whole` sets `clothing.action.exist`, `clothing.action.upper_body.exist`, and `clothing.action.lower_body.exist`;
- non-empty `builder.clothing.upper_body` sets `clothing.action.exist` and `clothing.action.upper_body.exist`;
- non-empty `builder.clothing.lower_body` sets `clothing.action.exist` and `clothing.action.lower_body.exist`.

If a future authored clothing value explicitly contains underwear or swimwear for Action compatibility, set the matching target-specific state on that generator value rather than repeating validation across action values.

Example classification rule:

- `Wearing a bikini, a shirt over the bikini top, shirt being wet and showing everything underneath` is SFW if the authored outcome still has a complete bikini under the shirt and is not directly nude.

## SFW/NSFW Split

Use SFW generators for clothing outcomes that remain dressed, covered, or otherwise safe even if the wording is suggestive, wet, layered, or visually detailed.

Use NSFW generators only for adult/NSFW steering, direct visible nudity, missing clothing that creates visible nudity, or explicit exposure-focused clothing outcomes.

The NSFW builder routes are value-gated by:

- `subject.adult=true`
- `content.nsfw_allowed=true`

Do not mix SFW and NSFW values in one generator.

## Refill Rules

Add clothing vocabulary only as small authored outcomes from explicit desired results.

Rules:

- Prefer one complete whole-body value when the clothing concept needs top and bottom to stay coordinated.
- Use upper/lower values only when the concept can safely vary by body half without causing contradictions.
- Do not rebuild the old item/aspect matrix.
- Do not split a coherent authored phrase into random color/material/item/fit/aspect generators unless a future concrete need proves it is still coherent.
- Keep values concise enough that the image model is steered, not overloaded.
- If a value requires several exact garments to remain logical, keep them together in one authored value.

## Filtering Model

Filtering should stay limited.

Current intended filters:

- nude/clothed route;
- Environment location clothing themes;
- selected broad clothing style blocking authored routes;
- whole-body route blocking upper/lower routes;
- SFW versus NSFW generator route;
- whole-body versus upper-body versus lower-body builder placement.

Add extra state validation only when a concrete value introduces a real conflict with body visibility, action, pose, environment, or another clothing route.

## Removed Old Model

Do not reintroduce the previous V2 clothing design by default:

- no separate coat/shirt/bottom/underwear/swimwear/footwear/socks builders;
- no clothing color generator family;
- no pre/post clothing aspect generator family;
- no generator matrix that randomly combines item, material, fit, wetness, transparency, damage, and exposure.

The new clothing model relies on curated complete values so combinations are authored for coherence before they are random-selected.
