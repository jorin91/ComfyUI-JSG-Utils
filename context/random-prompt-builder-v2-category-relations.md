# Random Prompt Builder V2 Category Relations

## Purpose

This file documents the important relationships between Prompt Builder V2 categories.

Use it before changing category order, adding validation, adding new states, or filling vocabulary that combines body, clothing, environment, action, pose, style, lighting, or quality. It is intentionally about relationships, not category-local vocabulary.

## Core Rule

Categories may depend only on durable global state that already exists from state profiles or earlier resolved categories/builders. V2 does not lazy-load later builders for validation.

They must not depend on another category's prompt text or accidental JSON order. If two categories can conflict, they need a documented state contract or one of them must stay broad enough not to conflict.

## Relation Map Maintenance Rule

This file is the single central relationship map for Prompt Builder V2.

Whenever a new relationship is created between categories, builders, generators, state keys, tags, prompt order, or validation order, update this file in the same work session. Category-specific files may explain local behavior, but every cross-category relationship must be represented here.

Do not create separate narrow relationship-map files for one subsystem unless there is a strong reason and this file links to them. The default is to keep one universal relationship map here.

Validation order is executable dependency context. Whenever a state is added, removed, renamed, moved, or given another possible writer or reader, check whether `data/random_prompt_builder_v2/config.json` needs a `resolve_order` update in the same work session. Generator value conditions count as readers too; always check where the generator is used before deciding order.

## Adding Clothing / Action / Pose Values

When adding clothing, action, or pose values, all relevant cross-category relationships must be checked before the value is considered valid.

This means checking every documented relation that can logically affect the new value, including clothing-to-pose/action, action-to-pose, subject/content gates, environment compatibility, and any body coverage or body-detail dependency. If the new value can conflict with another category, require another category's selected fact, or make another category's output unsafe or contradictory, the relationship must be represented with reusable state and validation.

Use the broadest accurate state first. Reuse an existing state when it expresses the needed fact. Add a new state only when a concrete value sets or consumes it and no existing state is accurate enough.

Do not validate against prompt wording, concrete value strings, builder order side effects, or many duplicated clothing/action/pose options. If no real relationship exists, do not invent state just to document one.

Alternative prompt wording is allowed when the image model may interpret it differently, when the wording is more standalone/general than an existing context-specific value, or when it changes steering strength. This is not the same as combining alternatives in one value. Keep each wording atomic and route it to the correct category if the wording changes ownership; for example, `wall squat` remains a Pose value, while `squatting against a wall` is an Action value because it steers wall support and scene context.

Pose/Action boundary:

- Action owns doing, movement, execution, undertaking, interaction, support/object use, and wording paired with movement.
- Pose owns static posture, body form, expression, and specific body-part placement.
- Active verbs such as touching, caressing, adjusting, washing, grabbing, object-holding, and leaning against support belong in Action.
- Pose may contain static derivatives from actions when the result is posture/form/placement only, such as `hands on the face`, `one hand on the cheek`, `hands resting over the mons pubis`, or `wall squat`.
- When Action contains useful static posture information that does not yet exist in Pose, derive an atomic Pose value from it. Keep the Action value when it carries movement/object/context; add only the static posture/form/expression piece to Pose.
- Clothing-displacement exposure belongs in Action because the subject is moving clothing. Validate it against the broadest Clothing-to-Action state for the involved body region, then gender-gate only genuinely gender-specific anatomy.
- Static camera-facing body-part display without clothing movement can belong in Pose. It is NSFW when it is visibility/nudity-oriented and sexual only when the wording depicts a sex act or sex-contextual expression/gesture.
- Self-stimulation, penetration, labia spreading, buttocks spreading for anal visibility, and oral-sex gestures are Sexual Action when phrased as doing/movement. Static held versions may also be Sexual Pose values when useful.
- Action is one conceptual slot. General, sport, NSFW, standalone sexual, penetration, and stimulation routes belong as sibling values inside `builder.action`, not as multiple sibling builders guarded by `action.selected`.
- High-variation sexual action subfamilies should become modular `builder.action` values instead of many sibling options in `generator.action.sexual`; current modular routes are penetration and stimulation.
- When a Pose or Action generator grows beyond roughly 25 non-empty options, split it into smaller semantic generators and let the builder contain multiple values pointing to those sets.
- When sibling builder values target the same kind of result but are separated by route class, keep their readable order `sfw -> nsfw -> sexual`. This order is not a weight or priority rule; valid sibling builder values are still randomly selected by the resolver.

## Universal Relationship Map

This is the high-level source -> target map. More detail lives in the sections below, but this table is the first place to check before adding values or validation.

