# Scholar voice character

- `reference/`: preserve the supplied character sheet and generation references.
- `src/`: reproducible MCP, Blender build, animation and QA scripts.
- `output/`: downloaded source models and versioned editable Blender/GLB outputs.
- `qa/`: provider response records, diagnostic images, preview frames and validation reports.
- Keep OAuth credentials in the Codex credential store. Never write tokens or signed upload/download URLs into shared documentation.
- Start with one Hyper3D generation; preserve its identifiers and source model. Do not automatically retry a timed-out generation.
- Use one character only; the reference sheet depicts multiple views of that same character.
- Target restrained voice-interaction motion. Preserve the hat, beard, costume and proportions.
- Validate model orientation, packed textures, skin weights, representative deformations and continuous animation before declaring success.
- Document whether speech motion is illustrative or driven by actual audio. Do not describe illustrative jaw motion as phoneme-synchronized lip sync.
- v2 adds separate A/E/I/O/U mouth geometry shape keys, natural lowered arms, walking and running. Keep v1 deliverables intact; save new files with `_v2` names.
- Live LLM integration is a future consumer. Deliver stable morph/action names and mixing guidance; do not claim an operational speech service without an actual audio pipeline.
- Realtime integration is now authorized: `src/realtime_v1/` holds the local web client, server and tests; `qa/realtime_v1/` holds sanitized verification evidence. Reuse the v3 GLB without modifying prior models. Keep API credentials server-side, optionally reuse only AIRI's Qwen settings from a temporary copy of its local database; never log or persist the key. Browser access is loopback-only. Verify audio scheduling, interruption, morph reset, provider connection and browser rendering separately. Clearly label acoustic mouth estimation as approximate, not phoneme alignment.
- v3 uses the supplied viseme, gaze, emotion, hand/boot and gesture sheets as visual references. Preserve v1/v2. Keep existing vowel names compatible; implement body gestures as bone Actions, not whole-body Shape Keys. Save v3 sources, local part replacements and quality evidence separately. Do not represent procedural detail additions as a new Hyper3D reconstruction.
