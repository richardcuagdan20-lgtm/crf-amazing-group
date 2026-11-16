# Logo slot

Replace `logo.svg` with the official CRF Amazing Group mark (SVG preferred, or `logo.png`).

`src/components/Logo.astro` is the single swap point. Today it uses:

- `/brand/logo.svg` on navy backgrounds (header and footer). If the official file is a dark-on-light mark, also add a light-on-navy version and point the header/footer to it in `Logo.astro`.
- `/brand/wordmark.svg` (gold + navy) if a light-background variant is needed.

The typographic SVGs in this folder are placeholders only. Do not treat them as the official logo.