| Source | Target | Current / Allowed Relation | State Contract | Validation Strictness |
| --- | --- | --- | --- | --- |
| State Profile | Subject / Content | Seeds fallback adult, gender, SFW/NSFW allow, profile mode. | `subject.adult`, `subject.gender`, `content.sfw_allowed`, `content.nsfw_allowed`, `profile.*` | Hard gates for adult/NSFW routes; profile mode is context, not routine gate. |
| Subject | Clothing | Adult and gender may gate concrete clothing values. | `subject.adult`, `subject.gender`, `content.nsfw_allowed` | Hard only for adult/NSFW/gender-specific values. |
| Subject / Content | Action / Pose | Adult/NSFW/sexual containers and values gate through subject/content state. | `subject.adult`, `content.nsfw_allowed` | Hard for NSFW and sexual values. |
| Subject | Body Detail | Sensitive, gender-specific, or broad phase-dependent detail may gate through subject state. | `subject.adult`, `subject.gender`, `subject.age_phase` | Hard only for concrete sensitive/gendered/phase-dependent detail values. |
| Ethnicity | Ethnicity internals | Mix and skin tone filter against selected base. | `ethnicity.base`, `ethnicity.mix`, `ethnicity.skin_tone` | Hard only inside Ethnicity compatibility. |
| Ethnicity | Body / Clothing / Style | No routine dependency; avoid stereotypes. | None by default. | Do not add without explicit documented need. |
| Clothing | Body Detail | Clothing may set exact body coverage/exposure facts for later body detail. | Future exact `body.*.coverage` states only when concrete values need them. | Hard for visible/exposed body details; unspecified clothing does not prove exposure. |
| Clothing | Pose | No active Clothing-to-Pose state. Static Pose values should usually remain clothing-independent unless a future value truly requires a garment or exact coverage. | None current. | Add only for concrete static poses that require clothing, underwear, swimwear, or specific covered/exposed facts. |
| Clothing | Action | Clothing writes Action-targeted availability states for clothing-dependent actions. | `clothing.action.exist`, `clothing.action.upper_body.exist`, `clothing.action.lower_body.exist`, `clothing.action.underwear.exist`, `clothing.action.swimwear.exist` | Hard only for actions that require clothing, underwear, swimwear, or specific covered/exposed facts. |
| Environment | Environment internals | Domain -> location -> room/area -> surface chain. | `environment.domain`, `environment.location`, `environment.room_area`, `environment.surface` | Hard internal compatibility; every room/area and surface must answer "kan dit?". |
| Environment | Clothing | Location values set broad accepted clothing themes for soft setting steering. | `environment.clothing.theme.*` | Soft steering. Clothing values validate against accepted themes, but locations should allow several themes, the blank/no-location fallback is permissive, and nude is allowed for every real location. |
| Environment | Action | Actions may validate against broad scene/location/surface facts when the action has a hard setting requirement. | `environment.domain`, `environment.location`, `environment.room_area`, `environment.surface` | Hard for cycling, swimming, showering, bathing, classroom-only work, etc.; no validation for soft plausibility like yoga. |
| Environment | Pose | Poses may validate against broad scene/location/surface facts only when the pose has a hard setting requirement. | `environment.domain`, `environment.location`, `environment.room_area`, `environment.surface` | Hard only for location/surface-dependent pose concepts; no validation for broadly portable poses. |
| Action | Pose | Random Action and random Pose are mutually exclusive through the internal route state; manual overrides bypass the route and still output text. | `activity.route` | Route is chosen only from random-enabled Action/Pose categories. Disabled-random categories are excluded from the route choice; override text emits directly, and empty override emits nothing. |
| Body Detail | Action / Pose | Body Detail should not imply action/pose. | None current. | Move posture/action wording to Pose or Action. |
| Environment | Lighting | Lighting may depend on broad domain/time only when concrete lighting values need it. | Future use of `environment.domain`, `environment.time` | Hard only for concrete light values that require it. |
| Environment | Composition | Environment owns where; Composition owns framing. | None current. | Boundary rule, not routine validation. |
| Style | Clothing Style | Image style and clothing style must not duplicate. | `clothing.style` remains clothing-owned. | Boundary rule. |
| Quality | All | Quality is final model steering and should not set scene facts. | None current. | Boundary rule. |

## Environment / Action / Pose Location Strictness

Action and Pose may validate against Environment, but only for hard requirements.

Soft plausibility is not enough for validation. A yoga pose or yoga action may often happen at home, in a gym, outdoors, or in many other settings, so it should not validate against location by default.

Hard setting requirements should validate. Examples:

- `cycling` should require an environment where cycling can logically occur, starting broadly with `environment.domain=outdoor` and narrowing only when concrete location/room/area values exist.
- `swimming` should validate against water/pool context such as `environment.location` in swimming-pool locations or `environment.room_area` values like `in a swimming pool`, `in an indoor built-in pool`, `in a built-in garden pool`, `in a frame garden pool`, or `in an inflatable garden pool`.
- `showering` validates against shower-capable room/area context.
- `taking a bath` validates against bathroom context. Do not micromanage it with `environment.surface=the bathtub` while room/area is already the broadest accurate hard requirement.
- `urinating` is only adult/NSFW gated and has no Environment validation, because it can technically happen anywhere.
- `singing in the shower` and `posing in the shower` use the same shower-capable validation as showering.
- mirror actions require mirror-capable room/area context.
- `making the bed` requires bedroom/dorm room context.
- hard gymnastics apparatus actions such as vault, beam, bars, rings, and pommel horse require `environment.room_area=in a gymnasium`.
- hard fixed fitness-apparatus actions such as treadmill, cycling machine, rowing machine, bench press, lat pulldown, battle ropes, and changing weight plates currently require `environment.room_area=in a gymnasium`. If future Environment values add home-gym/fitness-room support, broaden this through reusable state rather than per-action room lists.
- yoga and most dance/fitness actions are not environment-gated because they can technically happen in many places; only hard object/setting requirements should add validation.
- routine washing or grooming actions stay ungated by Environment unless a concrete value has a hard setting requirement. `washing the body`, `washing hands`, `washing the face`, `washing the hair`, `washing the buttocks`, `washing the vulva`, and `washing the penis` are not automatically shower/bath actions; keep them general unless the wording explicitly says shower, bath, sink, or another hard object.

Object-specific validation boundary:

- Validate on whether the selected value names a hard object or facility and where that object/facility can physically exist.
- A portable or generally available action stays broad. Washing can happen with many water sources and should not be tied to shower/bath unless the action wording names shower/bath.
- Social acceptability is not a validation reason. `urinating` can technically happen anywhere, so it stays Environment-ungated despite being strange or inappropriate in many places.
- A fixed/facility action validates at the broadest accurate level. `making the bed` names a bed and should require bedroom/dorm room; `showering` names shower facilities and should require bathroom/shower room; mirror actions require mirror-capable room/areas.
- Use `environment.surface` only when room/area and location are not accurate enough and the specific selected contact object itself is the hard requirement. Do not add surface validation merely because a compatible surface may also exist.

Use the broadest accurate Environment state first:

1. `environment.domain` when indoor/outdoor is enough.
2. `environment.location` when a whole place is required.
3. `environment.room_area` when a specific room/area is required.
4. `environment.surface` only when a concrete object/surface is physically required and room/area is not accurate enough.

Do not validate Action or Pose against `environment.time`, `environment.season`, or `environment.weather` unless a new concrete relationship is explicitly documented here first.

## Prompt Order Versus Resolve Order

Final prompt order is for model steering and readability.

Resolve order is the only path for generated state availability and validation. Later builders are never pulled forward automatically.

Current important relation:

- Environment resolves immediately after Subject because Clothing values validate against environment clothing themes and Action values validate against environment domain/room/surface state.
- Clothing resolves before Action because Action values validate against clothing-action availability states.
- Action appears before Pose in prompt text. Random Action/Pose selection is controlled by internal `activity.route`; random Action requires `activity.route=action`, and random Pose requires `activity.route=pose`.
- Body Detail, Body Build, Ethnicity, Composition, Lighting, Style, and Quality currently do not produce state consumed by active later categories, so they resolve after the dependency-producing chain.
- Body Build and Body Detail still appear before Clothing in prompt text, so body features steer strongly.
- Every configured category should have an explicit `resolve_order` in `data/random_prompt_builder_v2/config.json`; do not rely on the code fallback to prompt `order` for maintained categories.

Do not change `resolve_order` just to make final prompt text sound nicer. Use `order` for prompt text and `resolve_order` for logic.

## Relationship Matrix

### State Profiles -> Subject / Clothing / Body Detail / Action / Pose

Contract:

- State profiles set `content.sfw_allowed`, `content.nsfw_allowed`, `profile.content_mode`, and `profile.gender_mode`.
- State profiles seed `subject.adult`, and gender-specific profiles seed `subject.gender`, at fallback priority.
- State profiles may define debug-only `ignore_state_keys` and `ignore_tags` arrays. These bypass only individual matching state/tag condition checks; other checks on the same value, builder, or generator still validate normally.
- Generated Subject can overwrite fallback subject states with higher/default priority only after its value validates against the selected profile state.
- Generated Subject gender must validate against `profile.gender_mode`: `female` profiles allow only female Subject values, `male` profiles allow only male Subject values, and `any` profiles allow both.
- Manual Subject overrides do not infer state, so profiles provide the fallback.
- Non-adult generated Subject values validate on `content.sfw_allowed=true`; NSFW-only profiles therefore select adult generated subjects only.
- Random Subject must always output a concrete phrase; `builder.subject` must not contain empty skip values.

Risk:

- A wrong default profile can enable adult or gendered values even when manual Subject text says something else.

Rule:

- Manual overrides are text-only. Do not try to infer subject facts from override strings unless a future explicit parser is designed.

### Subject -> Clothing

Contract:

- `subject.gender` may gate explicitly gendered authored clothing values if future concrete values need it.
- `subject.adult=true` gates sexy, revealing, adult-styled, missing-clothing, and nude/visibility-directed authored values.
- `content.nsfw_allowed=true` gates values whose direct purpose is visible nudity.
- `profile.content_mode` is profile intent/context and should not be used as a routine NSFW gate when `content.nsfw_allowed` already provides the allow state.

Risk:

- Overusing adult gates on ordinary clothing can make non-adult subjects under-clothed or underspecified.

Rule:

- Ordinary clothing must stay available for non-adult subjects.
- Adult/NSFW gates belong only on the concrete values that need them.

### Subject / Content Gates -> Action / Pose

Contract:

- `subject.adult=true` gates adult-only action and pose values.
- `content.nsfw_allowed=true` gates NSFW action and pose values.
- Action and Pose use their `.nsfw` routes for gated private, revealing, sensitive, suggestive, or intimate presentation that is not necessarily a sexual act.
- Action and Pose reserve their `.sexual` routes for explicitly sexual acts or sex-contextual values.

Risk:

- Putting merely NSFW/sensitive values in `.sexual` makes the taxonomy too narrow and turns ordinary gated pose/action presentation into sexual content.
- Missing adult/NSFW gates can allow sensitive values for non-adult subjects or SFW profiles.

Rule:

- Every NSFW or sexual action/pose value must validate through the selected adult state and the NSFW allow state, either by builder-level gates when all values share the route or value-level gates when only some values need them.
- Do not use `profile.content_mode` as the routine gate when `subject.adult` and `content.nsfw_allowed` express the actual permission.

### Subject -> Body Detail

Contract:

- Adult-sensitive body details validate through `subject.adult=true`.
- Female-specific sensitive body details validate through `subject.gender=female`.
- Non-sensitive hairstyle values may validate against `subject.gender` when the wording is intentionally male-coded or female-coded.
- Hair style and hair color are safe for all ages and do not use adult/NSFW gates.
- The current breast body-part builder validates through `subject.gender=female`. Cup-size, development, and NSFW size are three sibling routes, not separate small/large builders or generators. Each route keeps its full scale. Cup-size values start at `subject.age_phase=preteen`. Development values use age-phase starts plus maximum validation: absolute no-development/no-visible-development values are valid for every phase; minimal/beginning development starts at `child`; small visible development starts at `preteen`; higher development stages are phase-limited by maximum. Missing `subject.age_phase` allows the full neutral scale for manual Subject overrides. NSFW breast wording additionally validates through `content.nsfw_allowed=true` and `subject.adult=true`.
- Future visible nudity or exposed sensitive details should validate through `content.nsfw_allowed=true` and exact `body.*.coverage=exposed` states when those concrete states are reintroduced.

Risk:

- Body detail can become both too explicit and contradictory when it ignores coverage.

Rule:

- Sensitive Body Detail values need exact adult, gender where relevant, NSFW, and coverage gates.
- Non-sensitive hair appearance may stay broad; gender validation is only for wording that would be awkward for the other selected subject gender.
- Do not add broad age/gender/body taxonomies until concrete validation needs them. `subject.age_phase` is the current broad phase state and is used by breast-size Body Detail values instead of parsing gendered `subject.age_range` text. Prompt-facing breast-size text should not include age words such as `adult`; age context belongs in Subject state and validation.

### Ethnicity -> Body Build / Body Detail / Style

Contract:

- Current ethnicity sets `ethnicity.base`, optional `ethnicity.mix`, and optional `ethnicity.skin_tone` for ethnicity-internal compatibility and debug visibility.
- Skin tone is generated by a separate builder after `ethnicity.base` exists, so the prompt receives origin wording and skin-tone wording as separate elements while keeping the same skin-tone validation against `ethnicity.base`.
- Skin-tone prompt values explicitly include `skin color` wording for clarity.
- Ethnicity variation should stay neutral: use broader/subregional heritage labels and compatible skin-color ranges, not stereotype facial features, body shape, clothing, attractiveness, or style assumptions.

