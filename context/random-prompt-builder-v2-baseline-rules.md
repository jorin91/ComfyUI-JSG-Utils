# Random Prompt Builder V2 Baseline Rules

## Purpose

This file is the strict general baseline for all future Random Prompt Builder V2 work.

Use it before adding values, generators, states, validation, or category logic. More specific files may add category details, but they should not contradict this baseline.

## Refill Workflow

PromptBuilder V2 should grow from user-provided desired outcomes, not from bulk vocabulary filling.

Workflow:

1. User describes a desired aspect or result.
2. Agent checks `context/random-prompt-builder-v2-category-relations.md` before adding or changing any value, builder, generator, state, tag, or validation.
3. Agent chooses the correct category, builder, generator, state, and validation location.
4. Agent adds only a small number of values needed for that outcome.
5. Agent updates the central relation map when the change creates or changes any relationship.
6. Agent updates relevant category context and state documentation.
7. Agent avoids adding adjacent vocabulary just because it seems related.

Small focused value sets are preferred over broad lists. A builder with a few coherent values is better than a builder with many loosely related values that combine unpredictably.

## Validation Feedback Rule

When the user points out a validation mistake, missed compatibility rule, or model-confusing combination, record the lesson in durable context during the same work session.

The context update should include:

- what validation was missed;
- why the combination confuses the image model or breaks category logic;
- which category relationship or builder/generator rule should prevent it next time.

Do not treat user validation feedback as a one-off fix. Convert it into a reusable rule or category note so future additions are checked against it.

## State Key Source / Target Contract

State keys must make the owner and target clear.

If a state represents a category's own selected fact, it may stay source-owned without a target segment, such as `clothing.coverage`, `clothing.style`, `pose.general`, or `environment.location`.

If a state is created so another category can validate against it, the key must include the target category after the source category:

- Clothing-created state for Pose starts with `clothing.pose.*` only when a concrete future Pose value truly needs clothing state.
- Clothing-created state for Action starts with `clothing.action.*`.
- Action-to-Pose compatibility state is not active. Random Action/Pose mutual exclusion is owned by the internal `activity.route` state.

Do not use one generic source-only compatibility key for multiple targets. A Pose-targeted key must not be reused by Action, and an Action-targeted key must not be reused by Pose. This prevents unrelated target domains from overwriting or overloading the same state.

Target-specific existence facts use the `exist` suffix, for example `clothing.action.exist`, `clothing.action.upper_body.exist`, and `clothing.action.underwear.exist`.

## Builder Versus Value Responsibilities

### Builder-Level Validation

Use builder-level `conditions` when every meaningful value in the builder shares the same gate.

Examples:

- the whole builder is adult-only;
- the whole builder requires `clothing.coverage=clothed`;
- the whole builder requires a specific scene domain;
- the whole builder only makes sense when a prerequisite state exists.

Do not repeat the same condition on every value when a builder-level condition is the correct shared gate.

### Builder-Level State

Use builder `state_export` or builder-level state behavior when the builder is recording a general fact from a selected slot and the exact value details do not matter beyond existence or selected text.

Examples:

- selected clothing type/item stored from an `{item}` slot;
- selected location stored from a `{location}` slot;
- selected broad style stored from a `{style}` slot;
- selected time/weather/season stored from a matching slot.

Builder state is appropriate when:

- the state means "this builder selected something";
- the state value is simply the resolved slot text;
- the same state behavior applies to every meaningful value in that builder.

### Value-Level Validation

Use value-level `conditions` when only some values in a builder need a gate.

Examples:

- one value is adult-only, but sibling values are not;
- one value requires NSFW allowed, but sibling values are SFW;
- one value only fits indoor rooms;
- one pose only fits lying actions.

### Value-Level State

Use value-level or generator-value `state_set` when the value owns a specific detail or exceptional fact.

Examples:

- an authored clothing value explicitly exposes a body region;
- a clothing item covers a precise body region;
- a value adds special compatibility metadata that cannot be derived from the selected text alone.

