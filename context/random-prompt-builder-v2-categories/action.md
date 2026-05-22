# Action Category

## Purpose

The action category describes what the subject is doing and keeps broad action purposes separated for future validation.

Action is the primary carrier for movement, intent, object/support interaction, and scene context. It may include values that look posture-like when the wording adds contextual behavior, such as interacting with a wall, mirror, bed, shower, clothing, equipment, or another object.

Before adding or changing any Action value, builder, generator, state, tag, condition, or validation, check `context/random-prompt-builder-v2-category-relations.md`. Update that central relation map immediately if the change creates or changes any relation with Environment, Clothing, Pose, Subject/Content, or Body state.

## Current Reset State

Implemented category file:

- `data/random_prompt_builder_v2/categories/action.json`

Implemented universal generator file:

- `data/random_prompt_builder_v2/shared_generators/action.json`

Current builder:

- `builder.action`: a single route picker for the subject's one Action concept.

Current route values inside `builder.action`:

- general movement, rest, grooming, mirror, home, and everyday actions through `generator.action.general`;
- sport, gymnastics, yoga, fitness, and dance actions through `generator.action.sport`;
- adult/NSFW-gated private, revealing, nudity-directed, or suggestive actions through `generator.action.nsfw`;
- standalone sexual actions through `generator.action.sexual`;
- modular penetration action;
- modular stimulation action.

Action route families are mutually exclusive values, not separate builders. The builder chooses one valid route value, and that route may then choose one concrete generator value or assemble one modular phrase. Empty/no-action output comes from generator-level empty entries inside those routes, not from an extra builder-level empty value. Do not reintroduce `action.selected`; it was an internal lock-state workaround and is no longer part of the Action model.

## Refill Rules

- Add only a few action values at a time.
- Put general everyday action vocabulary in `generator.action.general`.
- Put sport/exercise vocabulary in `generator.action.sport`.
- Put future work/profession vocabulary in a profession route value inside `builder.action`, backed by a future profession generator.
- Put adult-only private, revealing, nudity-directed, or suggestive vocabulary in `generator.action.nsfw` when the wording is gated but not truly sexual.
- Put standalone sexual action vocabulary in `generator.action.sexual` only when it is explicitly sexual or sex-contextual and not large enough for a modular route.
- Clothing-displacement exposure actions belong in the NSFW route when the action is about intentionally moving clothing to reveal a body part to the camera. They must validate against the broadest matching Clothing-to-Action state, such as `clothing.action.upper_body.exist` for breasts and `clothing.action.lower_body.exist` for buttocks, vulva, penis, or anus.
- Self-stimulation, penetration, labia spreading, buttocks spreading for anal visibility, and oral-sex gestures belong in sexual route values because they are explicit sexual acts or sex-contextual actions.
- Keep high-variation sexual subfamilies as modular builder values instead of many sibling values in `generator.action.sexual`. Current modular routes are penetration and stimulation.
- `generator.action.sexual` is only for small standalone sexual options that are not yet large enough for their own builder value.
- Do not add clothing validation to stimulation or penetration routes by default; clothing presence/absence is useful variation unless the wording explicitly moves clothing.
- NSFW and sexual route values are gated with `subject.adult=true` and `content.nsfw_allowed=true`.
- Future adult-only NSFW/sexual action values should keep the same allow-state plus selected-adult-state validation.
- Add extra visible-body validation only when a concrete value requires a specific exposed/covered body state.
- Some actions depend on clothing state, such as dressing, undressing, clothing adjustment, underwear adjustment, or swimwear adjustment. Validate those concrete values against documented clothing-to-action existence/group states.
- Do not add clothing validation to actions that can happen equally over clothing or without clothing.
- Prefer the broadest accurate clothing-to-action state first. Generic clothing actions validate against `clothing.action.exist`; upper/lower body clothing actions validate against `clothing.action.upper_body.exist` or `clothing.action.lower_body.exist`; underwear actions validate against `clothing.action.underwear.exist`; swimwear actions validate against `clothing.action.swimwear.exist`.
- Do not validate actions against Pose-targeted clothing states such as `clothing.pose.*`.
- Do not validate actions against dozens of individual clothing values. If several clothing values share the same action-relevant meaning, those clothing values should set one shared Action-targeted state.
- Avoid duplicate exact prompt phrases inside the same generator. If a user-provided list repeats the same action under multiple sport/dance/yoga headings, keep one atomic prompt phrase unless distinct wording is needed.
- Active verbs such as touching, caressing, adjusting, washing, grabbing, holding an object, or leaning against support belong in Action. Pose may keep a static derived form such as `hands on the face` or `wall squat`.
- When an Action generator grows beyond roughly 25 non-empty options, split it into smaller semantic generators and let the builder contain multiple values pointing to those sets.
- When sibling Action builder values target the same result route but are separated by content class, keep their readable order `sfw -> nsfw -> sexual`. This is an authoring convention only; runtime still validates all candidate values first and randomly selects from the valid set.

