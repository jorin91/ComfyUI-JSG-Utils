# Random Prompt Builder V2 Agreements

## Context Organization

Context files must stay organized by topic. Avoid dumping all Random Prompt Builder V2 details into one large file.

Use:

- `random-prompt-builder-v2.md` only as an index;
- `random-prompt-builder-v2-architecture.md` for system shape and implementation behavior;
- `random-prompt-builder-v2-authoring-rules.md` for reusable JSON/modeling rules;
- `random-prompt-builder-v2-states.md` for the state registry;
- `random-prompt-builder-v2-category-relations.md` for the central cross-category relationship map that must be checked before adding or changing values, builders, generators, states, tags, or validation;
- `random-prompt-builder-v2-categories/*.md` for category-specific prompt knowledge.

Prompt category context belongs in the matching category file. When a category grows large, split further only if there is a clear subsystem boundary.

## Durable Context Standard

Context files are not diaries, logs, or chronological reports.

Keep only durable project knowledge:

- current architecture and behavior;
- decisions and constraints;
- conventions;
- state contracts;
- category-specific modeling rules;
- TODOs that remain true beyond a single work session.

Remove or rewrite outdated context instead of stacking new notes underneath old ones.

## Relationship Map Maintenance

`context/random-prompt-builder-v2-category-relations.md` is the mandatory central relation map.

Before adding or changing any value, builder, generator, state, tag, condition, validation, category order, or resolve order, check that file as a reminder of every validation relationship that may need to be applied.

When a new relationship is created or an existing one changes, update the relation map in the same work session. Category-specific files may add local detail, but they do not replace the central relation map.

## Vocabulary Policy

Prompt vocabulary should grow category by category from explicit user direction.

Do not bulk-migrate old random prompt text into V2. The old builder can be used for ideas only.

When vocabulary is not provided yet, keep generators as intentional empty placeholders.
