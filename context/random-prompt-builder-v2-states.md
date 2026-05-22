# Random Prompt Builder V2 States

## Purpose

This file is the state index for `JSGRandomPromptBuilderV2`.

Use it before adding `state_set` or `state` conditions so we do not invent duplicate or conflicting state keys.

States start from absolute null. Do not add planned states here. Add a state only when a concrete builder/value actually sets or validates it.

State writes have optional priority metadata. When no priority is specified, priority is `0`. A state write only overwrites an existing state key when its priority is strictly higher than the existing write's priority; equal priority does not overwrite. Conditions still read the plain state value.

Priority exists for concrete conflict handling, especially future clothing/body coverage facts. Do not add priority noise where normal non-conflicting state writes are enough.

Each state entry must include:

- type;
- meaning;
- where it is set;
- where it is used/validated;
- notes when needed.

Generators are universal and must not validate against builder slots. If a universal generator value needs a fact selected elsewhere, that fact must be exposed as state by the earlier selected value/builder.

Coverage/exposed states should remain sparse. Add a body-region coverage state only when a concrete Body Detail, clothing, pose, or aspect value sets or validates it. Prefer coverage facts because specified garments/aspects can tell us what they cover; unspecified facts do not prove exposure.

## Reset Baseline

The current V2 data has been intentionally reset to a small baseline.

Kept filled:

- Subject values;
- Ethnicity values;
- Body Build physical trait and proportions values;
- Clothing coverage route: nude or clothed;
- Clothing style values.
- General, sport/movement, NSFW non-sexual, and one sexual mirror Action value.

Reset to empty:

- old explicit clothing piece values and generators;
- old clothing aspect generators;
- Profession Action values;
- Lighting, Style, and Quality scaffolds.

Environment has been partially reintroduced with indoor/outdoor domain, locations, room/area values, surface phrases, seasons, weather, and time/daypart values.
Action has been partially reintroduced with general movement/rest/everyday actions, sport/movement actions, adult/NSFW-gated private/visibility actions, and explicit sexual actions.
Pose has been partially reintroduced with general pose values, adult/NSFW-gated sensitive pose values, and explicit sexual pose values.
Body Detail has been partially reintroduced with safe-for-all-ages hair style and hair color values.
Body Detail also has one female breast body-part builder that exports the selected breast-size phrase to `body_detail.breasts`.
Body Build has been partially reintroduced with one broad physical trait builder and one whole-body proportions builder.

Only states used by the kept baseline, active state profiles, and reintroduced Environment/Action/Pose/Body Detail/Body Build values are current states below. Previous body coverage, clothing item, and missing-clothing states are no longer documented as current states until concrete values are reintroduced.

## Current States

### `content.sfw_allowed`

Type: boolean

Meaning:

- Controls whether SFW-only values/routes are allowed.
- `true` allows non-adult generated subjects and future SFW-only values.
- `false` blocks non-adult generated subjects for NSFW-only profiles.

Set by:

- `data/random_prompt_builder_v2/state_profiles/*.json`

Used by:

- `data/random_prompt_builder_v2/categories/subject.json`
- `data/random_prompt_builder_v2/categories/clothing.json`

Notes:

- Current SFW and Mixed profiles set this to `true`.
- Current NSFW profiles set this to `false`.
- Non-adult generated Subject values validate on this state.
- The `clothing.coverage=clothed` route validates on this state. NSFW-only profiles should not silently fall back to the clothed coverage route.

### `content.nsfw_allowed`

Type: boolean

Meaning:

- Controls whether NSFW-gated routes are allowed.
- `true` allows adult NSFW clothing, action, pose, and visibility-oriented routes when the selected subject is adult.
- `false` blocks NSFW routes even when `subject.adult=true`.

Set by:

- `data/random_prompt_builder_v2/state_profiles/*.json`

Used by:

- `data/random_prompt_builder_v2/categories/clothing.json`
- `data/random_prompt_builder_v2/categories/body_detail.json`
- `data/random_prompt_builder_v2/categories/action.json`
- `data/random_prompt_builder_v2/categories/pose.json`
- `data/random_prompt_builder_v2/categories/composition.json`

Notes:

- This is separate from `subject.adult`.
- Current NSFW and Mixed profiles set this to `true`.
- Current SFW profiles set this to `false`.
- NSFW means the gated adult-sensitive route, not necessarily a sexual act.
- Explicitly sexual routes also validate through this state plus `subject.adult=true`.

### `composition.framing`

Type: string

Meaning:

- The selected Composition framing phrase.
- Stores shot distance, crop, or subject placement such as full body, close-up, tight crop, or centered framing.

Set by:

- `data/random_prompt_builder_v2/categories/composition.json`

Used by:

- Not currently validated by another category.

Notes:

- This is a debug/state-discipline state, not a dependency contract.

### `composition.focus_perspective`

Type: string

Meaning:

- The selected Composition focus/perspective phrase.
- Stores general solo-subject emphasis or adult/NSFW-gated sensitive body-region focus.

Set by:

- `data/random_prompt_builder_v2/categories/composition.json`

Used by:

- Not currently validated by another category.

Notes:

- NSFW focus values are gated by `subject.adult=true` and `content.nsfw_allowed=true`.
- No sexual focus generator exists for Composition while the prompt model targets a solo person.

### `composition.angle_position`

Type: string

Meaning:

