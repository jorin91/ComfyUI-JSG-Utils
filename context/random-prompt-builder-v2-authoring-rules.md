# Random Prompt Builder V2 Authoring Rules

## State Policy

States start from absolute null.

Before adding or changing any value, builder, generator, state, tag, condition, validation, or metadata level, check `context/random-prompt-builder-v2-category-relations.md`.

If that change creates, removes, narrows, broadens, or depends on a relationship between categories, update the central relation map in the same work session. This is mandatory even for small value additions.

Only document states that exist because a concrete builder/value sets or validates them. Every used state must be documented in `context/random-prompt-builder-v2-states.md`.

That state index must include:

- state name;
- type;
- meaning;
- where it is set;
- where it is used/validated.

State profiles:

- live in `data/random_prompt_builder_v2/state_profiles/`;
- seed initial state/tags before categories resolve;
- should be used sparingly because value-owned state remains preferred;
- may be useful when manual category overrides skip a state-setting generated value;
- must only write documented state keys;
- must not replace value-level state writes when a generated value actually owns the fact;
- may define debug-only `ignore_state_keys` and `ignore_tags` arrays. These arrays bypass only the individual matching state/tag condition checks, not the whole value, builder, or generator. If a value has three state/tag checks and one key is ignored, only that one check is neutralized; the other two checks still validate normally.

Current state profiles all seed `subject.adult=true` at fallback priority so adult-gated values remain available when the user manually overrides Subject. Profiles set `content.sfw_allowed`, `content.nsfw_allowed`, `profile.content_mode`, and `profile.gender_mode`. Gender-specific profiles also seed `subject.gender` at fallback priority for manual Subject overrides. Generated Subject values may overwrite the fallback only after validating against `profile.gender_mode`. All profiles include empty `ignore_state_keys` and `ignore_tags` arrays by default.

## Naming Policy

Builder and generator `id` values must start with their source:

- builder ids start with `builder`;
- universal generator ids start with `generator`;
- category ids, preset ids, and state profile ids keep their own domain names and do not use the builder/generator source prefix.

ID format:

```text
<source>.<domain/category that owns it>.<subidentifier such as builder/generator group>.<optional target domain/category>.<sfw/nsfw when it is a meaningful route split>.<item/group/etc>
```

Examples:

- `generator.clothing.style`
- `generator.pose.nsfw`
- `generator.pose.sport`
- `generator.clothing.sfw.whole`
- `generator.clothing.nsfw.whole`
- `builder.clothing.coverage`
- `builder.clothing.whole`
- `builder.pose`

Use `sfw` / `nsfw` only when that distinction is part of the actual route or meaning. Do not add `sfw` merely because a value is safe by default. For example, sport pose can be `generator.pose.sport`; NSFW pose is `generator.pose.nsfw`; whole-body clothing has both `generator.clothing.sfw.whole` and `generator.clothing.nsfw.whole` because the same authored route is intentionally split.

State keys may omit the source prefix. Prefer concise semantic state such as `clothing.coverage`, `clothing.style`, `pose.general`, or `pose.nsfw` when the state represents the selected fact rather than the implementation source.

State key format:

```text
<domain/category that sets it>.<subidentifier such as builder/generator group>.<optional target domain/category>.<sfw/nsfw when meaningful>.<item/group/etc>
```

State key source/target rule:

- If a state represents a category's own selected fact, use that category as the domain and do not invent a target. Examples: `clothing.coverage`, `clothing.style`, `pose.general`.
- If a state is created specifically so another category can validate against it, include the target category directly after the source domain. Example: Clothing writing an action-compatibility fact uses `clothing.action.*`, not generic `clothing.*`.
- Do not let multiple targets share one vague source-only key when the state was made for a target. Action clothing compatibility must use precise `clothing.action.*` state instead of validating Action against `clothing.pose.*`.
- Targeted compatibility states should be as broad as possible inside that target namespace, but the target namespace itself is mandatory once the state exists for another category.
- For target-specific existence states, use the `exist` suffix in this project, such as `clothing.action.exist`, `clothing.action.upper_body.exist`, and `clothing.action.underwear.exist`. Future Pose-specific clothing states should use the same suffix inside the Pose target namespace, such as `clothing.pose.*.exist`.