Risk:

- Later body or style values could accidentally turn ethnicity into stereotype steering.

Rule:

- Do not use ethnicity state for body shape, attractiveness, clothing, or style unless the user explicitly requests a careful concrete feature and a durable rule is documented first.

### Clothing -> Body Detail

Contract:

- Clothing owns `clothing.coverage` and authored clothing prompt states.
- The reset nude coverage route currently writes only `clothing.coverage=nude`.
- Future authored clothing values may write `body.*.coverage=covered/exposed` only for regions they concretely affect.
- Future Body Detail exposed-region details should validate against exact coverage states when concrete body-detail vocabulary is reintroduced.

Risk:

- Authored clothing values such as sheer, displaced, open, wet, tiny, or transparent outcomes can imply exposure without setting coverage, causing Body Detail to skip or contradict the clothing.

Rule:

- If a clothing value explicitly exposes or covers a body region that Body Detail uses, write the exact coverage state.
- Use priority only for real conflicts between future authored values and body visibility states.
- Unspecified clothing does not prove exposure.

### Clothing Style -> Authored Clothing Prompts

Contract:

- `clothing.style` is a broad outfit direction.
- Authored clothing prompts live in `clothing.whole`, `clothing.upper_body`, and `clothing.lower_body`.
- `clothing.style` is exported as state from the selected style slot.
- All authored clothing prompt builders validate that `clothing.style` is missing.

Risk:

- Mixing broad style with authored clothing prompts produces double clothing steering: the style asks the image model to infer garments while authored values also force specific garments.

Rule:

- Keep style broad.
- Treat style as a complete broad clothing route.
- If style emits a value, whole/upper/lower authored clothing must skip.
- If concrete clothing is needed, let style skip and use whole or upper/lower authored routes instead.

### Authored Clothing Prompt Split

Contract:

- Whole-body clothing values are complete outfit outcomes.
- Upper-body and lower-body clothing values are complete body-half outcomes.
- SFW and NSFW values are separated into different generators.
- Whole-body validates that `clothing.style` is missing.
- Upper-body and lower-body builders validate that `clothing.whole` is missing.

Risk:

- Independent upper/lower values can contradict each other when an outfit concept actually needs coordinated garments.
- A whole-body outfit plus upper/lower outfit fragments can over-specify or contradict clothing.
- A broad style plus authored clothing fragments can over-specify or contradict clothing.

Rule:

- Prefer whole-body values when the top and bottom must stay coordinated.
- Use upper/lower values only when those halves can vary safely.
- Broad style wins over all authored clothing routes.
- Whole-body authored clothing wins over upper/lower authored clothing.
- Do not rebuild the old piece/aspect matrix unless the clothing design is explicitly changed again.

### Environment -> Clothing Themes

Contract:

- Environment location values set broad accepted clothing theme states under `environment.clothing.theme.*`.
- Theme states are location-level only. Do not set or validate clothing themes from `environment.room_area`, `environment.surface`, weather, time, or social context unless this design is explicitly changed.
- Current themes are `underwear_swimwear`, `sport`, `sleep`, `work`, `casual`, `seasonal`, `party`, and `nude`.
- Clothing coverage/style values validate against these theme states for soft setting direction.
- `nude` is accepted by every real location, but the nude clothing route still requires `subject.adult=true` and `content.nsfw_allowed=true`.
- The blank/no-location Environment fallback should set all Clothing themes to `true`; optional location must not accidentally make Clothing validation stricter than a real location.
- Underwear and swimwear share one location theme because the desired generation space treats pool/swim settings as compatible with both normal swimwear and adult/NSFW underwear styling. Individual clothing values may still add adult/NSFW gates where needed.

Risk:

- If themes become too narrow, Clothing will disappear too often or feel socially judgmental instead of setting-directed.
- If themes are set below location level, Environment-to-Clothing becomes micro-managed and hard to reason about.

Rule:

- Use themes as soft accepted buckets, not exact dress-code rules.
- Give each location several compatible themes, balancing ordinary setting fit with the adult/NSFW prompt space the generator is meant to support.
- Keep `environment.clothing.theme.nude=true` on every real location.
- Keep the blank/no-location fallback permissive across all Clothing themes.
- Do not validate Clothing directly against concrete location strings when a theme can express the intent.

### Environment -> Action

Contract:

- Action may validate against `environment.domain`, `environment.location`, `environment.room_area`, and `environment.surface`.
- Action must not validate against `environment.time`, `environment.season`, or `environment.weather`.
- Environment validation belongs only on actions with hard setting requirements, not actions that are merely plausible in some places.

Risk:

- Over-validating against detailed environment states can make actions disappear unexpectedly and make prompt results hard to reason about.
- Under-validating hard setting actions can create impossible prompts, such as swimming in a classroom or cycling indoors in a room with no cycling context.

Rule:

- Keep action/environment compatibility broad and location-based.
- Do not validate portable actions such as yoga just because they are common at home, in a gym, or outdoors.
- Validate hard setting actions such as swimming, cycling, showering, or room-specific work against the broadest accurate Environment state.
- Use `environment.surface` only when the concrete action physically requires a specific selected object/support and room/area is not accurate enough.

Current action/environment contracts:

- `urinating`: no Environment validation; adult/NSFW gate only.
- `showering`: requires `environment.room_area` of `in a bathroom` or `in a shower room`.
- `taking a bath`: requires `environment.room_area=in a bathroom`.
- `singing in the shower` and `posing in the shower`: same validation as `showering`.
- mirror actions: require mirror-capable `environment.room_area`, currently bathroom, bedroom, walk-in closet, hallway, landing, living room, public toilet, toilet room, fitting room, fitting booth, or changing room.
- `making the bed`: requires `environment.room_area` of `in a bedroom` or `in a dorm room`.
- `squatting against a wall`: Action-owned support/context wording. It allows missing `environment.surface` because the action prompt supplies the wall support, but if `environment.surface` is selected it must be `the wall`.
- shower/bath-specific action wording validates to shower/bath-capable room/area, but general washing wording does not.
- routine washing/grooming, clothing-change, reading, computer, TV, gaming, drinking, cuddling, studying, drawing, playing, cleaning, dancing, walking, running, jumping, skipping, crawling, sleeping, yawning, laughing, looking outside, dreaming, watering plants, and environment interaction: no Environment validation unless a future concrete value creates a harder setting requirement.