- The selected Composition camera angle or position phrase.
- Stores broad viewpoint variation such as front view, high angle, low angle, or close camera position.

Set by:

- `data/random_prompt_builder_v2/categories/composition.json`

Used by:

- Not currently validated by another category.

Notes:

- Orientation values are intentionally excluded because latent resolution owns portrait/landscape orientation.

### `profile.content_mode`

Type: string

Meaning:

- The selected global profile content mode.
- Current values are `sfw`, `nsfw`, and `mixed`.

Set by:

- `data/random_prompt_builder_v2/state_profiles/*.json`

Used by:

- Future category values only when a concrete option needs to distinguish SFW-only, NSFW-only, or Mixed profile intent.

Notes:

- Prefer `content.sfw_allowed` and `content.nsfw_allowed` for ordinary allow/deny validation.
- Use this mode only when the distinction between SFW-only, NSFW-only, and Mixed matters beyond simple allow states.
- Do not use this as a routine NSFW gate; prefer `content.nsfw_allowed` plus `subject.adult`.

### `profile.gender_mode`

Type: string

Meaning:

- The selected global profile gender mode.
- Current values are `any`, `female`, and `male`.

Set by:

- `data/random_prompt_builder_v2/state_profiles/*.json`

Used by:

- `data/random_prompt_builder_v2/categories/subject.json`
- Future category values only when a concrete option needs to know the requested profile gender mode.

Notes:

- Gender-specific profiles also seed `subject.gender` at fallback priority.
- Generated Subject values validate against this state before they may overwrite `subject.gender`: `female` profiles allow only female Subject values, `male` profiles allow only male Subject values, and `any` profiles allow both.
- Use `subject.gender` for the actual selected/generated subject and `profile.gender_mode` for the requested profile mode.

### `activity.route`

Type: string enum

Values:

- `action`
- `pose`

Meaning:

- Internal random route state that decides whether random Action or random Pose is allowed for the current build.

Set by:

- `nodes/JSGRandomPromptBuilderV2.py`

Used by:

- `data/random_prompt_builder_v2/categories/action.json`
- `data/random_prompt_builder_v2/categories/pose.json`

Notes:

- The route is selected before category generation.
- The route choice includes only Action/Pose categories whose random toggle is enabled.
- If both Action and Pose random toggles are enabled, the route is randomly selected.
- If only one of Action/Pose is random-enabled, the route selects that side.
- Disabled-random Action/Pose categories are excluded from the random route choice.
- Manual override text bypasses route validation and is emitted directly when the matching random toggle is disabled.
- Disabled random plus an empty override intentionally emits no category text.

### `action.general`

Type: string

Meaning:

- The selected general action phrase.

Set by:

- `data/random_prompt_builder_v2/categories/action.json`

Used by:

- Future action, pose, environment, or debug logic only when a concrete need appears.

Notes:

- Current values come from `generator.action.general`.
- This is prompt-state tracking only.

### `action.sport`

Type: string

Meaning:

- The selected sport, gymnastics, yoga, fitness, or dance action phrase.

Set by:

- `data/random_prompt_builder_v2/categories/action.json`

Used by:

- Future action, pose, environment, or debug logic only when a concrete need appears.

Notes:

- Current values come from `generator.action.sport` through the sport route value inside `builder.action`.
- This is prompt-state tracking only.

### `action.nsfw`

Type: string

Meaning:

- The selected adult/NSFW-gated action phrase.
- These values are private, visibility/nudity-oriented, or sensitive actions, not automatically sexual acts.

Set by:

- `data/random_prompt_builder_v2/categories/action.json`

Used by:

- Future action, pose, environment, or debug logic only when a concrete need appears.

Notes:

- Current values come from `generator.action.nsfw` through the NSFW route value inside `builder.action`.
- The NSFW route value is gated by `subject.adult=true` plus `content.nsfw_allowed=true`.
- Keep sexual route values reserved for explicit sexual acts or sex-contextual actions.
- Clothing-displacement exposure actions for breasts, buttocks, vulva, penis, and anus live here because they are nudity/visibility-directed actions, not necessarily sex acts. They validate against upper/lower `clothing.action.*.exist` state and gender where needed.

### `action.sexual`

Type: string

Meaning:

- The selected adult/sexual action phrase.
- These values are explicitly sexual or sex-contextual actions, not merely NSFW/private/revealing actions.

Set by:

- `data/random_prompt_builder_v2/categories/action.json`

Used by:

- Future action, pose, environment, or debug logic only when a concrete need appears.

Notes:

- Current values come from three sexual route values inside `builder.action`: standalone `generator.action.sexual`, modular penetration slots, and modular stimulation slots.
- Sexual route values are gated by `subject.adult=true` plus `content.nsfw_allowed=true`.
- NSFW mirror posing stays in `action.nsfw`; only explicitly sexual mirror posing belongs here.
- Current sexual actions include modular stimulation, modular penetration/object oral-sex, labia spreading, buttocks spreading for anal visibility, oral-sex gesture, and sexual mirror posing.
- Stimulation and penetration intentionally do not validate against clothing unless the wording explicitly moves clothing, because clothing presence/absence is allowed to vary.

### `action.sexual.penetration.bodypart`

Type: string

Meaning:

- Internal route state for the modular sexual penetration builder value. It emits no prompt text by itself; it only lets later slots choose compatible wording.
- Current values are `anus`, `vagina`, and `mouth`.

Set by:

- `data/random_prompt_builder_v2/shared_generators/action.json`