Reuse existing state keys whenever their meaning fits. Add a new state only when a concrete value sets it or a concrete value validates against it.

When many concrete values share one compatibility meaning, let those values write one shared state instead of making another category validate against many text choices. For example, clothing values that logically contain underwear for action compatibility write `clothing.action.underwear.exist`, so an underwear dressing or adjustment action can validate against that one state. Do not create a target-specific state until a concrete target category actually needs it.

State priority:

- state writes default to priority `0`;
- only a strictly higher priority may overwrite an existing state key;
- equal priority does not overwrite;
- use priority only for concrete conflicts, not as routine decoration;
- `state_set` may use top-level `state_priority`, or object-form values such as `{ "value": "covered", "priority": 1 }`;
- object-form `state_export` may include `"priority": 1`;
- state profile subject fallback values use priority `-1` so valid generated subject values can overwrite them at default priority.

Adult / NSFW / sexual policy:

- use `subject.adult=true` plus `content.nsfw_allowed=true` for NSFW-gated values, including visible nudity, revealing/private/sensitive presentation, adult-only body-touch actions, static sensitive-area placement poses, and NSFW clothing/action/pose routes;
- `content.nsfw_allowed=false` must block NSFW-gated values even when `subject.adult=true`;
- use `.nsfw` routes for gated adult-sensitive values that are not necessarily sexual acts;
- reserve `.sexual` routes for explicitly sexual acts or sex-contextual values;
- if every meaningful value in a builder shares an adult/NSFW gate, put the gate on the builder;
- if only some values are NSFW-gated, keep the gate on those values.

Clothing authored-value exception:

- clothing no longer uses the old item/aspect generator matrix;
- use complete authored clothing values in whole-body, upper-body, or lower-body SFW/NSFW generators;
- values may contain commas when that keeps a layered clothing idea coherent;
- SFW values may be suggestive, wet, layered, or visually descriptive when the authored outcome remains clothed and not directly nude;
- NSFW clothing values belong in the matching `.nsfw` generator and must stay adult/NSFW gated;
- do not split a coherent clothing outcome into random item, color, fit, wetness, transparency, damage, and exposure fragments unless a future concrete design explicitly replaces the authored-value model.

Atomic value wording:

- Generator and builder values should describe one clear option, not a menu of alternatives.
- Do not use combined alternatives such as `A or B`, slash pairs such as `A/B`, or vague paired choices when they would ask the image model to guess between different outcomes.
- Split alternatives into separate values and give each value its own validation/state metadata when needed.
- Use combined wording only when the phrase is a normal single concept rather than a choice, and document that exception in the category context if it is easy to misunderstand.
- Treat user-provided value lists as semantic intents, not literal prompt text. Rewrite each value into a standalone prompt phrase that the image model can understand without knowing the builder/generator category.
- When a value comes from a specialized group such as dance, yoga, gymnastics, fitness, NSFW, or sexual action/pose, include the needed context in the value text itself when the bare phrase would be ambiguous.
- Alternative wording is allowed when the image model can plausibly interpret it differently, when one wording is more standalone/general than another, or when the wording changes the steering strength. Do not collapse useful synonyms merely because a nearby value has the same human-level meaning.
- If a different wording changes category ownership, route it to the right category instead of treating it as a duplicate. For example, `wall squat` is a pose term, while `squatting against a wall` steers support/environment context and belongs in Action.
- Pose wording should stay static: body posture, body form, expression, or specific body-part placement. Action wording owns doing, movement, execution, undertaking, interaction, support/object use, and wording paired with movement.
- Active verbs such as touching, caressing, adjusting, washing, grabbing, object-holding, and leaning against support belong in Action. Pose may keep static derivatives from those actions, such as `hands on the face`, `one hand on the cheek`, or `wall squat`.
- When Action contains useful static posture information that does not yet exist in Pose, derive a separate atomic Pose value from it. Keep the Action value when it carries movement/object/context; add only the static posture/form/expression piece to Pose.
- When a Pose or Action generator grows beyond roughly 25 non-empty options, split it into smaller semantic generators and let the builder contain multiple values pointing to those sets.
- When sibling builder values target the same kind of result but are split by route class, author them in readable safety order: `sfw -> nsfw -> sexual`. Here `nsfw` means adult-gated sensitive/revealing/private content that is not necessarily a sexual act, and `sexual` means explicitly sexual or sex-contextual content. This ordering is for maintainability only; it does not imply selection priority because builder values are still randomly chosen after validation.

