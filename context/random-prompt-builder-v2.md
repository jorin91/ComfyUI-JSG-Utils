# Random Prompt Builder V2 Index

`JSGRandomPromptBuilderV2` is a standalone ComfyUI node, separate from the old `JSGRandomPromptBuilder`.

Use this file as the entry point only. Durable details live in focused context files so future work can load only the relevant area.

## Primary References

- `context/random-prompt-builder-v2-architecture.md`: node shape, JSON layout, resolver model, implementation notes.
- `context/random-prompt-builder-v2-baseline-rules.md`: strict global rules for builders, values, generators, SFW/NSFW split, validation order, and category relationships.
- `context/random-prompt-builder-v2-authoring-rules.md`: JSON authoring rules, builder/generator responsibilities, conditions, empty option weighting.
- `context/random-prompt-builder-v2-states.md`: global state index. Read before adding or validating any state.
- `context/random-prompt-builder-v2-category-map.md`: compact category ownership map and prompt-budget guardrails.
- `context/random-prompt-builder-v2-category-relations.md`: central cross-category relation map, allowed dependencies, and chaos-prevention rules. Check this before adding or changing any value, builder, generator, state, tag, condition, validation, category order, or resolve order.
- `context/random-prompt-builder-v2-agreements.md`: persistent user/project agreements and workflow expectations.
- `context/random-prompt-builder-v2-todos.md`: durable future implementation TODOs and old-builder features worth redesigning for V2.

## Prompt Category References

Each prompt category has its own file under `context/random-prompt-builder-v2-categories/`.

- `subject.md`
- `ethnicity.md`
- `body-build.md`
- `clothing.md`
- `body-detail.md`
- `action.md`
- `pose.md`
- `environment.md`
- `composition.md`
- `lighting.md`
- `style.md`
- `quality.md`

## Current Prompt Assembly Order

1. preset/model positive fragments
2. `tag_lora` at the front of the positive prompt
3. generated or overridden category positive fragments
4. preset/model negative fragments
5. negative fragments emitted by selected generated values

`tag_lora` is positive-only and intentionally simple. It exists to trigger LoRA tags.

State profile application happens before category generation and does not emit prompt text. The default profile is `Mixed Female`; profiles set SFW/NSFW allow state, profile mode state, and optional fallback gender state so manual Subject overrides still get usable filtering state.

## Category Order

1. Subject
2. Ethnicity
3. Body Build
4. Body Detail
5. Clothing
6. Action
7. Pose
8. Environment
9. Composition
10. Lighting
11. Style
12. Quality

## Current Validation Order Notes

`resolve_order` may differ from prompt output order.

Current important validation differences:

- Clothing resolves before Body Build and Body Detail.
- Environment resolves immediately after Subject by default, while its prompt text still outputs after Pose.
- Clothing resolves after Environment and before Action, so clothing theme and clothing-action states exist before dependent Action values validate.
- Action appears before Pose. Random Action and random Pose are mutually exclusive through internal `activity.route`: random Action validates on `activity.route=action`, random Pose validates on `activity.route=pose`, and manual override text bypasses this route while random disabled plus empty override intentionally emits nothing.
- Body Detail, Body Build, Ethnicity, Composition, Lighting, Style, and Quality currently resolve after the dependency-producing chain because no active later category depends on their generated state.