Used by:

- `data/random_prompt_builder_v2/categories/action.json`
- `data/random_prompt_builder_v2/shared_generators/action.json`

Notes:

- `vagina` validates against `subject.gender=female`.
- `mouth` routes to object oral-sex wording.
- This state is used to select compatible penetration action mode, prefix, and suffix wording inside one builder value.

### `action.sexual.penetration.action`

Type: string

Meaning:

- Internal route state for the modular sexual penetration action mode. It emits no prompt text by itself; it only lets later slots choose compatible wording.
- Current values are `self_penetrating`, `oral_object`, `riding`, `sitting_onto`, and `using_for_penetration`.

Set by:

- `data/random_prompt_builder_v2/shared_generators/action.json`

Used by:

- `data/random_prompt_builder_v2/categories/action.json`

Notes:

- `oral_object` validates against `action.sexual.penetration.bodypart=mouth`.
- The other current modes validate against `action.sexual.penetration.bodypart` in `anus` or `vagina`.
- This state lets one penetration builder value produce varied prompt grammar without turning every object/action combination into a separate random option.

### `action.sexual.penetration.object`

Type: string

Meaning:

- The selected object phrase for the modular penetration/object oral-sex route.

Set by:

- `data/random_prompt_builder_v2/categories/action.json`

Used by:

- Future action or prompt-debug logic only when a concrete need appears.

Notes:

- Values come from `generator.action.sexual.penetration.object`.
- Current object values include banana, cucumber, dildo, vibrator, butt plug, glass dildo, pencil, hairbrush handle, toothbrush handle, marker, closed lipstick tube, remote control, and paintbrush handle.

### `action.sexual.stimulation.target`

Type: string

Meaning:

- Internal route state for the modular sexual stimulation builder value. It emits no prompt text by itself; it only lets later slots choose compatible wording.
- Current values include `breasts`, `nipples`, `vulva`, `clitoris`, `penis`, `anus`, `buttocks`, `vulva_surface`, and `penis_surface`.

Set by:

- `data/random_prompt_builder_v2/shared_generators/action.json`

Used by:

- `data/random_prompt_builder_v2/categories/action.json`
- `data/random_prompt_builder_v2/shared_generators/action.json`

Notes:

- Female-specific targets validate against `subject.gender=female`.
- Penis targets validate against `subject.gender=male`.
- Surface targets require `generator.action.sexual.stimulation.surface` to render a surface/object after the stimulation action text.

### `action.sexual.stimulation.surface`

Type: string

Meaning:

- The selected surface/object phrase for modular surface-based sexual stimulation.

Set by:

- `data/random_prompt_builder_v2/categories/action.json`

Used by:

- Future action or prompt-debug logic only when a concrete need appears.

Notes:

- Values come from `generator.action.sexual.stimulation.surface`.
- This state is only exported when the selected stimulation target is `vulva_surface` or `penis_surface`.

### `clothing.action.exist`

Type: boolean

Meaning:

- A non-empty clothing prompt route was selected and Action needs to know that clothing exists.
- This is a Clothing-owned, Action-targeted compatibility state.

Set by:

- `data/random_prompt_builder_v2/categories/clothing.json`

Used by:

- `data/random_prompt_builder_v2/shared_generators/action.json`

Notes:

- Set at builder level by prompt-bearing clothing builders after a non-empty clothing result.
- Current clothing-change and generic clothing-adjustment actions validate against this state.
- This is not a generic clothing fact for every target. Pose currently has no clothing-targeted validation state.

### `clothing.action.upper_body.exist`

Type: boolean

Meaning:

- A non-empty clothing prompt route exists for the upper body and Action needs that fact.
- This is a Clothing-owned, Action-targeted compatibility state.

Set by:

- `data/random_prompt_builder_v2/categories/clothing.json`

Used by:

- `data/random_prompt_builder_v2/shared_generators/action.json`

Notes:

- Current style, whole-body, and upper-body clothing builders set this at builder level after non-empty output.
- Current upper-clothing adjustment and upper-body clothing-displacement exposure actions validate against this state.
- Do not infer this from `clothing.coverage=clothed`.
- Do not use Pose-targeted keys for Action validation.

### `clothing.action.lower_body.exist`

Type: boolean

Meaning:

- A non-empty clothing prompt route exists for the lower body and Action needs that fact.
- This is a Clothing-owned, Action-targeted compatibility state.

Set by:

- `data/random_prompt_builder_v2/categories/clothing.json`

Used by:

- `data/random_prompt_builder_v2/shared_generators/action.json`

Notes:

- Current style, whole-body, and lower-body clothing builders set this at builder level after non-empty output.
- Current lower-clothing adjustment and lower-body clothing-displacement exposure actions validate against this state.
- Do not infer this from `clothing.coverage=clothed`.
- Do not use Pose-targeted keys for Action validation.

### `clothing.action.underwear.exist`

Type: boolean

Meaning:

- The selected clothing value explicitly implies underwear and Action needs that fact.
- This is a Clothing-owned, Action-targeted compatibility state.

Set by:

- `data/random_prompt_builder_v2/shared_generators/clothing.json`

Used by:

- `data/random_prompt_builder_v2/shared_generators/action.json`

Notes:

- Current `underwear outfit` style generator value sets this state.
- `underwear outfit` is adult/NSFW gated in addition to its Environment clothing theme validation.
- Current underwear dressing and underwear-adjustment actions validate against this state.
- Do not infer this from `clothing.coverage=clothed`.
- Future authored clothing values that explicitly include underwear should set this state when an Action value needs it.

