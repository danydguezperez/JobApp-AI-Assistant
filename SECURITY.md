# Security Notes

## API Keys

Do not paste private API keys into random websites. JobApp AI Assistant is designed to keep BYOK usage local:

- download and run the desktop app,
- open the localhost interface,
- add the API key inside the local app,
- keep generated files in local `exports/`.

The PagBiOmicS website embed is a download/education block. It should not collect API keys.

## Why Not BYOK In The Website?

Asking users to paste API keys into a website creates trust and liability problems:

- the user must trust the website operator with their key,
- the key could be logged by mistake,
- browser extensions or injected scripts may see sensitive fields,
- a backend proxy must be carefully secured and documented.

For early releases, the safer approach is a local executable.

## Hosted API Roadmap

A hosted API mode can be added later only with:

- server-side secrets,
- rate limits,
- abuse protection,
- clear privacy policy,
- consent and data retention rules,
- cost controls,
- monitoring.

Until then, AI calls should use the user's own local key or local model.