Validation boundary:

- Before adding a value, check the central relation map and ask which other category facts this value physically depends on or conflicts with.
- Validate on physical/technical possibility, not on social acceptability or commonness.
- Use the broadest accurate state first, then narrow only when the broad state is not accurate enough.
- General actions stay broad when they do not name a fixed object/facility. For example, washing is not automatically showering or bathing, and urinating has no Environment validation even though many resulting places are strange.
- Fixed-object or facility wording does validate. For example, `making the bed` requires a bedroom/dorm room, mirror actions require mirror-capable room/areas, and shower/bath wording requires shower/bath-capable room/areas.
- Do not add `missing` fallbacks for a hard required state when missing would reintroduce impossible prompts. If an action truly requires a bed, mirror, shower, bath, pool, or apparatus context, the matching state must be present and valid.

State and tag ownership preference:

- prefer builder-level `state_set`, `state_export`, `tags_add`, and `tags_remove` when the metadata applies to every non-empty result produced by that builder;
- use builder-level metadata for broad facts such as "this builder produced clothing" when the fact is not affected by individual values;
- use builder value metadata when sibling builder values produce meaningfully different facts;
- use generator value metadata when variation inside a slot generator cannot be captured by the builder value, such as one style value implying underwear while another style value implies swimwear and sibling style values imply neither;
- avoid repeated per-value metadata when a builder-level state or tag can express the same fact once;
- do not move metadata upward if an empty skip route would then falsely set it.

Supported metadata levels:

- builder objects may set fixed states/tags with `state_set`, `state_priority`, `tags_add`, and `tags_remove` after a non-empty builder result is selected;
- builder objects may set slot-derived states with `state_export` after a non-empty builder result is selected, using the chosen builder value's resolved slots;
- builder value objects may set fixed states/tags with `state_set`, `state_priority`, `tags_add`, and `tags_remove`;
- builder value objects may set slot-derived states with `state_export`;
- generator value objects may set fixed states/tags with `state_set`, `state_priority`, `tags_add`, and `tags_remove`;
- generator values must not use slot-derived state because generators do not own or see builder slots.

State export notes:

- prefer `state_export` when recording selected slot text into a state key, such as an item name, location, time, weather, or broad style;
- `state_export` can write one slot result into multiple state keys when the same selected item occupies both a broad conflict state and a specific tracking state;
- empty exported slot text is skipped by default, so empty generator choices do not create state noise;
- if a value or builder really needs to mark an explicit empty state, `state_export` may use object syntax with `"empty": "null"`;
- explicit `null` states count as `missing` for `exists`/`missing`, but `equals null` only passes when the state key was actually written as null;
- every generated state must still use a documented state key.

Coverage state authoring:

- prefer coverage facts over assuming exposure from missing data;
- add only the body-region coverage states required by concrete builders, generators, or values;
- do not create unrelated region states while working on one body area;
- inspect relevant authored clothing values before adding Body Detail visibility logic;
- uncertain clothing coverage should choose the safe route;
- authored clothing values may set coverage/exposed states when they explicitly mention bare skin, exposed body parts, displaced garments, open garments, transparency, or similar visibility.

Aspect generator granularity:

- Split generators by logical aspect and region when several compatible details can appear in one prompt.
- Do not place all values for a broad aspect under one generator if that forces only one detail to be selected.
- For Body Detail body parts, keep one active builder per body part and let that builder select one aspect per prompt. Do not add separate size, shape, skin, tanning, firmness, or other aspect builders for the same body part.
- Body subparts may have their own builder when requested. For example, one breast body-part value may coexist with one areola value and one nipple value.
- Bone definition should be region-split because collarbones, ribs, pelvis/hips, and limb joints can coexist.
- Tanning should be region-split because general skin tan, abdomen tan lines, breast tan lines, pelvic tan lines, and buttock tan lines can coexist across different regions; if the tanned region is a body part that already has a builder, place that route inside the existing body-part builder.
- Muscle and toning may share a builder/generator when they represent the same surface-definition role for that region.

## Builder Boundary

Hard boundary:

- builder value entries own slots;
- generators are forbidden from owning or reading slots;
- a category contains builder objects;
- each builder object produces one result inside that category by randomly choosing one valid value entry;
- a builder object is only a container and runner for its value entries;
- use multiple sibling builders only when the category intentionally stacks multiple independent prompt elements;
- if options are alternatives for the same conceptual slot, put them as sibling values inside one builder rather than separate builders;
- builders may have validation when the whole builder is unavailable under the same state/tag gate;
- builders have no slots;
- builders have no template;
- every builder `values` entry must be an object;
- every builder value entry owns its own value-specific validity conditions;
- every builder value entry owns its own `template` and `slots` when it needs `{}` construction;
- template assembly belongs only on builder value entries;
- conditions must not be added to prevent sibling values inside the same builder from combining, because a builder chooses exactly one valid value entry;
- a builder value is validated as a complete candidate: first non-slot value conditions, then slot/template resolution on temporary state, then an empty-result check;
- a builder value only counts as valid when its resolved result contains text, negative text, state, or tags, unless the value explicitly sets `allow_empty=true`;
- candidate slot resolution may use and mutate temporary state for that candidate, but only the final randomly chosen value may apply state to the real builder/category state;
- slot validation belongs only inside that same builder value entry's `slots`;
- slot validation only controls whether/how the selected value's sentence is assembled;
- slot validation does not decide whether the value entry itself is valid for random selection;
- generators are universal and are not bound to one builder by default;
- universal generator objects must not define `template` or `slots`;
- generator values must not define `template` or `slots`;
- generator objects and generator values must not contain `slot` conditions;
- generator values may set state and may filter by state/tag only;
- generators must never read, resolve, require, or validate builder slots, even when they are invoked from inside a builder slot;
- resolver code must not pass builder slot context into universal generator condition/value resolution;
- universal generators containing `template`, `slots`, or `slot` conditions must be rejected/skipped by loader logic;
- if a universal generator needs a fact from another selected value, the earlier value must set state and the later generator must validate against that state.

Short rule:

- Builder values -> templates and slots.
- Generators -> universal values.
- Generators may have value conditions, but only universal `state`/`tag` validation. Slot logic is forbidden.

## Resolve And Prompt Flow

Prompt Builder V2 separates validation/build order from final prompt text order.

Load flow:

1. Load config and all configured category JSON files.
2. Load all universal generator JSON files.
3. Register category builders and universal generators into the resolver model.
4. Reject or skip universal generators that contain forbidden slot/template logic.

Validation and state flow:

1. Categories run in `resolve_order`.
2. Inside a category, each builder is resolved in builder list order.
3. Each builder first checks builder-level conditions. If they fail, the whole builder returns empty output.
4. State conditions only read state/tags that already exist from state profiles and earlier resolved categories/builders.
5. V2 does not lazy-load later builders to satisfy validation. If a builder or generator value depends on another state, the producing category must appear earlier in `resolve_order`.
6. The builder then inspects all builder value entries.
7. Each value first checks its general value conditions using state/tag validation only.
8. If the value has no template, its normalized value result is the candidate.
9. If the value has a template, the builder resolves the slots referenced by that template on temporary candidate state.
10. Slot definitions may validate against sibling slots because they belong to the builder value.
11. Slots choose one random value from valid generator values or slot-local values. Generator values may validate against state/tag only, never slots.
12. The rendered value is kept only if it is not empty, unless the value explicitly allows an empty result.
13. After all valid candidate values have been built, the builder randomly chooses one candidate.
14. The chosen candidate is already fully evaluated and materialized; do not re-run validation, slots, generators, or template rendering after random choice.
15. Only the chosen builder output writes state/tags to the real category/global state.
16. The next builder then resolves against the updated state.

Final prompt text flow:

1. Categories are appended to the final positive/negative prompt by `order`.
2. `order` controls text placement only.
3. `resolve_order` controls validation traversal and state availability.
4. Categories that produce state used by other categories must resolve earlier than their consumers.
5. Categories that do not produce state consumed by active later categories should move toward the end of `resolve_order`.
6. Do not change `resolve_order` just to make prompt text read better.

Cross-builder validation safety:

- if option A is incompatible with option B, both sides must validate through the same state contract;
- do not rely only on current builder order to make the later option reject the earlier option;
- option A should set/validate a state that blocks B, and option B should set/validate the same state or a reciprocal state that blocks A;
- this is required even when it feels redundant, because it protects future reordering, category run lists, and later inserted builders.

Builder-level validation rule:

- value-level validation remains the preferred and authoritative place to decide whether a value can be selected;
- add builder-level `conditions` only when every meaningful value in that builder shares the same gate or when the whole builder is bound to the same state/tag contract;
- when a gate applies to the whole builder, keep it only on the builder and remove the duplicate value-level conditions;
- builder-level validation is the authoritative place for whole-builder gates;
- value-level validation is still required for conditions that only apply to some values or specific value variants;
- when values are changed later, actively add, update, or remove builder-level conditions so they keep matching the current value set;
- builder-level conditions must use state/tag checks only, not slot checks, because builders still do not own slots.

Current reset examples:

- `builder.clothing.coverage` runs before clothing style and sets `clothing.coverage` to `nude` or `clothed`;
- the `nude` coverage value is gated by `subject.adult=true` and `content.nsfw_allowed=true`;
- the `clothed` coverage value is gated by `content.sfw_allowed=true`;
- `builder.clothing.style` validates `clothing.coverage=clothed` and exports the selected style into `clothing.style`;
- explicit clothing item builders remain as empty scaffolds until the user requests concrete values;
- future missing-clothing authored values that can create visible nudity must live in the relevant `.nsfw` clothing generator and stay gated by `subject.adult=true` plus `content.nsfw_allowed=true`.

## Object Shapes

Builder object reference:

```json
{
  "id": "builder.example.item",
  "description": "Short human note for maintainers.",
  "export_as": "example_slot_name",
  "state_set": {
    "example.exists": true
  },
  "state_export": {
    "example.selected": { "slot": "item", "priority": 0 }
  },
  "tags_add": [],
  "tags_remove": [],
  "conditions": {
    "all": [],
    "any": [],
    "none": []
  },
  "values": [
    {
      "template": "{modifier} {item}",
      "negative": "",
      "state_set": {},
      "state_priority": {},
      "state_export": {
        "example.item": { "slot": "item", "priority": 0 }
      },
      "tags_add": [],
      "tags_remove": [],
      "conditions": {
        "all": [],
        "any": [],
        "none": []
      },
      "slots": {
        "item": {
          "generator": "generator.example.item"
        },
        "modifier": {
          "generator": "generator.example.modifier",
          "conditions": {
            "all": [
              { "slot": "item", "op": "exists" }
            ],
            "any": [],
            "none": []
          }
        }
      }
    }
  ]
}
```