### `clothing.action.swimwear.exist`

Type: boolean

Meaning:

- The selected clothing value explicitly implies swimwear and Action needs that fact.
- This is a Clothing-owned, Action-targeted compatibility state.

Set by:

- `data/random_prompt_builder_v2/shared_generators/clothing.json`

Used by:

- `data/random_prompt_builder_v2/shared_generators/action.json`

Notes:

- Current `swimwear outfit` style generator value sets this state.
- Current swimwear dressing and swimwear-adjustment actions validate against this state.
- Do not infer this from `clothing.coverage=clothed`.
- Future authored clothing values that explicitly include swimwear should set this state when an Action value needs it.

### `clothing.coverage`

Type: string

Meaning:

- Minimal clothing coverage route selected before clothing style.
- Current values are `nude` and `clothed`.

Set by:

- `data/random_prompt_builder_v2/categories/clothing.json`

Used by:

- `data/random_prompt_builder_v2/categories/clothing.json`
- `data/random_prompt_builder_v2/categories/body_detail.json`
- `data/random_prompt_builder_v2/categories/action.json`
- `data/random_prompt_builder_v2/categories/pose.json`
- `data/random_prompt_builder_v2/categories/composition.json`
- `data/random_prompt_builder_v2/categories/action.json`
- `data/random_prompt_builder_v2/categories/pose.json`

Notes:

- The coverage builder emits no useful positive prompt text for the clothed route.
- The `nude` route emits `nude`, sets only `clothing.coverage=nude`, and validates on `subject.adult=true` plus `content.nsfw_allowed=true`.
- The `clothed` route sets `clothing.coverage=clothed` only when `content.sfw_allowed=true`, so clothing style and authored clothing prompt routes can run only in SFW-capable profiles.
- `clothing.coverage=clothed` is not proof that clothing prompt text exists. It only means the SFW-gated clothed coverage route won.
- The reset baseline intentionally does not write `body.*.coverage` from the nude route. Body Detail remains empty until concrete body-detail values are requested again.

### `clothing.style`

Type: string

Meaning:

- A broad clothing style was selected, so the image model can infer concrete garments from that style and context.
- This is a complete broad clothing route, not a prerequisite for authored clothing prompts.

Set by:

- `data/random_prompt_builder_v2/categories/clothing.json`

Used by:

- `data/random_prompt_builder_v2/categories/clothing.json`

Notes:

- Current clothing style values are the only filled clothing vocabulary besides nude/clothed coverage.
- Current clothing style values validate against `environment.clothing.theme.*` states set by Environment location values.
- Non-empty `builder.clothing.style` sets `clothing.action.exist=true`, `clothing.action.upper_body.exist=true`, and `clothing.action.lower_body.exist=true` at builder level.
- The `underwear outfit` generator value sets `clothing.action.underwear.exist=true` and is gated by `subject.adult=true` plus `content.nsfw_allowed=true`.
- The `swimwear outfit` generator value sets `clothing.action.swimwear.exist=true`.
- The old explicit clothing piece/aspect scaffold has been removed.
- New authored whole/upper/lower clothing builders require this state to be missing before they can run.
- If the style builder emits a value, authored whole/upper/lower clothing skips to avoid double clothing prompts.

### `clothing.whole`

Type: string

Meaning:

- A complete authored whole-body clothing prompt was selected.
- Values are allowed to contain commas and should remain coherent as one complete clothing outcome.

Set by:

- `data/random_prompt_builder_v2/categories/clothing.json`

Used by:

- `data/random_prompt_builder_v2/categories/clothing.json`

Notes:

- Current universal generators for this route are empty, so this state is only written after future non-empty values are added.
- Non-empty `builder.clothing.whole` sets `clothing.action.exist=true`, `clothing.action.upper_body.exist=true`, and `clothing.action.lower_body.exist=true`.
- SFW values come from `generator.clothing.sfw.whole`.
- NSFW values come from `generator.clothing.nsfw.whole` and are gated by `subject.adult=true` plus `content.nsfw_allowed=true`.
- This route validates that `clothing.style` is missing.
- When this state exists, `clothing.upper_body` and `clothing.lower_body` are blocked.

### `clothing.upper_body`

Type: string

Meaning:

- A complete authored upper-body clothing prompt was selected.
- Values are allowed to contain commas and should stay coherent without depending on random lower-body details.

Set by:

- `data/random_prompt_builder_v2/categories/clothing.json`

Used by:

- Future clothing/body validation only when concrete authored values need it.

Notes:

- Current universal generators for this route are empty, so this state is only written after future non-empty values are added.
- Non-empty `builder.clothing.upper_body` sets `clothing.action.exist=true` and `clothing.action.upper_body.exist=true`.
- SFW values come from `generator.clothing.sfw.upper_body`.
- NSFW values come from `generator.clothing.nsfw.upper_body` and are gated by `subject.adult=true` plus `content.nsfw_allowed=true`.
- This route validates that `clothing.style` is missing.
- This route validates that `clothing.whole` is missing.

### `clothing.lower_body`

Type: string

Meaning:

- A complete authored lower-body clothing prompt was selected.
- Values are allowed to contain commas and should stay coherent without depending on random upper-body details.

Set by:

- `data/random_prompt_builder_v2/categories/clothing.json`

Used by:

- Future clothing/body validation only when concrete authored values need it.

Notes:

- Current universal generators for this route are empty, so this state is only written after future non-empty values are added.
- Non-empty `builder.clothing.lower_body` sets `clothing.action.exist=true` and `clothing.action.lower_body.exist=true`.
- SFW values come from `generator.clothing.sfw.lower_body`.
- NSFW values come from `generator.clothing.nsfw.lower_body` and are gated by `subject.adult=true` plus `content.nsfw_allowed=true`.
- This route validates that `clothing.style` is missing.
- This route validates that `clothing.whole` is missing.

### `body_build.weight`

Type: string

Meaning:

- The selected whole-body weight or body-mass phrase.
- Current values range from extremely underweight to extremely overweight wording.

Set by:

- `data/random_prompt_builder_v2/categories/body_build.json`

Used by:

- Future body, clothing, style, or prompt-debug logic only when a concrete need appears.

Notes:

- Values come from `generator.body_build.weight`.
- This state is exported by `builder.body_build.general.physical_trait`.
- Weight is one sibling route in the physical trait builder; it does not combine with muscularity, toning, or bone visibility from the same builder.
- No current validation depends on this state.

### `body_build.muscularity`

Type: string

Meaning:

- The selected whole-body muscle-mass phrase.
- Current values range from extremely frail/low-muscle build to extremely muscular bodybuilder build.

Set by:

- `data/random_prompt_builder_v2/categories/body_build.json`

Used by:

- Future body, clothing, style, or prompt-debug logic only when a concrete need appears.

Notes:

- Values come from `generator.body_build.muscularity`.
- This state is exported by `builder.body_build.general.physical_trait`.
- Muscularity describes underlying muscle amount, not surface definition; visible definition belongs to `body_build.toning`.
- No current validation depends on this state.

### `body_build.toning`

Type: string

Meaning:

- The selected whole-body surface tone or muscle-definition phrase.
- Current values range from extremely soft/no visible definition to extremely sharp visible muscle definition.

Set by:

- `data/random_prompt_builder_v2/categories/body_build.json`

Used by:

- Future body, clothing, style, or prompt-debug logic only when a concrete need appears.

Notes:

- Values come from `generator.body_build.toning`.
- This state is exported by `builder.body_build.general.physical_trait`.
- Toning describes visible definition and softness; it does not assert high or low muscle mass by itself.
- No current validation depends on this state.

### `body_build.bone_visibility`

Type: string

Meaning:

- The selected general whole-body bone-visibility phrase.
- Current values range from no visible bone definition to extremely prominent visible bone structure.

Set by:

- `data/random_prompt_builder_v2/categories/body_build.json`

Used by:

- Future body, clothing, style, or prompt-debug logic only when a concrete need appears.

Notes:

- Values come from `generator.body_build.bone_visibility`.
- This state is exported by `builder.body_build.general.physical_trait`.
- This state is intentionally general and does not name a body region or specific bone. Region-specific bone detail belongs in Body Detail.
- No current validation depends on this state.

### `body_build.proportions`

Type: string

Meaning:

- The selected whole-body proportions or silhouette phrase.
- Current values range from very slight proportions to very full rounded proportions.

Set by:

- `data/random_prompt_builder_v2/categories/body_build.json`

Used by:

- Future body, clothing, style, or prompt-debug logic only when a concrete need appears.

Notes:

- Values come from `generator.body_build.proportions`.
- This state is exported by `builder.body_build.general.proportions`.
- Proportions can coexist with one selected physical trait because it describes overall silhouette rather than another mass/muscle/definition route.
- No current validation depends on this state.

### `body_detail.hair_style`

Type: string

Meaning:

- The selected hairstyle prompt phrase.
- Current values include ungendered hairstyles plus male-coded and female-coded hairstyle wording.

Set by:

- `data/random_prompt_builder_v2/categories/body_detail.json`

Used by:

- Future body, style, pose, or prompt-debug logic only when a concrete need appears.

Notes:

- Values come from `generator.body_detail.hair_style`.
- Hairstyle is safe for all ages and does not validate against `subject.adult` or `content.nsfw_allowed`.
- Male-coded and female-coded hairstyle values validate against `subject.gender`; ungendered hairstyle values remain available when gender is missing.
- This is appearance detail, not pose/action. Hair-touching, washing hair, combing hair, or hands-in-hair wording belongs to Action or Pose.

### `body_detail.hair_color`

Type: string

Meaning:

- The selected hair color prompt phrase.
- Current values include natural hair colors plus stylized fantasy dye colors such as pink, purple, blue, teal, green, rainbow-streaked, and split-dyed hair.

Set by:

- `data/random_prompt_builder_v2/categories/body_detail.json`

Used by:

- Future body, style, lighting, or prompt-debug logic only when a concrete need appears.

Notes:

- Values come from `generator.body_detail.hair_color`.
- Hair color is safe for all ages and does not validate against `subject.adult`, `content.nsfw_allowed`, or `subject.gender`.
- Keep hair color in Body Detail unless a future Style value changes the overall rendering/aesthetic rather than the subject's appearance.

### `body_detail.breasts`

Type: string

Meaning:

- The selected breast body-part prompt phrase.
- Current routes describe breast size through cup-size wording, development-style wording, or NSFW contextual wording.

Set by:

- `data/random_prompt_builder_v2/categories/body_detail.json`

