# Pose Category

## Purpose

The pose category describes static body posture, body shape/form, stance, and expression.

Pose is about how the subject's body or expression is held at an instant. It should stay as close as possible to static posture/form/expression and should not take over activity, movement, object interaction, or scene context.

Before adding or changing any Pose value, builder, generator, state, tag, condition, or validation, check `context/random-prompt-builder-v2-category-relations.md`. Update that central relation map immediately if the change creates or changes any relation with Action, Environment, Clothing, Subject/Content, or Body state.

## Current Reset State

Implemented category file:

- `data/random_prompt_builder_v2/categories/pose.json`

Implemented universal generator file:

- `data/random_prompt_builder_v2/shared_generators/pose.json`

Current builder:

- `builder.pose`: a single route picker for the subject's one Pose concept.

Current route values inside `builder.pose`:

- general pose route through `generator.pose.general`;
- sport/gymnastics/fitness-derived pose route through `generator.pose.sport.gymnastics_fitness`;
- yoga-derived pose route through `generator.pose.sport.yoga`;
- dance-derived pose route through `generator.pose.sport.dance`;
- adult/NSFW-gated pose route through `generator.pose.nsfw`;
- adult/sexual pose route through `generator.pose.sexual`.

Pose route families are mutually exclusive values, not separate builders. The builder chooses one valid route value, and that route chooses one concrete generator value. General and sport-derived route values export through `pose.general`; the NSFW route exports through `pose.nsfw`; the sexual route exports through `pose.sexual`.

`builder.pose` validates at builder level against internal state `activity.route=pose`. Random Pose output is mutually exclusive with random Action output. Manual Pose override text bypasses route validation.

## Refill Rules

- Add only a few pose values at a time.
- Keep route families as values inside `builder.pose`; do not add separate Pose builders for general, sport, NSFW, or sexual pose families.
- Use the NSFW route value for adult-only NSFW, visibility-oriented, suggestive, intimate, or static sensitive-area placement poses when the wording is gated but not truly sexual.
- Use the sexual route value only for explicitly sexual acts or sex-contextual poses. Do not put merely intimate, revealing, or sensitive touch values there by default.
- Provocative camera-facing body-part display can stay in the NSFW route when it is static presentation without a sexual act and without clothing movement. Do not validate those values against Clothing unless the wording explicitly requires a garment.
- Static sexual derivatives such as labia held open, buttocks held spread for anal visibility, hand-near-mouth oral-sex gesture, or open-mouth oral-ejaculation expression belong in the sexual route.
- NSFW and sexual route values are value-gated with `subject.adult=true` and `content.nsfw_allowed=true`.
- Future adult-only NSFW/sexual pose values should keep the same allow-state plus selected-adult-state validation unless a narrower documented gate is added.
- Add extra visible-body validation only when a concrete value requires a specific exposed/covered body state.
- Do not create extra pose builders preemptively.
- Keep every pose value atomic. Do not use combined alternatives such as `underwear or swimwear`, slash pairs, or other "A/B" wording. Split them into separate pose values so the image model receives one clear body/hand placement instruction.
- User-provided pose labels are semantic input, not literal prompt text. Convert them into clear standalone English pose phrases; the selected text must not rely on the generator name to make sense.
- Alternative pose wording may be kept as a separate value when the image model can interpret it differently, when it is more standalone/general than an existing context-specific value, or when it changes steering strength.
- Keep wording in Pose only when it primarily describes static body posture/form/expression. If the wording starts steering support, environment, object interaction, movement, or activity context, route it to the correct category instead.
- Example: `wall squat` is a pose term because it names a static posture form; `squatting against a wall` is Action wording because it steers the subject interacting with wall support and gives extra scene context.
- Active verbs such as touching, caressing, adjusting, washing, grabbing, holding an object, or leaning against a support belong in Action. Pose may keep the derived static body placement, such as `hands on the face`, `one hand on the cheek`, or `wall squat`.
- When a Pose generator grows beyond roughly 25 non-empty options, split it into smaller semantic generators and let the builder contain multiple values pointing to those sets.
- When sibling Pose builder values target the same result route but are separated by content class, keep their readable order `sfw -> nsfw -> sexual`. This is an authoring convention only; runtime still validates all candidate values first and randomly selects from the valid set.

## Current Vocabulary Notes

