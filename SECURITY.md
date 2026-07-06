# Security Notes

## API Keys

Do not paste private API keys into random websites. JobApp AI Assistant is designed to keep sensitive BYOK usage local:

- download and run the desktop app,
- open the localhost interface,
- add the API key inside the local app,
- keep generated files in local `exports/`.

The PagBiOmicS website embed is a download/education block. It should not collect API keys.

An experimental Web Lite page may be published for browser-based tests. In that mode, the user's browser calls the selected AI provider directly with the user's own API key. The main risk is API-key exposure in the browser environment. PagBiOmicS should label this clearly and recommend a temporary or restricted key that the user revokes or deletes after testing.

## Why Be Careful With BYOK In The Website?

Asking users to paste API keys into a website creates trust and liability problems:

- the user must trust the website operator with their key,
- the key could be logged by mistake,
- browser extensions or injected scripts may see sensitive fields,
- a backend proxy must be carefully secured and documented.

For early releases, the safer approach for repeated or sensitive work is a local executable. A static Web Lite mode can exist as a clearly labelled browser experiment if users are told to use a temporary or low-limit key and remove/revoke it after testing.

## Hosted API Roadmap

A hosted API mode can be added later only with:

- server-side secrets,
- rate limits,
- abuse protection,
- clear privacy policy,
- consent and data retention rules,
- cost controls,
- monitoring.

Until then, sensitive AI calls should use the user's own local key or local model inside the desktop app.