## Future Pose Coordination

Action gives the prompt more context and life than Pose. Action can describe activity, movement, intent, object/support interaction, and scene behavior. Pose is the static posture/form/expression supplement.

When wording differs only by expression but stays static, it may remain Pose. When wording adds object/support/context, it belongs in Action. Example: `wall squat` is Pose; `squatting against a wall` is Action because it steers wall support and scene context.

Random Action output is controlled by internal state `activity.route=action`.

Action/Pose random behavior:

- if Action and Pose are both random-enabled, the node randomly chooses `activity.route=action` or `activity.route=pose`;
- if Action is random-enabled and Pose is manual or disabled, the route choice only considers Action, so random Action still runs;
- if Action random is disabled with override text, that manual text is emitted directly and bypasses route validation;
- if Action random is disabled with an empty override, Action intentionally emits nothing.

Do not add Action-owned Pose compatibility states for random Action/Pose coordination. The old partial compatibility model has been retired because it made the random path too directional and fragile.

Static pose vocabulary can still be derived from action vocabulary when the wording is genuinely a held form, but the active movement/object/context part stays in Action.

## Environment Validation

Action values may validate against:

- `environment.domain`
- `environment.location`
- `environment.room_area`
- `environment.surface`

Use this only for hard setting requirements. Do not validate portable actions just because a setting is plausible or common.

Examples:

- Yoga should not be location-gated by default because it can happen at home, outdoors, in a gym, or many other places.
- Cycling should validate at least against a compatible outdoor or future cycling-capable environment state when concrete cycling actions are added.
- Swimming should validate against pool/water context such as swimming-pool locations or pool room/area values.
- Urinating is NSFW-gated but has no Environment validation because it can technically happen anywhere.
- General washing actions, including body/hand/face/hair/intimate washing, do not validate against Environment by default because they are not automatically shower or bath actions.
- Showering validates against bathroom/shower-room context.
- Taking a bath validates against bathroom context.
- Singing or posing in the shower uses the same shower-capable validation as showering.
- Mirror actions require a mirror-capable room/area.
- Making the bed requires a bedroom or dorm room.
- Hard gymnastics apparatus values such as vault, beam, bars, rings, and pommel horse require `environment.room_area=in a gymnasium`.
- Hard fixed fitness-apparatus values such as treadmill, cycling machine, rowing machine, bench press, lat pulldown, battle ropes, and changing weight plates currently require `environment.room_area=in a gymnasium`. If home-gym or fitness-room environment states are added later, broaden this through a reusable environment-to-action state instead of duplicating room lists.
- `squatting against a wall` is an Action value, not a Pose value, because it uses wall support as contextual behavior. If no Environment surface is selected, the action wording may supply the wall. If a surface is selected, it must be `the wall` to avoid contradictions.
- Routine washing/grooming actions do not currently validate against Environment because they can be done with portable water or handheld items; add validation only if a future value has a hard setting requirement.
- Yoga and most dance/fitness actions are intentionally not environment-gated because they can technically happen in many places; add validation only when the concrete action requires a hard object or setting.

Use the broadest accurate Environment state. `environment.surface` is only for a selected object/support that cannot be modeled correctly through domain, location, or room/area. Do not validate action values against time, season, or weather unless the relation is redesigned and documented first.

