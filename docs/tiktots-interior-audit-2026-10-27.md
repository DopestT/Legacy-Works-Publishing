# Tik Tots Interior Audit — 2026-10-27

## Release decision

**BLOCKED for a 50-page production release until 50 distinct interior pages are present and individually marked `review_status: approved`.**

The available cover concepts advertise “50 Pages” / “50 Fun Pages.” During this pass, the indexed Tik Tots page assets located in the Library reached `TikTots_Page_038.png`; no reliable evidence for pages 039–050 was found. The engine therefore treats the 50-page claim as a hard expected-page-count gate rather than filling the gap with duplicates.

## Print-resolution blocker

- Sampled production interiors `TikTots_Page_010.png` and `TikTots_Page_014.png` are 1103×1426 pixels. At an 8.5×11 inch trim they provide about 129.8 effective DPI, below the current KDP 300-DPI image target. These source files should not be treated as print-ready 8.5×11 masters.
- The Tik Tots profile now requires `min_effective_dpi: 300`, so these low-resolution originals fail preflight until a true print-resolution master (or a separately reviewed prepared master) replaces them.

## Confirmed defect

- `TikTots_Page_003.png` visibly prints `www.tiktots.com` at the bottom. The canonical site is `tiktotskids.com`. This page must be corrected or excluded before approval.

## Visually checked URL false positives

Direct visual inspection showed the actual printed URL is correct (`tiktotskids.com`) on pages 013, 014, 016, 017, 019, 024, 028, 031, and 032. OCR alone is not an approval signal.

## Engine safeguards added from this audit

- Exact expected page count.
- Missing-asset rejection.
- Duplicate page ID rejection.
- Duplicate asset-path rejection.
- Duplicate image-content rejection using SHA-256, even if the duplicate is renamed.
- Minimum resolution checks.
- Line-art color-fraction check.
- Canonical/forbidden brand-text metadata checks.
- Approved-character metadata checks.
- Required explicit page review for the Tik Tots production profile.
- Streaming PDF generation so a 50-page 300-DPI book does not require all pages in RAM at once.

## Approval workflow

For each production page: visually compare character appearance and props to the references; verify clean line art; verify `tiktotskids.com`; confirm uniqueness; set `review_status` to `approved`; then run `legacy-books preflight` before PDF assembly.
