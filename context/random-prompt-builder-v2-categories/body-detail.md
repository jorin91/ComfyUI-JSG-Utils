# Body Detail Category

## Purpose

The body detail category is reserved for regional body structure, body regions, body parts, body subparts, local surface details, regional bone definition, and regional tanning.

Before adding or changing any Body Detail value, builder, generator, state, tag, condition, or validation, check `context/random-prompt-builder-v2-category-relations.md`. Update that central relation map immediately if the change creates or changes any relation with Subject/Content, Clothing coverage, Body Build, Action, Pose, or Style.

Use Body Detail for anything limited to a smaller area of the body. Body Build remains the general whole-body category.

## Current State

Implemented category file:

- `data/random_prompt_builder_v2/categories/body_detail.json`

Old empty Body Detail scaffolds were removed from the active category file. Reintroduce a body part, subpart, or regional detail only when the user requests concrete outcomes for it.

Active filled Body Detail routes:

- `builder.body_detail.hair_style` resolves through `generator.body_detail.hair_style` and exports `body_detail.hair_style`.
- `builder.body_detail.hair_color` resolves through `generator.body_detail.hair_color` and exports `body_detail.hair_color`.
- `builder.body_detail.breasts` resolves one breast-size route through cup-size wording, development-style wording, or NSFW contextual wording, and exports `body_detail.breasts`.

Hair style and hair color are safe for all ages and do not validate against `subject.adult` or `content.nsfw_allowed`.
Some hairstyle values validate against `subject.gender` when their wording is intentionally male-coded or female-coded. If `subject.gender` is missing, only ungendered hairstyle values remain available.

Breast values validate through `subject.gender=female`. The breast builder has one route for cup-size wording, one route for development-style wording, and one route for NSFW contextual size wording; do not split those routes into separate small/large generators. Each generator contains its full scale, and the individual values own the broad `subject.age_phase` max-size validation. Missing `subject.age_phase`, such as when Subject is manually overridden, keeps the full neutral size/development range available so manual text remains user-controlled. Prompt-facing breast-size text must not include age words such as `adult`; age belongs in Subject state, not in body-size wording.

Neutral cup-size values start at `subject.age_phase=preteen` because cup labels are only used once visible breast development can exist. Neutral development values use both lower-start and max-size validation: absolute no-development/no-visible-development values are valid for every age phase; flat, barely-any, minimal, very-low, low, and slight development values start at `subject.age_phase=child`; petite and small visible development starts at `subject.age_phase=preteen`; higher development stages are phase-limited by maximum. The lower values must remain available for older subjects too, because "too small for age" is not a validation failure. Breast-owned prompt text should use breast/breasts wording rather than chest wording so the model sees the intended body-part ownership. NSFW breast-size wording additionally validates through `content.nsfw_allowed=true` and `subject.adult=true`, covers the lower flat/nearly-flat/tiny range before moving into small, full, and extreme wording, and also avoids age words in prompt text.

The previous concrete regional body-detail vocabulary and `body.*.coverage` validation were removed from the active baseline. Reintroduce them only when the user provides concrete desired body-detail outcomes.

## Organization Rule

Body Detail should use one active builder per body part. A body-part builder may contain multiple sibling value routes for different aspects, but the builder still emits only one selected aspect per prompt.

Rules:

- Hair is currently represented as two compatible builders: hairstyle and hair color. Keep them separate so a style and color can coexist without one broad generator blocking the other.
- Per body part, not subpart, keep only one active builder and one emitted aspect. For example, breasts have one builder whether the selected aspect is size, development, shape, skin, tanning, or another future breast-owned aspect.
- Subparts may have their own builder when requested. One breast value may coexist with one areola value and one nipple value because areola and nipples are subparts, not separate breast body-part builders.
- Do not collapse multi-region aspects into one broad generator if that prevents multiple compatible details from being selected together.
- Bone definition should use regional builders/generators when reintroduced because collarbones, ribs, pelvis/hips, and limb joints can coexist. If the region is a body part with an existing builder, add the bone-detail route inside that body-part builder instead of adding a second builder for that same body part.
- Tanning should use regional builders/generators when reintroduced because abdomen tan lines, breast tan lines, pelvic tan lines, and buttock tan lines can coexist across different body parts. Breast tanning, if reintroduced, belongs as a sibling route inside the single breast builder.
- Muscle and toning may share a builder/generator when they represent the same surface-definition role for that region.
- Add new region-specific generators only when a region needs its own vocabulary, coverage gate, or grammar.

Default hierarchy:

1. broad body region;
2. specific region;
3. body part;
4. body subpart;
5. local surface/aspect detail.

Promotion rule:

- keep a detail in the broadest logical regional builder until there are at least three concrete outputs that justify a more specific builder/group;
- promote to a more specific builder/group at three or more concrete outputs;
- when a more specific builder/group is promoted, move the relevant values and generators with it so the structure stays readable;
- apply the same promotion rule to both builders and universal generators;
- do not create empty future builders or generator groups just because the hierarchy might need them later.

## Coverage / Exposed State Rules

Body Detail follows coverage-first logic:

- A specified value can tell us what is covered or exposed; an unspecified value does not prove either.
- Add only the coverage/exposed states needed by concrete detail values.
- Do not create body-wide state grids up front.
- Check relevant clothing options before adding a detail value that depends on a body region being visible.
- If clothing coverage is uncertain, take the safe route and avoid selecting exposed-region details unless a concrete higher-priority aspect exposes that region.
- Clothing aspects may directly affect detail eligibility when they explicitly mention nudity, bare skin, displaced garments, open garments, transparency, or similar visibility.
- State priority is part of the contract: default priority `0`; only strictly higher priority overwrites; equal priority does not.

Do not document or implement individual coverage state keys until concrete Body Detail, clothing, or pose usage requires them.
