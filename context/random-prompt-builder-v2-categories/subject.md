# Subject Category

## Purpose

The subject category defines the generated subject identity and the core subject states used by later categories.

Before adding or changing any Subject value, builder, generator, state, tag, condition, or validation, check `context/random-prompt-builder-v2-category-relations.md`. Update that central relation map immediately if the change creates or changes any relation with Clothing, Body, Action, Pose, or content gating.

V2 currently supports one generated subject. Manual category override may contain arbitrary text, but generator logic is designed around one subject.

## Adult Gating

Subject age values should include explicit age-range prompt text because the user is training a LoRA around these distinctions.

State profile content mode affects subject validity:

- non-adult generated subjects require `content.sfw_allowed=true`;
- NSFW-only profiles set `content.sfw_allowed=false`, so they select adult generated subjects only;
- SFW and Mixed profiles set `content.sfw_allowed=true`, so non-adult generated subjects may remain available;
- gender-specific profiles seed `subject.gender` as a low-priority fallback for manual overrides;
- generated Subject gender values must validate against `profile.gender_mode`, so `Female` profiles can only generate female Subject values and `Male` profiles can only generate male Subject values.

Random Subject must always emit a concrete subject phrase. Do not add empty skip values to `builder.subject`.

Subject values should set `subject.adult`, `subject.age_phase`, and the debug/readability `subject.age_range`:

```json
{
  "text": "young adult woman (age 18-23)",
  "state_set": {
    "subject.adult": true,
    "subject.age_phase": "young_adult",
    "subject.age_range": "young adult woman (age 18-23)"
  }
}
```

Non-adult subject values:

```json
{
  "text": "late teen girl (age 16-17)",
  "state_set": {
    "subject.adult": false,
    "subject.age_phase": "late_teen",
    "subject.age_range": "late teen girl (age 16-17)"
  }
}
```

Do not add `subject.is_minor` or another overlapping age-group state. `subject.age_phase` is the durable validation state for broad phase checks that should not depend on gendered age-range text.

`subject.age_phase` is intentionally not seeded by state profiles. Manual Subject overrides do not infer it, and missing `subject.age_phase` means age-phase-dependent Body Detail values should remain available unless another explicit gate blocks them.

`subject.age_range` is intentionally kept as a debug/readability state. It mirrors the selected subject age phrase for debug output only and should not be used for validation.

Builder values that require adult subjects validate with state:

```json
{
  "conditions": {
    "all": [
      { "state": "subject.adult", "op": "equals", "value": true }
    ]
  }
}
```

If all meaningful values in a builder require adult subjects, keep this validation on the builder instead of repeating it on every value. Value-level adult validation is only needed when some values in the same builder are adult-only and others are not.

## Current States

- `subject.adult`
- `subject.age_phase`
- `subject.gender`
- `content.sfw_allowed`
- `profile.content_mode`
- `profile.gender_mode`

See `context/random-prompt-builder-v2-states.md` for the authoritative state index.