Do not use builder-level state for value-specific facts.

## Builder Values, Slots, And Word Order

Hard boundary:

- Builder value entries own slots.
- Builder value entries own `template` and `slots`.
- Generators are universal value providers.
- Generators may validate values with universal `state`/`tag` conditions.
- Generators must never contain `template`, `slots`, or `slot` conditions.
- Loader/runtime logic must reject or skip universal generators that contain slot/template logic instead of interpreting it.

Builders should use multiple value entries to create controlled variation in wording and phrase order.

Use separate builder values for different grammar shapes:

- `{item}`
- `{pre} {item}`
- `{item} {post}`
- `{modifier} {item} {detail}`
- any other wording that needs a distinct order.

Each slot should point to a generator that is compatible with that exact template.

Rules:

- Do not force all vocabulary through one generic generator if some words only work before or after the item.
- Do not create one large "aspect" generator whose values only work in some templates.
- Prefer small, template-compatible generators.
- Slot validation belongs inside the builder value that owns the slot.
- Generators must not validate against builder-local slots.

## SFW And NSFW Generator Split

Future content-bearing generators should be split into SFW and NSFW variants.

Pattern:

- create an SFW generator for ordinary/safe values;
- create an NSFW generator for adult-only or direct-nudity/sexual values;
- make the builder contain separate value entries that draw from the SFW or NSFW generator as appropriate;
- gate the NSFW builder value or NSFW generator with the relevant state conditions.

Typical gates:

- adult-only but not direct nudity: `subject.adult=true`;
- direct visible nudity or missing clothing that can create nudity: `subject.adult=true` and `content.nsfw_allowed=true`.

The SFW/NSFW split keeps prompt behavior readable because a builder clearly shows which random route it is taking.

Body Build and Body Detail are the exception: body vocabulary can become NSFW quickly, so body sections should use precise body visibility/adult/NSFW validation instead of a blanket SFW/NSFW generator split.

Neutral structural generators may remain single only when they genuinely have no SFW/NSFW distinction and do not contain content that changes safety or explicitness. If a neutral generator later gains adult or explicit values, split it.

When one builder contains multiple sibling values for the same result route and those values are separated by content class, keep the builder value order `sfw -> nsfw -> sexual`. This is a readability and maintenance convention only; runtime selection still validates candidates first and randomly chooses from the valid candidates.

## Category Relationship Rules

### Validation Order

State conditions may depend only on documented global state that already exists from state profiles or earlier resolved categories/builders. V2 does not lazy-load later builders for validation.

Rules:

- If a category or generator validates against state from another category, the producing category must appear earlier in `resolve_order`.
- When adding or changing generator value conditions, inspect where that generator is used before deciding whether `resolve_order` must change.
- Categories that produce state consumed by active later categories should resolve early.
- Categories that do not produce state consumed by active later categories should move toward the end of `resolve_order`.
- Do not depend on prompt text or concrete value strings for validation.
- Manual overrides remain text-only and do not provide generated state for later validation beyond profile fallback state.

### Action And Pose

Action is richer prompt context than Pose. Action can imply activity, scene intent, movement, body dynamics, object interaction, and mood; Pose is usually a more static body-position supplement.

Random Action and random Pose are mutually exclusive. The node sets internal state `activity.route` to either `action` or `pose` before category generation:

- `builder.action` validates against `activity.route=action`.
- `builder.pose` validates against `activity.route=pose`.
- when both Action and Pose random toggles are enabled, `activity.route` randomly chooses one side.
- when only Action random is enabled, `activity.route=action`.
- when only Pose random is enabled, `activity.route=pose`.
- categories with random disabled are excluded from this random route choice.
- manual override text bypasses `activity.route` validation because disabled-random categories emit the override text directly.
- random disabled plus an empty override remains a deliberate "do not generate this category" option.
- if both Action and Pose random toggles are disabled, the route may still be set internally for debug consistency, but no random Action/Pose builder uses it.

This replaces the old partial Action-to-Pose compatibility system. Do not reintroduce partial Action/Pose compatibility keys unless the whole route model is intentionally redesigned.

