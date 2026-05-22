# Composition Category

## Purpose

The composition category is reserved for generated framing, camera, perspective, crop, and image-composition prompt fragments.

Before adding or changing any Composition value, builder, generator, state, tag, condition, or validation, check `context/random-prompt-builder-v2-category-relations.md`. Update that central relation map immediately if the change creates or changes any relation with Environment, Action, Pose, Lighting, Style, or Quality.

## Current State

Composition is active with three simple builders:

- `builder.composition.framing` uses `generator.composition.framing` for shot distance, crop, and subject placement.
- `builder.composition.focus_perspective` uses `generator.composition.focus_perspective.general` for solo-subject visual emphasis and `generator.composition.focus_perspective.nsfw` for adult-only sensitive body-region focus.
- `builder.composition.angle_position` uses `generator.composition.angle_position` for simple camera angle and position variation.

The Composition category exports selected values into `composition.framing`, `composition.focus_perspective`, and `composition.angle_position` for debug/state discipline. These states are not currently used for cross-category validation.

Its only validation is the NSFW focus route gate: `subject.adult=true` and `content.nsfw_allowed=true`.

## Authoring Rules

- Keep framing limited to shot distance, crop, and placement. Do not imply clothing, nudity, action, sex, setting, or lighting through framing values.
- Keep focus/perspective limited to what the camera visually emphasizes.
- NSFW focus may name sensitive body regions, including genital focus, but does not create a separate sexual generator while Prompt Builder V2 is aimed at solo-person prompts.
- Keep angle/position broad enough to create visible viewpoint variation without micro camera details.
- Do not add orientation values here; latent resolution owns portrait/landscape orientation.