Validation is based on physical possibility, not social acceptability. For example, `urinating` stays ungated by Environment even when the resulting place would be strange or inappropriate; `making the bed` is gated because the action names a bed, which is a hard room/area object in the current Environment model.

User-provided action lists are semantic input, not literal prompt text. Convert vague labels into prompt-ready values that stand alone without relying on the generator name. Dance values must say the dance style and movement when needed, such as `performing quick salsa footwork` instead of generic `quick footwork`.

## Current Vocabulary

General actions:

- `walking`
- `running`
- `jumping`
- `skipping`
- `crawling`
- `squatting against a wall`
- `leaning back against a surface`
- `leaning sideways against a surface`
- `sleeping`
- `yawning`
- `washing hands`
- `washing the face`
- `washing the belly`
- face, neck, abdomen, and torso touch/caress actions
- generic, upper-body, and lower-body clothing adjustment actions
- `playing with a towel`
- `washing the hair`
- `combing the hair`
- `applying makeup`
- `cleaning`
- `looking at oneself in a mirror`
- `looking at one's back in a mirror`
- `posing in front of a mirror`
- `reading a book`
- `using a computer`
- `making the bed`
- `dancing`
- `watching TV`
- `gaming`
- `drinking coffee`
- `drinking tea`
- `laughing`
- `looking outside`
- `dreaming`
- `watering plants`
- `cuddling blankets`
- `cuddling a pillow`
- `cuddling stuffed animals`
- `playing`
- `studying`
- `drawing`
- `interacting with the environment`

Sport actions:

- Gymnastics, yoga, fitness, dance, ballet, hip hop, salsa, tango, ballroom, contemporary dance, and K-pop/idol-style movement values live in `generator.action.sport`.
- Current sport vocabulary includes broad training/session values, specific gymnastics/acrobatic values, yoga poses and breathing/meditation values, gym/fitness exercise values, and dance-style/performance values.
- Exact duplicate concepts from the requested lists are kept as one phrase where practical, for example repeated `warming up` and `bridge pose` style concepts.

NSFW actions:

- `urinating`
- `showering`
- `taking a bath`
- `changing clothes`
- `undressing`
- `getting dressed`
- clothing-displacement exposure actions for breasts, buttocks, vulva, penis, and anus, validated against upper/lower clothing existence and gender where needed
- `washing the body`
- `washing the buttocks`
- `washing the vulva`
- `washing the penis`
- sensitive body-touch, caress, cup, and finger-touch actions
- `singing in the shower`
- `posing in the shower`
- `drying off`
- `posing suggestively in front of a mirror`
- `putting on underwear`
- `adjusting underwear with one hand`
- `taking off underwear`
- `putting on swimwear`
- `adjusting swimwear with one hand`
- `taking off swimwear`

Sexual actions:

- `posing sexually in front of a mirror`
- modular stimulation actions for breasts, nipples, vulva, clitoris, penis, anus, buttocks, and surface-based vulva/penis rubbing or pressing
- modular penetration actions for anus, vagina, and mouth, including self-penetrating, oral object sex, riding, sitting onto, and using an object for penetration
- penetration objects include banana, cucumber, dildo, vibrator, butt plug, glass dildo, pencil, hairbrush handle, toothbrush handle, marker, closed lipstick tube, remote control, and paintbrush handle
- Anal penetration wording should include both `anal` and `anus` when possible, such as `anal penetration of the anus`; avoid `anally`, because image models may underread that adverb.
- Vagina penetration wording should use `vagina` as the concrete noun, such as `vagina penetration`; avoid `vaginally` and prefer not to use `vaginal penetration` in Action prompt text.
- Oral-object sex wording should not rely on `oral sex` alone. Include the actual mouth action too, such as `putting {object} in the mouth for oral sex`, so the model sees both `mouth` and `oral sex`.
- spreading labia with fingers
- spreading buttocks to show the anus
- making a suggestive oral-sex gesture with one hand near the mouth

NSFW here means visibility/nudity/private-sensitive gating, not sexual action. Sexual action values are only for explicitly sexual or sex-contextual wording.