Used by:

- Future body, clothing, style, or prompt-debug logic only when a concrete need appears.

Notes:

- Values come from `generator.body_detail.breasts.size_cup`, `generator.body_detail.breasts.development`, or `generator.body_detail.breasts.nsfw_size`.
- The builder validates on `subject.gender=female`.
- Cup-size and development routes are not split by small/large generator ids; each generator owns the full scale and individual values validate their maximum size/development level through `subject.age_phase`.
- Very small cup-size values validate from `subject.age_phase=preteen` upward; mid-range cup values open in later phases; the largest cup values validate through adult age phases or missing `subject.age_phase`.
- Development values use age-phase starts plus maximum validation: absolute no-development/no-visible-development values are valid for every phase; flat, barely-any, minimal, very-low, low, and slight development values start at `child`; petite and small visible development starts at `preteen`; higher development stages are phase-limited by maximum.
- Missing `subject.age_phase`, such as when Subject is manually overridden, allows the full neutral cup/development range.
- Low development values remain available for older phases too, including adult subjects, because "too small for age" is not a validation failure.
- Breast-owned prompt text should use breast/breasts wording rather than chest wording so the selected phrase stays aligned with `body_detail.breasts`.
- NSFW contextual wording additionally validates through `content.nsfw_allowed=true` and `subject.adult=true` at the value level.
- The NSFW size route covers the lower flat/nearly-flat/tiny range before small, full, and extreme wording.
- Breast-size prompt text must not include age words such as `adult`; age context belongs in Subject state and validation only.
- This is the only active breast body-part builder. Future breast size, shape, firmness, skin, tanning, or similar breast-owned aspects should be sibling routes inside this builder, not separate breast builders.
- Areola and nipple may have separate future builders because they are subparts.

### `pose.general`

Type: string

Meaning:

- The selected general non-intimate pose phrase.
- Current values cover ordinary standing, leaning, sitting, lying, squatting, kneeling, arm placement, non-intimate hand placement, and derived static sport/yoga/dance pose forms.

Set by:

- `data/random_prompt_builder_v2/categories/pose.json`

Used by:

- Future pose/action/body/clothing validation only when a concrete compatibility need exists.

Notes:

- Values come from `generator.pose.general`, `generator.pose.sport.gymnastics_fitness`, `generator.pose.sport.yoga`, or `generator.pose.sport.dance`.
- This is prompt-state tracking, not a compatibility taxonomy.
- Do not derive action mode, surface requirement, or body visibility from this state unless a future concrete value contract documents it.

### `pose.nsfw`

Type: string

Meaning:

- The selected adult/NSFW-gated pose phrase for sensitive, revealing, intimate, suggestive, or static sensitive-area placement presentation.
- These values are NSFW-gated but are not automatically sexual acts.

Set by:

- `data/random_prompt_builder_v2/categories/pose.json`

Used by:

- Future pose/action/body/clothing validation only when a concrete compatibility need exists.

Notes:

- Values come from `generator.pose.nsfw`.
- The NSFW route value inside `builder.pose` is gated by `subject.adult=true` plus `content.nsfw_allowed=true`.
- Keep the sexual route inside `builder.pose` reserved for explicit sexual acts or sex-contextual poses; do not move merely intimate, suggestive, or sensitive placement values there by default.
- Add exact body coverage validation only when a concrete value must require exposed or covered regions.

### `pose.sexual`

Type: string

Meaning:

- The selected adult/sexual pose phrase.
- These values are explicitly sexual or sex-contextual static poses/expressions, not merely NSFW/private/revealing presentation.

Set by:

- `data/random_prompt_builder_v2/categories/pose.json`

Used by:

- Future pose/action/body/clothing validation only when a concrete compatibility need exists.

Notes:

- Values come from `generator.pose.sexual`.
- The sexual route value inside `builder.pose` is gated by `subject.adult=true` plus `content.nsfw_allowed=true`.
- Current values include static derivatives such as labia held open, buttocks held spread for anal visibility, an oral-sex hand gesture, and an oral-ejaculation expression.
- Random sexual Pose output is controlled by `activity.route=pose`; manual Pose override text bypasses that route.

### `ethnicity.base`

Type: string

Meaning:

- The selected base ethnicity text from the universal ethnicity base generator.

Set by:

- `data/random_prompt_builder_v2/shared_generators/ethnicity.json`
- `data/random_prompt_builder_v2/categories/ethnicity.json`

Used by:

- `data/random_prompt_builder_v2/shared_generators/ethnicity.json`

Notes:

- This state exists so universal ethnicity mix and skin-tone generator values can filter without reading builder slots.
- `builder.ethnicity.base_mix` owns `{base}` and `{mix}` slots, then exports the selected base and mix into state.
- `builder.ethnicity.skin_tone` runs after the base/mix builder and uses this state to validate compatible skin-tone values.
- Current base values include broad and subregional heritage/ethnicity labels so repeated generations have more visual variety before skin-tone variation is applied.

### `ethnicity.mix`

Type: string

Meaning:

- The selected optional mixed-ethnicity phrase.

Set by:

- `data/random_prompt_builder_v2/categories/ethnicity.json`

Used by:

- Future ethnicity, style, or prompt-debug logic only if a concrete need appears.

Notes:

- Empty mix slot choices do not write this state.
- Current mix values filter against `ethnicity.base` to avoid repeating the same base.
- The mix generator mirrors the expanded base list and remains optional through scheduled empty values.