### Environment Internal Chain

Contract:

- `environment.location` sets the selected place and does not validate against `environment.domain`.
- `environment.room_area` must validate against `environment.domain` and either a compatible `environment.location` or missing `environment.location`.
- `environment.surface` must validate against `environment.room_area`.
- The executable surface compatibility source is `data/random_prompt_builder_v2/shared_generators/environment.json`, `generator.environment.surface`, where each surface value owns its allowed `environment.room_area` conditions.

Risk:

- If room/area and surface do not validate through the chain, prompts can create impossible combinations such as a bathtub in a garden, a bed in a bathroom, or a kitchen counter in a bedroom.

Rule:

- Every room/area value needs a clear allowed location/domain contract, expressed as domain plus an `any` location check: compatible location or missing location.
- Every surface value needs a clear allowed room/area contract.
- Do not add environment vocabulary that cannot answer "kan dit?" through state validation.
- A location such as home can contain both indoor and outdoor areas; domain compatibility belongs on the room/area values, not on the location value.
- A location that has no meaningful indoor form may validate against `environment.domain=outdoor`; current examples are `in a forest`, `at a beach`, `by a lake`, `by a river`, and `in the countryside`. Their room/area values still validate against the outdoor domain, and against either their compatible location or missing location.
- Keep values atomic. Do not use combined alternatives such as `hallway or landing`.
- Prefer room-specific surface names when the same object type has a different visual identity by location, such as `the sofa` for a living room versus `the garden bench` outdoors.
- Reuse existing room/areas and surfaces when they are semantically broad enough; add a variant only when visual meaning changes enough to justify it.
- When adding a location, check existing room/areas and link every room/area that logically belongs there.
- When adding a room/area, check existing locations and surfaces and link every compatible value.
- When adding a surface, check all existing room/areas and link every compatible room/area, not only the room/area that triggered the addition.
- Scheduled empty values remain valid after the candidate list is filtered. Environment therefore uses explicit empty-cadence multipliers for the dependency chain: `location` uses the global default, `room_area` uses `3x` the default base, and `surface` uses `4x` the default base. With the current base of 10 real choices, this means room/area empties every 30 real choices and surface empties every 40 real choices, both rounded up.
- Do not add separate empty builder values to `builder.environment.location`, `builder.environment.room_area`, or `builder.environment.surface`; that stacks skip chances across the dependency chain and makes surfaces disappear too often. Their skip chance belongs in the generator value lists. This is the category-specific version of the global rule that generator-backed template builders do not add duplicate builder-level skip values.

Current location -> domain -> room/area map:

- `at home`
  - indoor: `in a living room`, `in a hallway`, `on a landing`, `in a kitchen`, `in a laundry room`, `in a toilet room`, `in a bathroom`, `in a bedroom`, `in a walk-in closet`, `in a shed`, `in a basement`, `in an attic`, `in an indoor built-in pool`
  - outdoor: `in a garden`, `in a built-in garden pool`, `in a frame garden pool`, `in an inflatable garden pool`, `beside a private pool`
- `at a primary school`
  - indoor: `in a hallway`, `in a toilet room`, `in a classroom`, `in a cafeteria`, `in a gymnasium`, `in a library`, `in a principal office`, `in a changing room`
  - outdoor: `on a playground`
- `at a secondary school`
  - indoor: `in a hallway`, `in a toilet room`, `in a classroom`, `in a cafeteria`, `in a gymnasium`, `in a library`, `in a principal office`, `in a changing room`, `in a science lab`, `in a computer lab`
  - outdoor: `on a playground`, `on a sports field`
- `at a university`
  - indoor: `in a hallway`, `in a toilet room`, `in a library`, `in a lecture hall`, `in a seminar room`, `in a laboratory`, `in a lounge`, `in a dorm room`
  - outdoor: `on campus`, `in a campus courtyard`
- `at a library`
  - indoor: `in a reading area`, `in a study area`, `between bookshelves`, `at a reception desk`, `in a computer area`
- `at a public swimming pool`
  - indoor: `in a changing room`, `in a swimming pool`, `beside the swimming pool`, `in a shower room`, `in a locker area`, `in a visitor area`
  - outdoor: `in a swimming pool`, `beside the swimming pool`
- `at a private swimming pool`
  - indoor: `in an indoor built-in pool`
  - outdoor: `in a built-in garden pool`, `in a frame garden pool`, `in an inflatable garden pool`, `beside a private pool`
- `at a clothing store`
  - indoor: `among clothing racks`, `in a fitting room`, `in a fitting booth`, `at a checkout counter`, `in a display area`, `in a storage room`, `in a public toilet`, `behind a display window`
- `in a forest`
  - outdoor: `among tall trees`, `on a forest trail`, `in a forest clearing`, `at the woodland edge`, `near a mossy grove`
- `at a beach`
  - outdoor: `on the sandy beach`, `near the shoreline`, `in the dunes`, `on a rocky beach`, `near a tide pool`
- `by a lake`
  - outdoor: `on the lakeshore`, `on a lakeside dock`, `among reeds by the lake`, `near a quiet cove`, `beside a small lake`
- `by a river`
  - outdoor: `on the riverbank`, `on a riverside path`, `near a waterfall`, `by shallow rapids`, `on a wooden bridge`
- `in the countryside`
  - outdoor: `in a meadow`, `in a field`, `in a wildflower field`, `on a hill`, `beside a country road`, `near a wooden fence`

Current room/area -> surface map:

- `among clothing racks`: `the floor`, `the wall`, `the door`, `clothing racks`
- `among reeds by the lake`: `grass`, `the lakeshore`, `reeds`
- `among tall trees`: `grass`, `a bag`, `a backpack`, `moss`, `a tree trunk`, `a fallen log`, `a rock`, `leaf litter`, `a tree stump`
- `at a checkout counter`: `the floor`, `the wall`, `the door`, `a cash register`, `a shopping basket`, `a shopping bag`, `a checkout counter`, `a counter display`
- `at a reception desk`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `the reception desk`
- `at the woodland edge`: `grass`, `a bench`, `a fence`, `a tree trunk`, `a dirt path`, `wildflowers`, `a wooden fence`
- `behind a display window`: `the floor`, `the wall`, `the door`, `a mannequin`, `a display table`, `a display window`
- `beside a country road`: `grass`, `a fence`, `a bag`, `a backpack`, `a dirt path`, `a hay bale`, `a wooden fence`, `a country road`
- `beside a private pool`: `a bench`, `the pool edge`, `a towel`, `a towel rack`, `a bag`, `a backpack`
- `beside a small lake`: `grass`, `a bench`, `a fence`, `a towel`, `a bag`, `a backpack`, `a tree trunk`, `a fallen log`, `a dirt path`, `a beach towel`, `the shoreline`, `the lakeshore`, `a dock`, `a rock`, `a picnic blanket`, `reeds`
- `beside the swimming pool`: `a bench`, `the pool edge`, `a towel`, `a towel rack`, `a bag`, `a backpack`
- `by shallow rapids`: `moss`, `the riverbank`, `a rock`, `pebbles`
- `between bookshelves`: `the floor`, `the wall`, `the door`, `a bookshelf`, `a rolling ladder`, `a stool`, `books`, `a book`
- `in a basement`: `the floor`, `the stairs`, `the wall`, `the washing machine`, `the dryer`, `the workbench`, `the door`
- `in a bathroom`: `the floor`, `the wall`, `the toilet`, `the sink`, `the shower`, `the shower tray`, `the shower wall`, `the bathtub`, `the door`, `the large mirror`, `the small mirror`
- `in a bedroom`: `a chair`, `the windowsill`, `the rug`, `the floor`, `the wall`, `the bed`, `the wardrobe`, `the bedside table`, `a seat cushion`, `the door`, `the large mirror`, `the small mirror`
- `in a built-in garden pool`: `the pool floor`, `the pool ladder`, `the pool edge`, `a pool noodle`, `a floating mat`, `an inflatable ring`, `a ball`
- `in a cafeteria`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `a table`, `the cafeteria counter`
- `in a campus courtyard`: `a bench`, `pavement`, `a fountain`
- `in a changing room`: `the floor`, `the wall`, `the door`, `a bench`, `a towel`, `a towel rack`, `a bag`, `a backpack`
- `in a classroom`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `a desk`, `the teacher desk`
- `in a computer area`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `a table`, `a computer desk`, `a keyboard`, `a monitor`, `a computer`, `a computer mouse`
- `in a computer lab`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `a computer desk`, `a keyboard`, `a monitor`, `a computer`, `a computer mouse`
- `in a display area`: `the windowsill`, `the floor`, `the wall`, `the door`, `a table`, `a mannequin`, `a display table`
- `in a dorm room`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the bed`, `the wardrobe`, `the door`
- `in a fitting booth`: `the floor`, `the wall`, `the door`, `a mirror`, `a curtain`, `a clothes hanger`, `clothing`, `new clothing`, `personal clothing`
- `in a fitting room`: `a chair`, `the floor`, `the wall`, `the door`, `a bench`, `a mirror`, `a curtain`, `a clothes hanger`, `clothing`, `new clothing`, `personal clothing`
- `in a frame garden pool`: `the pool floor`, `the pool ladder`, `the pool edge`, `a pool noodle`, `a floating mat`, `an inflatable ring`, `a ball`
- `in a field`: `grass`, `a fence`, `a ball`, `a bag`, `a backpack`, `a tree trunk`, `a dirt path`, `wildflowers`, `a hay bale`, `a wooden fence`, `a picnic blanket`
- `in a forest clearing`: `grass`, `a bag`, `a backpack`, `moss`, `a tree trunk`, `a fallen log`, `a rock`, `wildflowers`, `a picnic blanket`, `a tree stump`
- `in a garden`: `the wall`, `a seat cushion`, `the garden bench`, `a garden chair`, `a garden lounge chair`, `sand`, `grass`, `the door`
- `in a gymnasium`: `the floor`, `the wall`, `the door`, `the gym bench`, `a climbing frame`, `a gym mat`
- `in a hallway`: `the windowsill`, `the floor`, `the wall`, `the door`, `lockers`, `a bench`, `the rug`, `the stairs`, `the large mirror`, `the small mirror`
- `in a kitchen`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the kitchen counter`, `the dining table`, `a dining chair`, `the sink`, `the door`
- `in a laboratory`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `a lab bench`, `an equipment cabinet`
- `in a laundry room`: `the floor`, `the wall`, `the washing machine`, `the dryer`, `the sink`, `the door`
- `in a lecture hall`: `a chair`, `the floor`, `the wall`, `the door`, `a podium`, `a projector`, `a projector screen`
- `in a library`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `a table`, `a bookshelf`
- `in a living room`: `the sofa`, `a chair`, `the coffee table`, `the windowsill`, `the rug`, `the floor`, `the wall`, `a seat cushion`, `the door`, `the large mirror`
- `in a meadow`: `grass`, `a fence`, `a ball`, `a bag`, `a backpack`, `a tree trunk`, `a dirt path`, `wildflowers`, `a wooden fence`, `a picnic blanket`
- `in a locker area`: `the floor`, `the wall`, `the door`, `lockers`, `a bench`, `a towel`, `a towel rack`, `a bag`, `a backpack`
- `in a lounge`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `a table`, `a lounge sofa`, `a vending machine`, `a coffee table`
- `in a principal office`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `a desk`, `a cabinet`
- `in a public toilet`: `the floor`, `the wall`, `the toilet`, `the sink`, `the door`, `the small mirror`, `a toilet stall`
- `in a reading area`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `a table`, `a bookshelf`, `books`, `a book`
- `in a science lab`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `a lab bench`, `science equipment`, `an equipment cabinet`
- `in a seminar room`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `a table`, `a projector`, `a projector screen`
- `in a shed`: `a chair`, `the floor`, `the wall`, `the workbench`, `the door`
- `in a shower room`: `the floor`, `the wall`, `the shower`, `the shower wall`, `the door`, `the shower head`, `the shower drain`, `a glass shower wall`, `a shower bench`, `the shower door`, `a glass shower door`
- `in a storage room`: `the floor`, `the wall`, `the door`, `storage racks`, `pallets`, `cardboard boxes`, `a concrete floor`, `a roll container`, `a waste container`, `old paper`
- `in a study area`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `a table`, `a bookshelf`, `a divider wall`, `books`, `a book`
- `in a swimming pool`: `the pool floor`, `the pool ladder`, `the pool edge`, `a pool noodle`, `a floating mat`, `an inflatable ring`, `a ball`
- `in the dunes`: `sand`, `a bag`, `a backpack`, `a beach towel`, `a dune`
- `in a toilet room`: `the floor`, `the wall`, `the toilet`, `the sink`, `the door`, `the small mirror`, `a toilet stall`
- `in a visitor area`: `a chair`, `the windowsill`, `the floor`, `the wall`, `the door`, `a bench`, `a table`
- `in a walk-in closet`: `the floor`, `the wall`, `the wardrobe`, `the door`, `the large mirror`, `the small mirror`
- `in a wildflower field`: `grass`, `a bag`, `a backpack`, `wildflowers`, `a picnic blanket`
- `in an attic`: `a chair`, `the windowsill`, `the floor`, `the stairs`, `the wall`, `the wardrobe`, `the workbench`, `the door`
- `in an indoor built-in pool`: `the pool floor`, `the pool ladder`, `the pool edge`, `a pool noodle`, `a floating mat`, `an inflatable ring`, `a ball`
- `in an inflatable garden pool`: `the pool floor`, `the pool ladder`, `the pool edge`, `a pool noodle`, `a floating mat`, `an inflatable ring`, `a ball`
- `on a landing`: `the windowsill`, `the rug`, `the floor`, `the stairs`, `the wall`, `the door`, `the large mirror`, `the small mirror`
- `near a mossy grove`: `moss`, `a tree trunk`, `a fallen log`, `a rock`, `leaf litter`, `a tree stump`
- `near a quiet cove`: `grass`, `the shoreline`, `the lakeshore`, `a rock`, `a picnic blanket`
- `near a tide pool`: `sand`, `the shoreline`, `a rock`, `driftwood`, `pebbles`
- `near a waterfall`: `grass`, `a bench`, `a towel`, `a bag`, `a backpack`, `moss`, `a tree trunk`, `a fallen log`, `a beach towel`, `a rock`, `a wooden bridge`
- `near a wooden fence`: `grass`, `a fence`, `wildflowers`, `a hay bale`, `a wooden fence`
- `near the shoreline`: `sand`, `a towel`, `a beach towel`, `the shoreline`, `a rock`, `driftwood`, `pebbles`
- `on a forest trail`: `a bag`, `a backpack`, `moss`, `a tree trunk`, `a fallen log`, `a dirt path`, `a rock`, `a wooden bridge`, `leaf litter`
- `on a hill`: `grass`, `a bench`, `a fence`, `a bag`, `a backpack`, `a tree trunk`, `a dirt path`, `a rock`, `wildflowers`, `a hay bale`, `a wooden fence`, `a picnic blanket`
- `on a lakeside dock`: `a bench`, `a towel`, `a bag`, `a backpack`, `a dock`
- `on a playground`: `grass`, `a bench`, `a climbing frame`, `a slide`, `a swing`, `pavement`, `a sandbox`
- `on a riverside path`: `a bench`, `a fence`, `a bag`, `a backpack`, `a tree trunk`, `a fallen log`, `a dirt path`, `the riverbank`, `a rock`, `a wooden bridge`
- `on a rocky beach`: `a bag`, `a backpack`, `the shoreline`, `a rock`, `driftwood`, `pebbles`
- `on a sports field`: `grass`, `a bench`, `artificial turf`, `a running track`, `a football goal`, `a football goal post`, `a fence`, `a football`
- `on a wooden bridge`: `a bag`, `a backpack`, `a wooden bridge`
- `on the lakeshore`: `grass`, `a towel`, `a bag`, `a backpack`, `a beach towel`, `the shoreline`, `the lakeshore`, `a dock`, `a rock`, `a picnic blanket`
- `on the riverbank`: `grass`, `a tree trunk`, `a fallen log`, `a dirt path`, `the riverbank`, `a rock`, `a picnic blanket`, `reeds`
- `on the sandy beach`: `sand`, `a bench`, `a ball`, `a towel`, `a bag`, `a backpack`, `a beach towel`, `a picnic blanket`, `a beach chair`
- `on campus`: `grass`, `a bench`, `pavement`, `a fence`