Universal generator reference:

```json
{
  "id": "generator.example.item",
  "values": [
    "",
    {
      "text": "example text",
      "negative": "",
      "state_set": {},
      "tags_add": [],
      "tags_remove": [],
      "conditions": {
        "all": [],
        "any": [],
        "none": []
      }
    }
  ],
  "state_set": {}
}
```

Notes:

- `conditions` on a builder skip the entire builder before value validation. Use them for shared builder-wide gates and do not repeat the same gate on every value.
- The builder example above is template-only, so it intentionally has no builder-level scheduled empty value; its generator slots own the skip chance.
- `export_as` stores the builder result in category-local slot memory so later builders in the same category can validate against it.
- `template` and `slots` belong only on builder value entries. Shared generators and generator values only provide selectable values plus state/tag metadata and state/tag conditions.
- Slot conditions belong only in builder value `slots` definitions. They are forbidden in universal generators and generator values.
- Empty text means skip this piece. Use `{ "text": "", "allow_empty": true }` for empty builder values and `""` for empty universal generator values.
- `negative` contributes to the final negative prompt only if the value is selected.
- `state_set` writes fixed global state after the value/generator is selected.
- Builder-level `state_set`, `state_export`, and tags are applied only after the builder chooses a non-empty result. Pure empty skip values do not trigger builder-level metadata; put meaningful empty-route state on the builder value itself.
- `state_priority` optionally assigns priorities to keys in `state_set`; unspecified keys use priority `0`.
- `state_set` may also use object-form entries such as `"body.example.coverage": { "value": "covered", "priority": 1 }`.
- `state_set` on generator values is preferred for per-value metadata or exceptional facts that cannot be derived from the chosen slot text alone.
- `state_export` maps resolved slot text into global state when the builder is simply recording the selected slot value.
- `state_export` supports legacy shorthand (`"state.key": "slot"` or `"state.key": "{slot}"`) and explicit object syntax (`"state.key": { "slot": "slot" }`).
- Object-form `state_export` skips empty slot text by default; use `{ "slot": "slot", "empty": "null" }` only when a later check needs an explicit `null` write. Explicit null still behaves as missing for `exists`/`missing`, but can be targeted with `equals null`.
- Object-form `state_export` may include `"priority"` for conflict-aware state writes.
- `tags_add` and `tags_remove` are supported by code, but states should be preferred for meaningful validation.

## Conditions

Conditions use:

- `all`: every condition must pass;
- `any`: at least one condition must pass;
- `none`: no condition may pass.

Compound condition blocks may be nested inside other compound blocks when a value needs grouped logic, such as `content.sfw_allowed=true` and either `profile.gender_mode` missing or matching the value gender.

Supported operations:

- `exists`
- `missing`
- `equals`
- `not_equals`
- `in`
- `not_in`

Condition targets:

- `slot`: local slot in the currently selected builder value entry only;
- `state`: global state accumulated from earlier selected values/builders;
- `tag`: tag presence, supported but not preferred for main logic.

Local slot condition:

```json
{ "slot": "item", "op": "exists" }
```

Global state condition:

```json
{ "state": "subject.adult", "op": "equals", "value": true }
```

For every random choice, whether builder value, generator value, or slot-local value, the resolver:

1. validates available values first;
2. randomly chooses from the remaining valid values;
3. resolves any selected `{slot}` structure lazily as needed;
4. treats empty strings as valid skip options.

When a selected builder value's slot condition references a missing slot that the same value entry knows how to generate, the resolver generates that missing slot first, then continues validation.

## Empty Values