### `ethnicity.skin_tone`

Type: string

Meaning:

- The selected optional compatible skin-tone phrase.

Set by:

- `data/random_prompt_builder_v2/categories/ethnicity.json`

Used by:

- Future body, style, lighting, or prompt-debug logic only if a concrete need appears.

Notes:

- Empty skin-tone slot choices do not write this state.
- Current skin-tone values filter against `ethnicity.base` for broad compatibility.
- Prompt-facing skin-tone values should say `skin color`, for example `medium brown skin color`, so the text reads as color guidance rather than a vague skin descriptor.
- Compatibility should stay broad enough that a base ethnicity can still produce multiple plausible skin-color outputs.

### `environment.domain`

Type: string

Meaning:

- The selected broad scene domain.
- Current values are `indoor` and `outdoor`.

Set by:

- `data/random_prompt_builder_v2/categories/environment.json`

Used by:

- `data/random_prompt_builder_v2/categories/environment.json`

Notes:

- The domain builder emits `indoors` or `outdoors` as prompt text.
- Weather currently validates on `environment.domain=outdoor`.
- Future Action and Pose values may validate against this state when concrete location compatibility is needed.

### `environment.season`

Type: string

Meaning:

- The selected season context.
- Current values are `spring`, `summer`, `autumn`, and `winter`.

Set by:

- `data/random_prompt_builder_v2/categories/environment.json`

Used by:

- `data/random_prompt_builder_v2/shared_generators/environment.json`

Notes:

- Weather values may validate against season.
- If season is missing, weather values remain broadly available unless another condition blocks them.
- Current season generation is gated to `environment.domain=outdoor`; do not emit season for indoor settings unless a future indoor-visible weather/window context is explicitly designed.

### `environment.weather`

Type: string

Meaning:

- The selected outdoor weather context.

Set by:

- `data/random_prompt_builder_v2/categories/environment.json`

Used by:

- Future Environment, Action, Pose, Lighting, Style, or Clothing values only when concrete compatibility needs it.

Notes:

- Current weather runs only when `environment.domain=outdoor`.
- Current weather values are intentionally small and broad to avoid overloading prompts.
- Weather must not emit for indoor settings in the current simple baseline because it adds outdoor visual context to an indoor scene.

### `environment.time`

Type: string

Meaning:

- The selected daypart or time context.

Set by:

- `data/random_prompt_builder_v2/categories/environment.json`

Used by:

- Future Environment, Action, Pose, Lighting, Style, or Clothing values only when concrete compatibility needs it.

Notes:

- Detailed illumination belongs in Lighting. Environment time should stay broad and scene-plausibility focused.

### `environment.location`

Type: string

Meaning:

- The selected broad place.
- Current values include home, school/university, library, public/private swimming pool, clothing store, and concrete outdoor nature locations such as forest, beach, lake, river, and countryside.

Set by:

- `data/random_prompt_builder_v2/categories/environment.json`

Used by:

- `data/random_prompt_builder_v2/shared_generators/environment.json`

Notes:

- Mixed-domain locations do not validate against `environment.domain`.
- Outdoor-only locations may validate against `environment.domain=outdoor`; current examples are `in a forest`, `at a beach`, `by a lake`, `by a river`, and `in the countryside`.
- A location can contain both indoor and outdoor room/area values.
- Current room/area values validate against `environment.location` plus the correct `environment.domain`.

### `environment.clothing.theme.underwear_swimwear`

### `environment.clothing.theme.sport`

### `environment.clothing.theme.sleep`

### `environment.clothing.theme.work`

### `environment.clothing.theme.casual`

### `environment.clothing.theme.seasonal`

### `environment.clothing.theme.party`

### `environment.clothing.theme.nude`

Type: boolean

Meaning:

- Broad accepted Clothing themes for the selected Environment location.
- These are soft setting-direction states, not exact social dress-code or physical-possibility gates.

Set by:

- `data/random_prompt_builder_v2/shared_generators/environment.json`

Used by:

- `data/random_prompt_builder_v2/categories/clothing.json`
- `data/random_prompt_builder_v2/shared_generators/clothing.json`

Notes:

- Real location values set several accepted themes so Clothing remains flexible.
- Theme states are location-level only; do not set them from room/area, surface, weather, time, or social context unless the design is intentionally changed.
- Every real location sets `environment.clothing.theme.nude=true`; the nude clothing route still validates through `subject.adult=true` and `content.nsfw_allowed=true`.
- Blank/no-location Environment values set all Clothing themes to `true`, so optional location does not accidentally suppress Clothing validation.
- Underwear and swimwear share `environment.clothing.theme.underwear_swimwear`; individual clothing values may still add adult/NSFW gates.

### `environment.room_area`

Type: string

Meaning:

- The selected room or area within the selected domain, optionally narrowed by the selected location.
- Current values include home rooms/areas such as `in a living room`, `in a kitchen`, and `in a garden`; public/library/pool/store areas; and nature areas under forest, beach, lake, river, and countryside such as `among tall trees`, `on the sandy beach`, `on the lakeshore`, `on the riverbank`, `in a meadow`, and `beside a country road`.

Set by:

- `data/random_prompt_builder_v2/categories/environment.json`

Used by:

- `data/random_prompt_builder_v2/shared_generators/environment.json`

Notes:

- Room/area values validate against `environment.domain` and an `any` location check: compatible `environment.location` or missing `environment.location`.
- Surface values validate against this state.