The executable source remains the surface generator conditions. If this summary and JSON ever differ, update both immediately.

### Environment -> Pose

Contract:

- Pose may validate against `environment.domain`, `environment.location`, `environment.room_area`, and `environment.surface`.
- Pose must not validate against `environment.time`, `environment.season`, or `environment.weather`.
- Environment validation belongs only on poses with hard setting requirements, not poses that are merely plausible in some places.

Risk:

- Surface/time/weather validation can overfit pose and cause too many silent skips.
- Missing hard environment validation can allow setting-dependent pose concepts in impossible places.

Rule:

- Use environment validation for obvious hard room/location compatibility only.
- Do not validate portable poses such as yoga-like postures merely because they are common in some locations.
- Use `environment.surface` only when the pose physically requires a specific selected object or support. Support/interacting wording such as `leaning against a surface` belongs in Action unless the value is rewritten as a purely static posture such as `leaning back`.

### Action -> Pose

Contract:

- Random Action and random Pose are mutually exclusive.
- Manual Action/Pose override text bypasses the random route and still outputs when the matching random toggle is disabled and the override text is non-empty.
- Random disabled with an empty override is a deliberate no-output path for that category.
- Pose is static body posture/form/expression. Action is movement, intent, object/support interaction, or broader scene behavior/context.
- The node sets internal state `activity.route` before category generation.
- `builder.action` validates against `activity.route=action`.
- `builder.pose` validates against `activity.route=pose`.
- The route is chosen only from Action/Pose categories whose random toggle is enabled.

