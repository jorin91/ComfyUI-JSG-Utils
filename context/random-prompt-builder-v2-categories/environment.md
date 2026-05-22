# Environment Category

## Purpose

The environment category creates person-focused scene context and stores useful environment state for later filtering.

Before adding or changing any Environment value, builder, generator, state, tag, condition, or validation, check `context/random-prompt-builder-v2-category-relations.md`. Update that central relation map immediately if the change creates or changes any relation with Action, Pose, Lighting, Composition, Clothing, or Environment's own location/room/surface chain.

Environment should model dependency and compatibility through state and generator value validation, not through premature indoor/outdoor generator splits.

## Current State

Implemented category file:

- `data/random_prompt_builder_v2/categories/environment.json`

Implemented universal generator file:

- `data/random_prompt_builder_v2/shared_generators/environment.json`

Detailed location, room/area, and surface relationship rules are maintained centrally in:

- `context/random-prompt-builder-v2-category-relations.md`

Current builder scaffold:

1. domain;
2. location;
3. room or area;
4. surface;
5. environment condition;
6. season;
7. weather;
8. time;
9. social context;
10. props.

Currently filled:

- `builder.environment.domain`: required `indoors` / `outdoors`, setting `environment.domain`.
- `builder.environment.location`: optional location values, exported to `environment.location`; real location values set broad accepted `environment.clothing.theme.*` states for Clothing, and the blank/no-location fallback sets all Clothing themes as accepted.
- `builder.environment.room_area`: optional room/area values, exported to `environment.room_area`, validating against `environment.location` and `environment.domain`.
- `builder.environment.surface`: optional compatible surface phrase, exporting `environment.surface` and `environment.surface_relation`.
- `builder.environment.season`: optional outdoor-only spring/summer/autumn/winter, exported to `environment.season`.
- `builder.environment.weather`: optional outdoor-only weather, exported to `environment.weather`.
- `builder.environment.time`: optional daypart/time, exported to `environment.time`.

Still empty:

- condition;
- social context;
- props.

The current Environment vocabulary is intentionally small and broad. Add more values only from explicit user-requested scene outcomes.

Current location families:

- home/private home spaces;
- school and university spaces;
- library spaces;
- public and private swimming pool spaces;
- clothing store spaces;
- outdoor nature spaces.

Location-level Clothing themes:

- Environment owns broad accepted Clothing themes at the location level only.
- Current theme states are `environment.clothing.theme.underwear_swimwear`, `.sport`, `.sleep`, `.work`, `.casual`, `.seasonal`, `.party`, and `.nude`.
- Themes are soft setting direction. They should steer what the generator is likely to show without becoming exact social dress-code validation.
- Do not set Clothing themes from room/area, surface, weather, time, condition, social context, or props unless the Environment-to-Clothing design is explicitly revised.
- Every real location should set `environment.clothing.theme.nude=true`; the actual nude route remains adult/NSFW gated by Clothing.
- The blank/no-location fallback should set every Clothing theme to `true`, so optional location never blocks Clothing by absence of setting context.

## Generator Organization

Do not split environment generators into indoor/outdoor versions by default.

Current universal generator scaffolds are intentionally unified:

- `generator.environment.location`
- `generator.environment.room_area`
- `generator.environment.surface`
- `generator.environment.condition`
- `generator.environment.season`
- `generator.environment.weather`
- `generator.environment.time`
- `generator.environment.social_context`
- `generator.environment.props`

Split into multiple builders or generators only when concrete vocabulary makes it genuinely useful for organization or validation.

## Refill Rules

- Add only a few environment values at a time.
- Keep values person-focused.
- Keep generator values atomic. Do not use combined alternatives such as `x or y`; split them into separate values and update any state validation lists that reference them.
- Reuse and cross-link existing locations, room/areas, and surfaces whenever a new value logically fits existing mappings. Add specificity only when visual meaning changes enough to justify a separate value.
- Even when a user provides a structured `location -> room_area -> surface` list, evaluate each part independently and actively search for additional logical links.
- If an existing value is conceptually right but the wording is slightly wrong for a new context, create a new variant instead of forcing awkward reuse.
- Every meaningful selected environment value must write or export state.
- Every real location value should set the accepted Clothing theme states for that broad location.
- Blank/no-location values should remain permissive and set all Clothing theme states.
- Use Environment to say where the subject is, not how the camera frames the subject or how the image is lit.
- Prefer builder `state_export` when a selected slot simply stores its text into state.
- Use generator value `state_set` only for exceptional metadata that differs per value.
- Add environment state documentation when a concrete value sets or validates that state.

## Validation Expectations

When environment values return, use state and generator value validation.

Expected validation flow:

- `domain`: may set `environment.domain`.
- `location`: values set `environment.location`; they usually do not validate against `environment.domain` because one location, such as a home, can contain both indoor and outdoor areas. Truly outdoor-only broad locations may validate against `environment.domain=outdoor` when no indoor variant is meaningful; current examples are forest, beach, lake, river, and countryside locations.
- `room_area`: values must validate against `environment.domain` and against either a compatible `environment.location` or missing `environment.location`.
- `surface`: values must validate against `environment.room_area` when the surface belongs to a room/area.
- `surface_relation`: values are simple relation/prefix words. The builder relation slot validates that the selected surface slot exists; the generator itself must not contain slot logic.
- Surface phrase assembly (`{relation} {surface}`) belongs on the `builder.environment.surface` builder value, not on universal generators.
- `condition`: keep sparse; values validate only where a condition is meaningfully constrained.
- `season`: optional context that may set `environment.season`.
- `season`: currently builder-gated to `environment.domain=outdoor`; do not emit seasons for indoor settings unless a future indoor-visible weather/window context is explicitly designed.
- `weather`: currently builder-gated to `environment.domain=outdoor`; values also validate their own season compatibility where needed.
- `time`, `social_context`, and `props`: validate at value level only when concrete compatibility requires it.

