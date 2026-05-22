# Random Prompt Builder V2 Architecture

## Node Shape

Implemented file:

- `nodes/JSGRandomPromptBuilderV2.py`

Registered display name:

- `Random Prompt Builder V2`

Data folder:

- `data/random_prompt_builder_v2/`

Before changing JSON structure, category order, resolve order, builders, generators, values, state writes, tags, or validation behavior, check `context/random-prompt-builder-v2-category-relations.md`. If the change creates or changes a category relationship, update that central relation map in the same work session.

Outputs:

- `Positive Prompt`
- `Negative Prompt`
- `Debug State`
- `Subject`

`Debug State` is a readable string overview of the final global state, state write priorities, and active tags after generation.

`Subject` is only the resolved Subject category text, intended for filenames, labels, and similar utility use. It mirrors the generated subject or the manual Subject override when Subject randomization is disabled. Other category-specific prompt parts are not exposed as separate node outputs by default.

## Inputs

Base inputs:

- `always_load`: forces ComfyUI to re-run the node. During every actual `build()` execution, V2 reloads config, category files, universal generators, state profile, and preset JSON so file edits are picked up without restarting/reloading ComfyUI.
- `preset`: selects default model positive/negative fragments. Preset positive fragments are appended after generated category text so quality/style steering stays at the end of the full positive prompt.
- `state_profile`: selects initial state/tags applied before category generation.
- `tag_lora`: positive-only LoRA trigger text.

Per category:

- `random_<category>`: when true, generate from JSON.
- `<category>_override`: when random is false, this string replaces the whole category.

Override behavior:

- override replaces the full category;
- empty override means the category is skipped;
- random generation can also resolve empty and be skipped;
- overrides are text-only and do not infer state.

V2 currently supports one generated subject. A manual override can write whatever text the user wants, but generator logic is designed around one subject.

## JSON Layout

Current layout:

- `data/random_prompt_builder_v2/config.json`
- `data/random_prompt_builder_v2/presets/*.json`
- `data/random_prompt_builder_v2/state_profiles/*.json`
- `data/random_prompt_builder_v2/categories/*.json`
- `data/random_prompt_builder_v2/shared_generators/*.json`

Prompt values start empty. Do not migrate old random prompt text wholesale. The old builder may be used for ideas only.

Each category has one JSON file. That category file contains its own category-output builders. Do not split a category across exposed/internal files.

Shared generator files should be organized by actual need:

- if there is only one broad universal picker of a kind, it may live in `shared_generators/universal.json`;
- if a shared concept grows into multiple related pickers, split it into a logical file;
- example: one color picker can live in `universal.json`, but once there are several color pickers for different purposes, move them into `shared_generators/colors.json`.

## Generator Model

Keep the JSON structure simple:

- category files own builders;
- builders are not generator objects and are not used as local helper pickers;
- do not use `private` helper builders for generator-like values;
- all random value pickers used by builder value slots belong in `shared_generators/`;
- pure random value generators should be moved to a logical universal generator file, even when first used by one category;
- universal generators may set state or filter by state/tag, but must remain universal;
- universal generator values must not filter by builder slots.
- builder-level metadata can set fixed states/tags and slot-exported states after the selected builder value produces a non-empty result;
- use builder-level metadata for facts shared by every non-empty result from that builder, then builder-value metadata, then generator-value metadata only when the variation truly lives inside the generator values.

Category builders each produce one category prompt element. A category may contain multiple builders, and category output joins builder outputs with commas. Use multiple builders only for stackable category dimensions, such as Environment domain, location, room/area, surface, weather, and time. Mutually exclusive alternatives for the same conceptual slot must be sibling values inside one builder, not separate builders guarded by lock states.

## Implementation Notes

Implemented behavior:

- JSON is loaded fresh every run.
- Presets can add positive and negative prompt fragments. Preset positives are appended after generated category output; preset negatives are still collected into the negative prompt.
- State profiles can seed initial state/tags before any category resolves.
- State writes track optional priority metadata. Default priority is `0`; only a strictly higher priority may overwrite an existing state key.
- Category overrides replace full categories.
- Random mode resolves listed category `values` and category-local `builders`.
- Every random picker call uses a fresh seed from `os.urandom(16)`. The runtime tracks seeds used during the current build and regenerates if a seed would repeat, so no two `choice` calls in the same build intentionally share the same seed.
- Builder outputs are joined as comma-separated category prompt elements.
- `export_as` exposes a builder result as a category-local slot for later builders.
- Values may be empty strings, strings, or objects depending on whether they are generator values or builder value objects.
- Selected values may emit positive text, negative text, state, and tags.
- Universal generator registry loads recursively from `data/random_prompt_builder_v2/shared_generators`.
- Category builders are still resolved through their owning category registry.
- Templates support `{slot}` placeholders only when the builder value defines that slot explicitly.
- Slot dependencies are resolved only inside the currently selected builder value or from category-local slots already exported by earlier builders in the same category.
- State conditions only read the state that already exists from state profiles and earlier resolved categories/builders. V2 does not lazy-load later builders for validation.
- Generator values can carry their own `conditions`, `negative`, and `state_set`, but universal generator conditions cannot use builder slots.
- Generator value `state_set` is preserved through slot-based use.
- Builder value `state_export` can export resolved slot text into global state, including object syntax such as `{ "slot": "item" }`.
- Empty slot exports are skipped by default; object-form `state_export` can explicitly write `null` with `"empty": "null"` when a later check needs that distinction.
- `state_set` supports optional top-level `state_priority` and object-form values containing `value` plus `priority`; object-form `state_export` also supports `priority`.
- State condition comparison distinguishes absent state keys from explicit `null` for `equals null`, while both absent and null still count as `missing`.
- Builders may carry state/tag `conditions` that skip the entire builder before value selection.
- Builders choose from their own validated random `values`; each selected builder value is an object and can contain `template`, `slots`, `conditions`, `text`, `negative`, and state/tag effects.
- Value-level validation remains authoritative; builder-level validation is used only for builder-wide gates that every meaningful value shares.
- Slot resolution filters possible slot-local values before the final random choice.
- Global state starts from the selected state profile. The `none` profile preserves absolute-null startup.
- Config `order` controls final prompt order. Config `resolve_order` controls validation/state traversal and defaults to `order` when omitted. Since there is no lazy loading, every cross-category dependency must be satisfied by placing the state-producing category earlier in `resolve_order`.

Current reset baseline intentionally contains filled values only for Subject, Ethnicity, Clothing coverage, and Clothing Style. Other category builders and universal generators remain as empty scaffolds so their structure can be reviewed before values are added again.

## State Profiles

State profiles are V2's initial state mechanism.

Current profile options:

- `SFW`: both genders, SFW routes only.
- `NSFW`: both genders, NSFW routes only.
- `Mixed`: both genders, SFW and NSFW routes.
- `SFW Female`, `NSFW Female`, `Mixed Female`.
- `SFW Male`, `NSFW Male`, `Mixed Male`.

Profiles write `content.sfw_allowed`, `content.nsfw_allowed`, `profile.content_mode`, and `profile.gender_mode`. Gender-specific profiles also seed `subject.gender` at priority `-1` for manual Subject overrides. Generated Subject values write at default priority `0`, but they must validate against `profile.gender_mode` before selection, so Female profiles generate only female Subject values and Male profiles generate only male Subject values. Profiles seed `subject.adult=true` at priority `-1` so manual Subject overrides can still allow adult-gated values. Generated Subject values overwrite the fallback adult state with the selected subject's actual adult/non-adult value.

Profiles may also define debug-only `ignore_state_keys` and `ignore_tags` arrays. These do not create node UI controls and do not bypass whole values/builders/generators. They only neutralize individual matching state/tag condition checks; all other checks on the same object still validate normally.

The default profile is `Mixed Female`.

## Category Order

Config `order` is prompt output order.

Config `resolve_order` is the validation/state traversal order. It should be explicit on every configured category, even though the node can technically default to `order` when omitted. There is no lazy loading: if a category or generator validates against another category's state, the producing category must resolve earlier.

Current validation order:

- `subject`: `resolve_order=0`
- `environment`: `resolve_order=1`
- `clothing`: `resolve_order=2`
- `action`: `resolve_order=3`
- `pose`: `resolve_order=4`
- `body_detail`: `resolve_order=5`
- `body_build`: `resolve_order=6`
- `ethnicity`: `resolve_order=7`
- `composition`: `resolve_order=8`
- `lighting`: `resolve_order=9`
- `style`: `resolve_order=10`
- `quality`: `resolve_order=11`

Intentional differences from prompt order:

- Environment resolves before Clothing and Action because both read environment-owned state from category files and shared generator values.
- Clothing resolves before Action because Action values read `clothing.action.*` state.
- The node sets internal `activity.route` before category generation. Random Action requires `activity.route=action`; random Pose requires `activity.route=pose`. The route is selected only from Action/Pose categories whose random toggle is enabled, while manual override text bypasses the route and still outputs directly.
- Body Detail, Body Build, Ethnicity, Composition, Lighting, Style, and Quality currently do not produce state consumed by later active categories, so they resolve after the dependency-producing chain. They keep their prompt `order` positions for final text.

The node UI/category input order follows prompt `order`, not `resolve_order`. Final prompt order keeps Body Build, Body Detail, and Clothing in their authored text positions even though validation resolves Environment and Clothing earlier.

Category UI inputs are generated from `config.categories` sorted by prompt `order`, so the visible node order should not mirror validation order.

After the reset, most categories do not emit prompt text even though their order and resolve order are preserved. Keep this split in place because the empty scaffold may be refilled gradually.

## Verification Notes

Last verified:

- Python syntax compile passed using ComfyUI embedded Python.
- JSON scaffolds parsed with PowerShell `ConvertFrom-Json`.
- Direct node build with `tag_lora` and subject override returned the expected positive prompt.
- Resolver rendered builder value templates with slots, while universal generators stayed state-based rather than builder-slot-based.