General pose values include standing, relaxed/casual/neutral standing, one-knee-raised variants, legs-together/apart and wide-stance variants, forward-bent and bent-over variants, static leaning variants, seated variants, knees-up and legs-up variants, lying prone/supine/side variants, crouching and squatting variants, wall squat, side-profile squat, hands on hips/knees, hands behind back, static hand placement on face/neck/abdomen/side, hands in hair, arm-stretched variants, kneeling, sitting-on-heels variants, one-knee kneeling variants, and hands-and-knees/all-fours poses.

Derived static pose generators add recognisable held forms from Action vocab without moving the action itself into Pose. Current derived groups include gymnastics/fitness forms such as handstand, bridge, split stretch, plank, side plank, lunge, push-up position, and landing poses; yoga forms such as lotus, tree, cobra, downward dog, upward dog, child, warrior, triangle, camel, boat, crow, headstand, shoulder stand, twist, fold, meditation, and palms-together poses; and dance forms such as ballet arabesque/plie/releve/toe-point, mid-dance, dramatic dance, contemporary floor/body-extension, idol, tango leg-hook, ballroom-frame, salsa-hip, and expressive dance poses.

NSFW pose values currently include adult-gated provocative/suggestive posing, seductive gaze, legs-spread/thigh-gap/hip-forward/back-arch variants, hands-between-legs variants, provocative camera-facing body-part display for breasts, vulva, penis, buttocks, and anus, and static sensitive-area hand-placement variants. These are intentionally NSFW rather than sexual when they describe sensitive/intimate or suggestive presentation instead of an explicit sex act.

Sexual pose values currently include static explicit sexual/sex-contextual derivatives: labia held open with fingers, buttocks held spread to reveal the anus, a hand-near-mouth oral-sex gesture, and an open-mouth tongue-out oral-ejaculation expression.

Current clothing-dependent pose values:

- None active. Clothing adjustment is Action because it is a hand action and depends on clothing existence.

Do not use `clothing.coverage=clothed` as proof that pose-compatible clothing exists. If a future Pose truly requires a garment or exposed/covered body state, introduce a concrete Clothing-to-Pose state only then.

Current body-placement pose values do not validate against clothing when the pose can still make sense over clothing or without clothing. In those cases the value describes static body/hand placement, not a required visible body state.

## Future Validation

Some poses are natural add-ons to an action, but the current random system intentionally avoids stacking random Action and random Pose.

Random Action/Pose behavior:

- if Action and Pose are both random-enabled, the node randomly chooses `activity.route=action` or `activity.route=pose`;
- `builder.pose` requires `activity.route=pose`;
- disabled-random Pose with override text is emitted directly and bypasses route validation;
- disabled-random Pose with an empty override intentionally emits nothing;
- manual Pose does not remove random Action from the route choice. If Action is still random-enabled, random Action can still run beside the manual Pose text.

Action often gives the model more context than Pose because it can carry movement, intent, support/object interaction, and scene behavior. Pose should not duplicate that richer context unless it is a pure static form/expression value.

Future pose logic that conflicts with clothing or body details should use explicit covered/exposed or availability states introduced only when concrete builders need them.

Do not reintroduce old partial Action-to-Pose compatibility keys unless the Action/Pose route model is intentionally redesigned.

Pose/clothing compatibility is value-specific. Validate poses that require actual clothing, underwear, swimwear, nudity, or a covered/exposed body state. Do not validate poses against clothing merely because hands are placed on a body area; placement can be over clothing as well as without clothing unless the wording explicitly requires visible skin or a specific garment.

Prefer the broadest accurate clothing-to-pose state first if a future static Pose actually needs clothing. No Clothing-to-Pose states are active right now.

Do not validate Pose against generic source-only clothing existence keys. If Clothing creates a state for Pose, the key must include the target namespace: `clothing.pose.*`.

Pose adult/NSFW compatibility must use `subject.adult=true` plus `content.nsfw_allowed=true` for NSFW and sexual route values. The sexual route remains reserved for explicitly sexual acts or sex-contextual poses, not merely sensitive or intimate presentation.

## Environment Validation

Pose values may validate against:

- `environment.domain`
- `environment.location`
- `environment.room_area`
- `environment.surface`

Use this only for hard setting requirements. Do not validate portable poses just because a setting is plausible or common.

Examples:

- Yoga-like or static stretching poses should not be location-gated by default because they can happen in many settings.
- A future pose that explicitly depends on pool/water, a changing room, a classroom, or another hard setting should validate against the broadest accurate Environment state.
- Use `environment.surface` only when the pose physically requires a specific selected object or support. Generic support/interacting wording usually belongs in Action instead of Pose.

Do not validate pose values against time, season, or weather unless the relation is redesigned and documented first.
