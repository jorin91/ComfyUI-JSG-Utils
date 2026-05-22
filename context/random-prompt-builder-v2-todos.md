# Random Prompt Builder V2 TODOs

This file tracks durable future implementation work for `JSGRandomPromptBuilderV2`.

It is not a changelog or session diary. Keep only TODOs that remain meaningful beyond the current work session.

## Purpose

Random Prompt Builder V2 should remain the main path for future prompt generation because its category, builder, template, slot, generator, and state model is better suited to controlled prompt grammar than the old builder.

The old `JSGRandomPromptBuilder` still contains several useful operational features that should be considered for V2 once the V2 data model stabilizes. These features should not be copied blindly. They should be redesigned in V2 terms so they support the cleaner builder/value/generator boundary.

## Structured Debug Path

Goal:

- Extend the implemented `Debug State` output into a fuller resolver trace when needed.

Current behavior:

- V2 returns a third `Debug State` string output with final global state, state priorities, and active tags.

Future desired behavior:

- Include selected preset and preset positive/negative fragments.
- Include each category in resolve order.
- For each category, include whether it used override text or random generation.
- For generated categories, include each builder/generator that emitted text, negative text, tags, or state.
- Include skipped builders/values when a condition failed only if this can be done without making debug output overwhelming.
- Include slot results for template-based values, especially when a slot is empty and causes an otherwise visible template to collapse.

## Debug Order Visibility

Goal:

- Add debug visibility for the already implemented split between category resolve order and final prompt output order.

Why this matters:

- V2 now supports config `resolve_order` for validation/state resolution and keeps config `order` for final prompt order.
- Debug output should make both visible so confusing category interactions can be diagnosed.

Examples:

- Body/clothing coverage facts may resolve in a different order than they appear in the prompt.
- A scene-level preset may need to set conditions before categories resolve while leaving visible prompt text near style or quality.

Desired V2 behavior:

- Debug output should list each category's `resolve_order` and `order`.
- Debug output should show prompt assembly order separately from state resolution order.

Design notes:

- `resolve_order` controls when state/tags are produced and consumed.
- `order` controls where emitted positive/negative text appears in the final prompt.

## Logic-Only Values

Goal:

- Add an explicit way for a selected V2 value or generator to set state/tags/negative data without emitting positive prompt text.

Why this matters:

- The old builder supports `includeInPrompt=false`, allowing logic-only parts to affect later generation without showing text.
- V2 can currently produce empty text with `state_set`, but the intent is not explicit enough.
- Logic-only behavior will become important for visibility, coverage, category coordination, preset state, and conflict management.

Desired V2 behavior:

- Add a clear JSON convention such as `include_in_prompt: false` or `emit_text: false` on value entries.
- The selected value should still be allowed to:
  - set state;
  - add or remove tags;
  - emit negative prompt text if explicitly allowed;
  - affect later conditions.
- Template values should be able to resolve slots and export state without adding their rendered text to the positive prompt when marked logic-only.

Design notes:

- Logic-only values should still appear in debug output.
- The feature must preserve the builder/value boundary: builders remain containers; value entries own this behavior.
- The default should remain visible prompt emission when text exists.

## State Priority Debug Visibility

Goal:

- Add debug visibility for implemented state priority and skipped overwrites.

Why this matters:

- V2 now tracks priority for state writes.
- Default priority is `0`.
- Only a strictly higher priority overwrites an existing state key.
- Equal priority does not overwrite.

Desired V2 behavior:

- Debug output should show the accepted write priority for final state values.
- Debug output should show when a same/lower priority write was ignored.

Design notes:

- Avoid adding source/locked/merge strategies until a concrete conflict needs more than priority.

## Trigger / Preset-State Mechanism

Meaning:

- A trigger or preset-state mechanism is a reusable named state package that a value, category, or preset can apply without repeating a long list of state writes every time.
- Initial state profiles are now implemented for V2 as `data/random_prompt_builder_v2/state_profiles/*.json`; reusable value-applied state packages remain future work.

Old builder reference:

- The old builder has `state.json` trigger definitions.
- A value can list triggers, and each trigger applies grouped tag/kv changes before the value's own changes.
- Example concept: `all_covered` can set many body coverage keys to `covered` in one reusable action.

V2 interpretation:

- In V2, this should not become a loose legacy tag/kv system.
- It should be redesigned as named reusable state/tags fragments that integrate with V2 `state_set`, `tags_add`, and `tags_remove`.

Why this matters:

- Some future systems may need to set many related state values together.
- Repeating the same large `state_set` object across many values would make JSON noisy and error-prone.
- Presets may eventually need to seed state as well as positive/negative prompt fragments. Initial state profile seeding already exists separately from presets.

Possible V2 shapes:

- Shared state package:

```json
{
  "id": "generator.state.coverage.all_covered",
  "state_set": {
    "body.upper_torso.coverage": "covered",
    "body.lower_torso.coverage": "covered"
  }
}
```

- Value applying a state package:

```json
{
  "text": "",
  "apply_state": ["generator.state.coverage.all_covered"]
}
```

- Preset seeding state:

```json
{
  "positive": ["score_9"],
  "negative": ["low quality"],
  "state_set": {
    "model.family": "pony"
  }
}
```

Design notes:

- Use this only when repeated state packages become real, not as an early abstraction.
- Any state keys applied through packages must still be documented in `random-prompt-builder-v2-states.md`.
- Debug output should show applied trigger/package names and expanded state effects.
- The name should probably avoid old-builder wording if it causes confusion. `state_package`, `state_preset`, or `apply_state` may fit V2 better than `trigger`.

TODO before implementation:

- Decide the final V2 naming and JSON shape before adding reusable value-applied packages.
- Prefer V2-native wording over copying the old builder's `trigger` name directly.
- Current preferred direction:
  - keep initial startup state in `state_profiles`;
  - define reusable packages as `state_package` or `state_preset`;
  - apply them from values with a field such as `apply_state`;
  - allow presets to seed initial state through their own `state_set` or package reference.
- Document the chosen naming in the authoring rules before adding real vocabulary that depends on it.