Empty generator convention:

- universal generators with no real values should use `values: [""]`;
- resolver fallback for a generator with missing/empty `values` is also `[""]`;
- builder fallback for missing/empty `values` is `{ "text": "" }`;
- all value text is trimmed before use;
- whitespace-only values become empty values;
- rendered templates collapse runs of whitespace to a single space;
- complete empty results are skipped in final prompt assembly.

Empty chance ownership:

- the random source that owns the concrete choice owns the empty chance;
- when a builder value is only a template around one or more generator slots, the generator values own the skip weighting and the builder must not add an extra scheduled empty value for the same route;
- template-only builders whose values all resolve through generator slots therefore do not get builder-level scheduled empty values;
- fixed-string builder values use builder-level scheduled empty values because the builder itself owns those choices;
- mixed builders with fixed-string values and at least one slot-template value may add scheduled empty builder values only when the builder's own real value count reaches the configured empty threshold; the current threshold is 10;
- in mixed builders, the generator-backed template values still keep their own generator-level empty entries, while the builder-level empty entry exists only to keep the builder's own value list skippable once it is large enough;
- do not stack a builder-level scheduled empty value on top of generator-level scheduled empty values just because a template can render empty;
- meaningful empty routes may remain when the empty choice writes required state/tags/negative data or represents a real route decision; when such a route is the intended skip entry for that random source, it counts as that source's empty entry;
- internal no-text route generators whose values all set route state are not skip generators. Do not add plain empty values to them unless a real "no route" option is intended.

When filling `values` arrays for the random source that owns the concrete choices, add one empty option for every ten real random choices, rounded up.

Rules:

- count only real non-empty choices;
- the current default empty cadence base is `10` real choices;
- for 1-10 real choices, add 1 empty string;
- for 11-20 real choices, add 2 empty strings;
- for 21-30 real choices, add 3 empty strings;
- continue the same pattern;
- the empty option always comes directly after each group of ten real choices, in order;
- use `{ "text": "", "allow_empty": true }` for scheduled empty builder values;
- `""` is still allowed in universal generator values when no per-value metadata is needed.
- Meaningful empty values are authored route entries, not disposable filler. Preserve their `state_set`, `tags_add`, `tags_remove`, `negative`, or other metadata. If that meaningful empty route is also the intended skip option for its random source, count it as the empty entry instead of adding another plain empty. Example: the empty `clothing.coverage=clothed` route must keep its conditional state write.
- Subject is an output-required category. `builder.subject` must never contain empty skip values, even though most other random sources are allowed to skip.

Required route exception:

- Required route builders, such as `environment.domain`, may intentionally have no empty option.

Current exception:

- authored clothing prompt generators may keep only `values: [""]` while they are empty scaffolds;
- once real authored clothing values are added, use the normal scheduled empty-value convention unless a concrete prompt-budget reason is documented.
- Environment `generator.environment.room_area` uses a `3x` empty-cadence multiplier: with the current default base of `10`, it schedules one empty value per `30` real choices, rounded up.
- Environment `generator.environment.surface` uses a `4x` empty-cadence multiplier: with the current default base of `10`, it schedules one empty value per `40` real choices, rounded up.
- Do not add extra empty builder values to `builder.environment.location`, `builder.environment.room_area`, or `builder.environment.surface`; the dependency chain already receives its skip weighting from the generator-level empty values.
- If the default empty cadence base changes later, update the concrete Environment exception intervals from the multiplier formula instead of leaving them at fixed `30` or `40` values.

## Descriptions

Every meaningful JSON object with an `id` must include a short `description`.

This includes:

- category entries;
- category files;
- builders;
- universal generators;
- presets.
- state profiles.

Descriptions should explain why the object exists or how it is intended to be used. They are durable design context, not changelog text or action history.

Value objects without `id` do not need descriptions unless they become complex enough that their purpose is not obvious from their fields.
