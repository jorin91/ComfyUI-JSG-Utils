# Random Prompt Builder V2 Category Map

## Purpose

This file is the compact ownership map for Prompt Builder V2 categories.

Use it when the generated prompt starts becoming chaotic, too concrete, or over-combined. Category-specific detail still belongs in `context/random-prompt-builder-v2-categories/*.md`; this file defines the high-level boundary of each category and the expected prompt budget.

## Global Prompt Discipline

V2 should generate coherent prompts by selecting a small number of compatible facts, not by exhausting every possible detail system.

Before adding or changing any category value, builder, generator, state, tag, condition, or validation, check `context/random-prompt-builder-v2-category-relations.md`. If the change creates or changes a cross-category relation, update that central map immediately.

Rules:

- One category should usually own one conceptual job.
- Do not describe the same visual fact in multiple categories.
- Prefer broad steering unless a concrete builder needs precision.
- Specific anatomical, clothing, action, or environment details must be gated by state when they can contradict another category.
- More vocabulary is not automatically better; add values only when they improve coherent random output.
- When a category grows too noisy, reduce builder count, add skip weight, or introduce stronger category-level modes before adding more validation.
- A prompt should tolerate missing categories. Missing state must not be treated as proof of exposure, clothing, location, action, or style.
- If a value requires multiple other facts to make sense, it probably belongs behind a narrower state contract or should be split into a less specific value.

## Category Ownership

### Subject

Owns:

- one generated person;
- adult/non-adult state;
- broad gender state when generated or seeded by profile;
- age-range prompt wording.

Does not own:

- clothing;
- body detail;
- pose/action;
- ethnicity;
- model/style quality tags.

Prompt budget:

- exactly one subject phrase when random Subject is enabled.

### Ethnicity

Owns:

- base ethnicity;
- optional mix;
- compatible skin tone.

Does not own:

- facial beauty, body shape, style, or lighting;
- cultural clothing unless later introduced as clothing/style through explicit state.

Prompt budget:

- one complete ethnicity phrase.

### Body Build

Owns:

- whole-body stature, mass, proportions, broad muscularity, whole-body tone, broad skin tension or softness, broad non-region tanning.

Does not own:

- named body parts;
- regional bones, tan lines, abdomen/breast/pelvic/buttock details;
- clothing-driven visibility.

Prompt budget:

- current active output allows at most one mass/muscle/definition/bone-visibility trait plus optional whole-body proportions.

### Body Detail

Owns:

- regional body structure;
- body parts and subparts;
- local skin/surface details;
- regional bones, muscle definition, tan lines, and sensitive-region details.
- non-action hair appearance details such as hairstyle and hair color.

Does not own:

- whole-body build;
- authored clothing prompt details;
- pose/action;
- camera framing.

Prompt budget:

- only visible/allowed regions should emit concrete detail.
- Sensitive or exposed-region detail must remain behind exact coverage and adult/NSFW gates.
- Per body part, emit at most one body-part aspect. A breast body-part value may coexist with one areola subpart value and one nipple subpart value, but not with another breast aspect from a separate builder.
- Avoid stacking many microscopic details in one generated prompt unless a deliberate detail mode is added later.

### Clothing

Owns:

- nude versus clothed route;
- broad outfit style;
- authored complete clothing prompts for the whole body, upper body, or lower body;
- SFW versus NSFW clothing prompt routing.

Does not own:

- body anatomy itself;
- pose/action;
- setting;
- fashion photography style unless it becomes a clothing style value.

Prompt budget:

- clothing should stay concise and coherent.
- clothing may validate against Environment-owned location theme states, but it should not own the location/theme taxonomy itself.
- Prefer one complete authored whole-body value when garments must agree with each other.
- Use upper/lower authored values only when those halves can vary without contradiction.

### Environment

Owns:

- indoor/outdoor domain;
- person-focused location, room/area, surface, sparse condition, season, weather, time, social context, and props.
- broad accepted Clothing theme states at the location level, with blank/no-location values remaining permissive.
- current mapped location families include home, school/university, library, swimming pool, clothing store, and outdoor nature.

Does not own:

- pose/action;
- detailed lighting direction or mood;
- camera composition;
- general visual style.

Prompt budget:

- environment should anchor the scene, not crowd it.
- Domain is always useful; deeper environment layers should skip often enough to avoid long setting chains.

### Action

Owns:

- what the subject is doing;
- activity, movement, intent, object interaction, and scene behavior;
- the prompt-facing selected Action state such as `action.general`, `action.sport`, `action.nsfw`, or `action.sexual`.

Does not own:

- static pose wording unless required by the action phrase;
- environment details beyond validating against domain/location/room area;
- clothing/body visibility except through documented state contracts.

Prompt budget:

- at most one action group should dominate the scene.
- Action route families belong as values inside the single Action builder, not as multiple stacked builders.
- Random Action is mutually exclusive with random Pose through internal `activity.route`.
- NSFW Action owns clothing-displacement exposure and private/nudity-directed actions; Sexual Action owns explicit sexual acts or sex-contextual gestures.

### Pose

Owns:

- body posture, stance, static held forms, expression/gaze, body-part placement, and pose-like visibility presentation.

Does not own:

- action intent;
- environment surface/time/weather;
- body anatomy or clothing item detail.

Prompt budget:

- pose should complement action.
- Random Pose is mutually exclusive with random Action through internal `activity.route`.
- Manual Pose override text bypasses route validation; random disabled with an empty override intentionally emits nothing.
- Static pose values may be derived from Action wording when the action phrase contains a useful held form; the active movement or object/context part stays in Action.
- NSFW Pose owns static sensitive/revealing presentation; Sexual Pose owns explicit sexual static gestures or expressions.

### Composition

Owns:

- camera framing, crop, perspective, shot distance, and image composition.

Does not own:

- lighting;
- subject/body/clothing facts;
- style or quality tags.

Prompt budget:

- should usually emit one camera/framing instruction when filled.

### Lighting

Owns:

- light direction, light quality, light intensity, mood from illumination, and lighting setup.

Does not own:

- time of day except where phrased as visible lighting;
- environment weather;
- rendering style or quality.

Prompt budget:

- one lighting setup should dominate.

### Style

Owns:

- medium, rendering style, aesthetic family, visual treatment.

Does not own:

- clothing style;
- model quality tags;
- subject anatomy.

Prompt budget:

- one style direction should dominate unless future preset logic explicitly supports style blending.

### Quality

Owns:

- final fidelity, detail, quality, and model-steering tags.

Does not own:

- subject or scene content;
- style/medium;
- camera framing.

Prompt budget:

- concise final steering only.

## Current High-Risk Areas

- Clothing can become chaotic if the old item/aspect matrix is rebuilt instead of using authored complete values.
- Body Detail can become over-specific if many regional builders are refilled and allowed to emit together.
- Environment can create long chains if domain, location, room/area, surface, season, weather, time, social context, and props are all refilled without skip discipline.
- Action and Pose can contradict if manual text combines incompatible concepts; random Action/Pose output avoids this by using `activity.route`.
- Broad style, clothing style, and quality can accidentally overlap if style/quality vocabulary is later added without strict ownership.

## Stabilization Preference

When prompts become messy, prefer these fixes in order:

1. reduce emitted builder count or increase empty skip weight;
2. move over-specific wording to a narrower generator;
3. add or tighten state contracts between categories;
4. split broad generators only when their vocabulary has genuinely different compatibility rules;
5. add new states only when an existing concrete conflict cannot be solved with current states.