Risk:

- Reintroducing partial action-to-pose compatibility modes can become a second action taxonomy and make random output directional again.
- Treating manual overrides as route candidates can accidentally block the still-random opposite category.

Rule:

- Do not use partial Action-to-Pose compatibility states in the current model.
- Do not validate pose/action compatibility from generated prompt text.
- Keep Action/Pose mutual exclusion at builder level through `activity.route`.
- Exclude disabled-random categories from the route choice, regardless of whether they contain manual override text.
- Manual override text always remains user-controlled output and should not be blocked by route validation.
- If wording adds support/object/environment context, prefer Action over Pose even when the body shape is static-looking.
- Static pose values may be derived from Action vocabulary, but random generation chooses Action or Pose instead of stacking both.

### Body Detail -> Pose / Action

Contract:

- Current Body Detail does not set pose/action state.

Risk:

- Body Detail phrases can imply posture or sexual action if vocabulary is too concrete.

Rule:

- Body Detail should describe the body region, not what the subject is doing with it.
- If wording implies posture or action, move it to Pose or Action.

### Clothing -> Pose / Action

Contract:

- Current authored clothing prompt states are available for targeted Action compatibility. Pose currently has no active Clothing-to-Pose state because current Pose wording is static body placement that can work over clothing or without clothing.
- Clothing-dependent Action values must validate against target-specific clothing state.
- Values that can work over clothing as well as without clothing do not need clothing validation.
- `clothing.coverage=clothed` is not proof that clothing prompt text exists. It only proves the SFW-gated clothed route won.
- Clothing emits Action-targeted existence/group states under the target namespace: `clothing.action.exist`, `clothing.action.upper_body.exist`, `clothing.action.lower_body.exist`, `clothing.action.underwear.exist`, and `clothing.action.swimwear.exist`.
- Future Clothing-to-Pose compatibility must use its own target namespace, such as `clothing.pose.exist`, but only after a concrete static Pose value truly needs clothing.

Risk:

- Actions that assume nudity, dressing, showering, or exposed body parts can conflict with clothed output.
- Actions or future poses that assume an actual garment, underwear, or swimwear can conflict with nude output.
- Over-validating static body-part placement poses against clothing can remove valid prompts where the same hand placement works over clothing.
- Validating against many concrete clothing strings creates brittle pose/action logic and duplicates clothing knowledge outside the Clothing category.

Rule:

- Add clothing/body coverage validation only for concrete pose/action values that directly require it.
- Do not globally block poses just because clothing is selected.
- Validate generic clothing actions against `clothing.action.exist`.
- Validate upper/lower clothing actions against `clothing.action.upper_body.exist` or `clothing.action.lower_body.exist`.
- Clothing-displacement exposure actions use upper/lower clothing state because the hard requirement is actual clothing to move aside. Use upper-body state for breast exposure and lower-body state for buttocks, vulva, penis, or anus exposure.
- Validate underwear actions against `clothing.action.underwear.exist`.
- Validate swimwear actions against `clothing.action.swimwear.exist`.
- Never validate Action against `clothing.pose.*` and never validate Pose against `clothing.action.*`.
- Validate nudity, missing-garment, or explicit exposed-region values against documented body/clothing coverage states when those exact states exist.
- Do not add clothing validation to static hand-placement wording unless the value explicitly requires visible skin, nudity, a specific garment, or a covered/exposed body state.
- Prefer one shared target-specific clothing state over many value-specific validations. Add narrower states only when the current shared state becomes too broad for a concrete validation need.

### Environment -> Lighting

Contract:

- Environment owns time/weather/season as scene context.
- Lighting owns illumination, light quality, and lighting setup.

Risk:

- Environment time and Lighting can contradict each other, such as midday plus moonlit lighting.

Rule:

- When Lighting vocabulary is filled, it may validate against `environment.domain` and `environment.time` only when the lighting value directly depends on them.
- Do not move lighting mood or light direction into Environment.

### Environment -> Composition

Contract:

- Environment owns location and surface.
- Composition owns camera/framing/perspective.

Risk:

- Surface values can sneak in camera wording or composition can sneak in location details.

Rule:

- Environment says where the subject is.
- Composition says how the image frames the subject.

### Style -> Clothing Style

Contract:

- Clothing style describes outfit direction.
- Style category describes image medium/aesthetic/rendering.

Risk:

- Values like "fashion editorial", "casual style", or "cinematic" can land in the wrong category and duplicate intent.

Rule:

- If the value changes garments, it belongs in Clothing.
- If the value changes rendering or aesthetic treatment, it belongs in Style.
- If it changes camera/framing, it belongs in Composition.

### Quality -> All Categories

Contract:

- Quality is final model steering and should not set scene facts.

Risk:

- Quality tags can drown the actual prompt or duplicate preset tags.

Rule:

- Keep Quality short.
- Preset quality fragments and Quality category vocabulary should be reviewed together before adding model-specific tags.

## Chaos Prevention Checklist

Before adding or changing any value, builder, generator, state, tag, condition, validation, category order, or resolve order, check:

- Does this value duplicate a fact another category already owns?
- Can it contradict a category that resolves earlier or later?
- If this is clothing, action, or pose, have all relevant relationship sections been checked?
- Does the needed validation already exist as state?
- If a relationship exists, is it expressed through the broadest accurate reusable state instead of repeated concrete value checks?
- Is the value too concrete for random use?
- Will it combine with many sibling builders and overload the prompt?
- Should this be a broad value, a gated value, a new state contract, or a skip-weight adjustment?
- Does the prompt still make sense if nearby categories skip?

## Current Priority For Cleanup

PromptBuilder V2 should be stabilized before adding more vocabulary.

Highest-value context-guided refill areas:

- refill Body Detail slowly and audit builder count plus skip weighting;
- refill authored Clothing values slowly and audit whether whole/upper/lower routes stay coherent;
- refill Environment slowly and audit layer skip weighting so setting text stays person-focused;
- keep Action/Pose random coordination limited to the internal route unless the route model is intentionally redesigned;
- keep Style, Lighting, Composition, and Quality empty or very sparse until their boundaries are actively designed.