Builder-level validation is usually not useful for environment beyond cases where every meaningful value in the whole builder shares the same gate.

Strict dependency chain:

- `environment.location` is the selected place, such as home/thuis or nature. Do not use it as the domain gate for mixed-domain locations.
- `environment.room_area` validates to `environment.domain` plus an `any` location check: compatible `environment.location` or missing `environment.location`.
- `environment.surface` validates to `environment.room_area`.
- Do not add a room/area unless it can answer "which location/domain can this exist in?"
- Do not add a surface unless it can answer "which room/area can this exist in?"
- Avoid relying on prompt wording alone. Compatibility must be enforced through state conditions.

## Scope Boundaries

`room` and `area` are intentionally combined as `environment.room_area`. They often serve the same prompt role and should not always stack.

`surface` describes where or against what the subject physically is, such as a floor, bed, sofa, grass, pavement, or similar person-contact context.

`props`, `social_context`, and `condition` should remain sparse. Add values only where they materially improve the person-focused scene or unlock a specific kind of setting.

`time` may guide scene plausibility, but detailed light direction, intensity, and mood belong in the Lighting category.

Do not add broad decorative backdrop, camera, framing, lighting, or visual style values here. Those belong to Composition, Lighting, or Style unless they are genuinely environment context.

Current validation lesson:

- Weather and season are outdoor visual environment context in the simple baseline.
- Do not combine `indoors` with season or weather terms; it confuses the model by adding outdoor scene context to an indoor setting.
- Future indoor-visible weather or season context must be introduced as a separate explicit concept, such as a window/outside-visible setting, with its own validation.

Environment dependency-chain note:

- The core chain `location -> room_area -> surface` must not stack builder-level empty skip values on top of generator-level scheduled empty values. Skip weighting for these three layers lives in their generators.
- This follows the global empty chance ownership rule: generator-backed template builders do not add a second builder-level skip chance for the same generated slot.
- If `location` skips, `room_area` may still validate against the selected domain through the missing-location fallback; if `room_area` skips, `surface` cannot validate.
- Complete location/room/surface output is still gated by validation, but `room_area` and `surface` intentionally use lower generator skip frequency than the global default so compatible room/surface context appears more often.
- Global default scheduled empty cadence is one empty per 10 real choices, rounded up. `generator.environment.location` uses that default.
- `generator.environment.room_area` uses a `3x` multiplier against the default cadence, so with the current base of 10 it schedules one empty per 30 real choices, rounded up.
- `generator.environment.surface` uses a `4x` multiplier against the default cadence, so with the current base of 10 it schedules one empty per 40 real choices, rounded up.
- If the default base cadence changes, recalculate the concrete room/area and surface exception intervals from these multipliers.

Location planning note:

- First concrete location is home/house/thuis, emitted as `at home`.
- A home location can support both indoor and outdoor room/area values.
- Room/area values for home must validate on `environment.location=at home` or missing `environment.location`, and the correct `environment.domain`.
- Surface values for home must validate on the selected `environment.room_area`.
- Outdoor nature is split into five concrete locations: `in a forest`, `at a beach`, `by a lake`, `by a river`, and `in the countryside`. Each validates against `environment.domain=outdoor` and owns its own compatible room/area values and surfaces.
- Keep the central relation map updated when adding or renaming location, room/area, or surface values.

Validation feedback lesson:

- Do not make `environment.location` validate against `environment.domain` just because the current location has indoor/outdoor implications. The domain/indoor-outdoor compatibility belongs on `environment.room_area`, because a single location can contain both indoor and outdoor areas.
- Outdoor-only broad locations may be location-gated by `environment.domain=outdoor` when the location itself has no meaningful indoor form and must still steer the prompt if `room_area` skips.
- Do not make the surface relation/prefix generator validate specific surface compatibility or surface existence. Surface compatibility belongs on the selected `surface`; surface-exists validation belongs on the builder's `relation` slot definition.
- Do not put `template`, `slots`, or `slot` conditions on universal generators or generator values. Template and slot logic belongs at the builder value level only.

## Action/Pose Validation Boundary

Action and Pose may validate against Environment only for hard setting requirements:

- `environment.domain`
- `environment.location`
- `environment.room_area`
- `environment.surface`

Soft plausibility is not enough. Do not validate a yoga action or pose against home/gym/outdoor merely because those are common settings. Do validate harder setting concepts such as cycling, swimming, showering, mirror use, bed-making, or room-specific actions/poses against the broadest accurate Environment state.

Validation follows physical possibility and object specificity, not social acceptability. General washing and grooming may stay ungated because they are not necessarily shower/bath/sink actions. `urinating` stays Environment-ungated because it can technically happen anywhere. `making the bed`, mirror actions, showering, and bathing validate because they name a fixed object/facility that only exists in specific room/area contexts.

Use `environment.surface` only when the selected surface/support itself is the hard requirement and room/area is not accurate enough. Do not validate Action or Pose values against `environment.time`, `environment.season`, or `environment.weather` unless this relation is redesigned and documented first.