Action and Pose must validate against scene context when concrete values are added.

Allowed environment dependency:

- `environment.domain`
- `environment.location`
- `environment.room_area`
- `environment.surface`

Use Environment validation only for hard "can this physically happen here?" requirements. Do not validate for social acceptability or ordinary plausibility. Use `environment.surface` only when a concrete object or support is physically required. Do not validate Action or Pose against environment time, season, or weather unless that relationship is explicitly redesigned and documented.

Boundary examples:

- portable/general actions such as washing, stretching, yoga, dancing, or bodyweight exercise stay ungated unless the wording names a hard object or facility;
- fixed-object/facility actions such as making a bed, showering, mirror posing, gymnastics apparatus, or fixed fitness apparatus validate at the broadest accurate Environment level;
- use direct `environment.room_area` validation when that is already the broadest accurate state; introduce a reusable Environment-to-Action state only when multiple room/area values must represent the same hard capability.

Action/Pose values should logically fit:

- indoor versus outdoor;
- broad location;
- room or area;
- the internal Action/Pose route.

Active verbs such as touching, caressing, adjusting, washing, grabbing, object-holding, and leaning against support belong in Action. Static held posture/form/expression belongs in Pose. Static pose values may still be derived from Action vocabulary, but random generation chooses Action or Pose instead of stacking both.

### Body Build And Body Detail

Body Build and Body Detail must validate against clothing visibility when concrete body values are added.

Rules:

- visible body details should require exact visibility or coverage states;
- covered body regions should not emit exposed-region details;
- unspecified clothing does not prove exposure;
- body values should not infer visibility from missing state;
- clothing items/aspects should write only the exact body coverage states they concretely know;
- uncertain clothing coverage should choose the safe route.

Body Build is broad and whole-body focused. Body Detail is regional and may require precise coverage/adult/NSFW validation.

### Clothing And Body

Clothing owns garments, clothing style, and clothing behavior/aspects.

Body categories own the body itself.

If a clothing value says a body region is covered or exposed, it may write a precise coverage state. If a body value needs visibility, it validates against that precise state.

Do not describe the same body fact in both Clothing and Body Detail.

### Environment, Composition, Lighting, Style, Quality

Environment says where the subject is.

Composition says how the image is framed.

Lighting says how the scene is illuminated.

Style says how the image is rendered or aesthetically treated.

Quality says final model/fidelity/detail steering.

Do not duplicate the same visual intent across these categories.

Weather and season are outdoor visual environment context in the current simple baseline. They must not emit for `environment.domain=indoor`, because indoor prompts such as `indoors, winter, rainy weather` confuse the model unless a future explicit indoor-visible weather/window context is designed.

## State Rules

- Every used state must be documented in `random-prompt-builder-v2-states.md`.
- Every meaningful selected value must set or export at least one state.
- If the value has no special metadata, store the selected value itself through builder `state_export` or value `state_set`.
- Empty skip values do not need to write state unless the skip itself is a meaningful route, such as `clothing.coverage=clothed`.
- Do not document planned states as current states.
- Add states only when concrete values set or validate them.
- Prefer states over tags for meaningful validation.
- Prefer specific states over broad ambiguous states.
- Do not infer exposure, clothing, location, action, or style from missing state.
- Use state priority only for real conflicts.

## Prompt Discipline

The generated prompt should remain coherent, not maximal.

Rules:

- fewer compatible values are better than many loosely compatible values;
- avoid over-specific values unless the user requested that exact result;
- avoid values that tell the model too much concrete micro-detail at once;
- use empty skip values deliberately;
- keep category output useful even if neighboring categories skip;
- do not add values that only work when several unrelated random choices happen to align.

## Cleanup Rule

If prompts become messy again, prefer cleanup in this order:

1. remove or narrow over-specific values;
2. increase skip weight or reduce builder emissions;
3. split generators by grammar or SFW/NSFW route;
4. add precise state validation;
5. only then add new builders or states.
