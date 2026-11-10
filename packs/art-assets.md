# Pack: Art and asset generation

## Intake questions

- Style reference image(s) and three words for the look. What must it never resemble (brands, existing games, flags, real people)?
- Asset list: name, purpose, size on screen, transparent or not, states/poses.
- Which image tool is available in this session? If none, the output is prompts for the user to run.
- Who approves the style (G2 is the art-direction gate: one master image before any batch).

## Rules

- One approved master first. Every later prompt references the master so the set stays consistent.
- Save the exact prompt beside each image and list every file in a manifest with its hash and source prompt.
- State in each prompt: subject, style, framing, margin, background (transparent or not), what to exclude, "no text" unless text is the subject.
- Poses of one object: same camera, scale and placement in equal cells; one file per pose is safer than a sheet.
- Symbols must read at the smallest size they appear (for example 60 px). Verifier checks by downscaling with a script.
- Never describe an image you have not opened. Verifier opens every file: size, transparency, cropping, stray text.
- No real people, brands, or existing characters. Theme rules from the brief are constraints.
- Generation is the expensive step. Do not regenerate to "improve" an approved asset; change only what the user rejected.

## Acceptance checks

Manifest complete and hashes match · every file opened and checked · contact sheet shown at G3 · prompts saved.

## Lessons
