# Body Build Category

## Purpose

The body build category is reserved for general whole-body traits: height, weight, overall proportions, broad muscularity, whole-body visible tone, skin tension/softness, and broad non-region-specific tanning.

Before adding or changing any Body Build value, builder, generator, state, tag, condition, or validation, check `context/random-prompt-builder-v2-category-relations.md`. Update that central relation map immediately if the change creates or changes any relation with Subject/Content, Clothing, Body Detail, Action, Pose, or Style.

Use Body Build only when the value affects the whole body or the subject's overall build/presentation. Region-specific body structure, body parts, subparts, regional surface detail, regional bone definition, and regional tanning belong in Body Detail.

## Current State

Implemented category file:

- `data/random_prompt_builder_v2/categories/body_build.json`

Implemented shared generator file:

- `data/random_prompt_builder_v2/shared_generators/body_build.json`

Current builders:

- `builder.body_build.general.physical_trait`: selects one optional whole-body trait route from weight/mass, muscularity, visible toning/definition, or general bone visibility.
- `builder.body_build.general.proportions`: selects one optional whole-body proportions/silhouette phrase.

The physical trait builder intentionally keeps weight, muscularity, toning, and bone visibility as sibling builder values so only one of those aspects can appear in a generated prompt. This prevents long prompts that stack several broad body-build directions that can steer the model into each other.

The proportions builder may coexist with one physical trait because it describes the whole-body silhouette rather than another mass/muscle/definition route.

## Organization Rule

Body Build should stay broad and whole-body focused.

Allowed grouping:

1. overall height/stature;
2. overall weight/mass;
3. overall proportions/shape;
4. overall muscularity;
5. whole-body surface tone or skin tension;
6. broad non-region-specific tanning.

Current prompt-budget rule:

- Keep the active general physical trait builder to one emitted route across weight, muscularity, toning, and bone visibility.
- Keep proportions as the only separate active Body Build builder for now.
- Height, broad tanning, and skin-tension-only builders are not active; add them later only when explicitly requested and when they do not make Body Build too dense.

Boundary rule:

- If a value names a body region, body part, subpart, regional tan line, regional bone, or local surface detail, it belongs in Body Detail.
- Do not add breast, abdomen, pelvis, buttock, areola, nipple, vulva, anus, limb, rib, collarbone, or navel builders here.
- If a future whole-body value later needs regional exceptions, keep the whole-body builder here and put regional refinements in Body Detail.

## Refill Rules

- Add only a few values at a time from explicit user-requested outcomes.
- Prefer broad traits that can combine cleanly with clothing, pose, and style.
- Avoid adding many body dimensions at once.
- Prefer adding another value to the existing physical trait route over adding another active builder when the new wording is another whole-body mass, muscle, definition, or bone-visibility direction.
- Adult-gated body build values should validate through `subject.adult` only when the concrete value needs it.

## Coverage / Exposed State Rules

Body Build should rarely need coverage states because it is whole-body and not region-specific.

Do not create broad all-body visibility state packages as a default. Add coverage/exposed states only when concrete Body Detail, clothing, or pose builders actually need them.
