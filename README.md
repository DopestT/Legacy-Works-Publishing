# Legacy Works Book Engines

Reusable publishing engines for coloring books and voiceover books. Tik Tots is the first strict brand profile, not hard-coded product logic.

## What this fixes

The existing publishing repository referenced a completed KDP pipeline archive, but the unpacked pipeline code is not present on `main`. This package restores the reusable core as inspectable, tested code.

For Tik Tots, the engine fails closed when interiors have the wrong page count, missing or duplicate assets, insufficient effective print DPI, unexpected color in line-art pages, unapproved character metadata, missing review approval, or known brand/URL drift. The canonical Tik Tots URL is `tiktotskids.com`.

## Install

```bash
python -m pip install -e .
```

## Coloring-book workflow

1. Put approved interior art in a book workspace under `assets/`.
2. List every page in order in `book.json`.
3. Run preflight:

```bash
legacy-books preflight book.json --profile brand.json
```

4. Only after preflight passes, build the PDF:

```bash
legacy-books coloring book.json --profile brand.json --output build/interior.pdf
```

The renderer fits each source page inside the configured trim size without stretching it.

## Voiceover-book workflow

A story manifest uses page-level narration and optional timing. Build a narration package with:

```bash
legacy-books voiceover story.json --profile brand.json --output-dir build/voiceover
```

Outputs:
- `narration.txt`
- `narration.ssml`
- `timeline.json`
- `render_queue.json`

`render_queue.json` is intentionally provider-neutral. A TTS adapter can render the queued per-page MP3 files without changing the book or story format.

## Duplicate the engine for more books

Do **not** copy the Python engine. Create a new book workspace from a brand profile:

```bash
legacy-books init-book --profile profiles/tiktots.brand.json --destination books/tiktots-book-02 --title "Tik Tots: Book Two"
```

That creates `brand.json`, `book.json`, `story.json`, and `assets/`. For another brand, create one new brand profile and reuse the same engine.

## Tik Tots current asset gate

The approved cover concepts say “50 Pages,” so the production coloring manifest must contain 50 distinct, approved interior pages before release. Sampled existing interiors are 1103×1426 pixels (about 130 effective DPI at 8.5×11), so the Tik Tots production profile also blocks them until true 300-DPI print masters are available. The template in `examples/tiktots-coloring.book.template.json` intentionally fails until the full approved interior set is supplied; this prevents accidental publication with missing or duplicated pages.

The first voiceover example is `examples/tiktots-endless-scroll.story.json`.