### `environment.surface`

Type: string

Meaning:

- The selected person-contact surface or nearby object.
- Current values include indoor surfaces such as `the sofa`, `the floor`, `the kitchen counter`, and `the bed`; outdoor/nature surfaces such as `grass`, `sand`, `moss`, `leaf litter`, `a tree stump`, `driftwood`, `pebbles`, `a dock`, `the shoreline`, `the riverbank`, `wildflowers`, and similar.

Set by:

- `data/random_prompt_builder_v2/categories/environment.json`

Used by:

- Future Environment, Action, Pose, or Composition values only when a concrete relation is documented.

Notes:

- Surface values validate against `environment.room_area`.
- Surface prompt text is emitted together with `environment.surface_relation`.
- Do not encode room names into the surface text itself when the selected room/area already supplies that context.

### `environment.surface_relation`

Type: string

Meaning:

- The selected relation/prefix word for a surface phrase.
- Current values are `on`, `in`, `against`, `beside`, `in front of`, `behind`, and `under`.

Set by:

- `data/random_prompt_builder_v2/categories/environment.json`

Used by:

- Future prompt-debug or surface phrase logic only if needed.

Notes:

- The builder relation slot validates that the surface slot exists.
- Do not put slot logic or surface-specific compatibility on the relation generator; the surface value owns room/area compatibility.

### `subject.adult`

Type: boolean

Meaning:

- `true`: selected generated subject is adult.
- `false`: selected generated subject is not adult.

Set by:

- `data/random_prompt_builder_v2/state_profiles/*.json`
- `data/random_prompt_builder_v2/categories/subject.json`

Used by:

- `data/random_prompt_builder_v2/categories/clothing.json`

Notes:

- This remains the hard adult/NSFW permission state for adult-only routes.
- State profiles seed this as a fallback so manual subject overrides can still use adult-gated values.
- Generated subject values overwrite the profile seed with the selected subject's actual adult/non-adult value.
- Non-adult generated subject values validate on `content.sfw_allowed=true`, so NSFW-only profiles select adult generated subjects only.
- Do not add `subject.is_minor`.
- Use `subject.age_phase` for broad phase validation instead of parsing `subject.age_range`.

### `subject.age_range`

Type: string

Meaning:

- Debug/readability state containing the selected subject age-range prompt phrase.
- Mirrors the selected subject text's age range and label.

Set by:

- `data/random_prompt_builder_v2/categories/subject.json`

Used by:

- Debug state output.

Notes:

- This state is intentionally kept because it was manually added for debugging.
- Do not use it for validation by default. Use `subject.age_phase` for broad age-phase validation.
- Age/adult gating should continue to use `subject.adult`.

### `subject.age_phase`

Type: string

Meaning:

- Broad age phase for validation that should not depend on gendered age-range text.
- Current values are `young_child`, `child`, `preteen`, `teen`, `late_teen`, `young_adult`, `adult`, `prime_adult`, `middle_aged`, `older_adult`, and `elderly`.

Set by:

- `data/random_prompt_builder_v2/categories/subject.json`

Used by:

- `data/random_prompt_builder_v2/categories/body_detail.json`

Notes:

- State profiles intentionally do not seed this state. Manual Subject overrides remain text-only and leave `subject.age_phase` missing.
- Missing `subject.age_phase` allows breast-size Body Detail routes that are otherwise phase-gated, so manual Subject overrides can still use the full breast-size range.
- `subject.age_phase` does not encode gender or explicit ages. Use `subject.gender` and `subject.adult` separately when those facts are needed.

### `subject.gender`

Type: string

Meaning:

- The selected generated subject's broad gender category.
- Current values are `male` and `female`.

Set by:

- `data/random_prompt_builder_v2/state_profiles/SFWFemale.json`
- `data/random_prompt_builder_v2/state_profiles/NSFWFemale.json`
- `data/random_prompt_builder_v2/state_profiles/MixedFemale.json`
- `data/random_prompt_builder_v2/state_profiles/SFWMale.json`
- `data/random_prompt_builder_v2/state_profiles/NSFWMale.json`
- `data/random_prompt_builder_v2/state_profiles/MixedMale.json`
- `data/random_prompt_builder_v2/categories/subject.json`

Used by:

- `data/random_prompt_builder_v2/shared_generators/action.json`
- `data/random_prompt_builder_v2/shared_generators/body_detail.json`
- `data/random_prompt_builder_v2/shared_generators/pose.json`
- Future gendered clothing, body-detail, action, or pose values when a concrete value needs it.

Notes:

- Gendered state profiles seed this state for manual subject overrides.
- Generated subject values overwrite the profile seed only after validating against `profile.gender_mode`.
- Current NSFW washing-vulva and washing-penis actions validate against this state.
- Current NSFW/Sexual Action and Pose values validate breast/vulva/labia/penis-specific wording against this state where needed.
- Current Body Detail hairstyle values validate against this state only when the wording is intentionally male-coded or female-coded; hair values remain safe for all ages.
- State profiles write `subject.adult` and `subject.gender` with priority `-1`, so valid generated subject values at default priority `0` can overwrite fallback seeds while manual subject overrides can still use the profile seed.
- `profile.gender_mode` records the selected profile gender mode separately from the actual selected/generated `subject.gender`.
- Keep this state because Subject currently sets it and future gendered clothing values are expected to use it again.
