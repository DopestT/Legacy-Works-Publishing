# Tik Tots — 50-Page Coloring Book Production Map

## Locked structure

- Cover files are not counted as coloring interiors.
- `TikTots_Page_010.png` is front matter (`This Book Belongs To`) and is not counted among the promised 50 coloring pages.
- Existing candidate coloring interiors are `TikTots_Page_011.png` through `TikTots_Page_038.png`: **28 candidate interiors**.
- The production book therefore needs **22 new, distinct coloring interiors** to reach 50 actual coloring pages.
- Every production interior must pass the reusable engine preflight and be individually marked `review_status: approved`.
- Existing low-resolution art must not be considered print-ready merely by changing DPI metadata. The release target is an effective 300 DPI at 8.5×11 inches.

## Existing candidate interiors — book pages 1–28

| Book page | Source | Scene |
|---:|---|---|
| 1 | TikTots_Page_011.png | Crew running through a magical doorway |
| 2 | TikTots_Page_012.png | Art studio creation scene |
| 3 | TikTots_Page_013.png | Music courtyard |
| 4 | TikTots_Page_014.png | Garden exploration / magnifying glass |
| 5 | TikTots_Page_015.png | Build Zone blocks |
| 6 | TikTots_Page_016.png | Science lab |
| 7 | TikTots_Page_017.png | Garden / planting |
| 8 | TikTots_Page_018.png | Magical garden run |
| 9 | TikTots_Page_019.png | Kindness Court gardening |
| 10 | TikTots_Page_020.png | Map exploration |
| 11 | TikTots_Page_021.png | Movie set |
| 12 | TikTots_Page_022.png | Puzzle garden |
| 13 | TikTots_Page_023.png | Photo studio |
| 14 | TikTots_Page_024.png | Music celebration |
| 15 | TikTots_Page_025.png | Build Zone rocket |
| 16 | TikTots_Page_026.png | Telescope / space science |
| 17 | TikTots_Page_027.png | Outdoor art |
| 18 | TikTots_Page_028.png | Brighter World doorway |
| 19 | TikTots_Page_029.png | Starry door in bedroom |
| 20 | TikTots_Page_030.png | Creative room teamwork |
| 21 | TikTots_Page_031.png | Music park |
| 22 | TikTots_Page_032.png | Rocket workshop |
| 23 | TikTots_Page_033.png | Space/science activity |
| 24 | TikTots_Page_034.png | Picnic |
| 25 | TikTots_Page_035.png | Treasure hunt |
| 26 | TikTots_Page_036.png | Film set / directing |
| 27 | TikTots_Page_037.png | Photo booth |
| 28 | TikTots_Page_038.png | Shapes activity |

## New interiors — book pages 29–50

These scenes are deliberately chosen to broaden the book instead of repeating the existing art/music/build/science/movie/photo/treasure themes.

29. **Library Adventure** — Tiko and friends in a whimsical library, opening books and discovering a tiny glowing door between shelves.
30. **Robot Coding Day** — Zee guides a friendly small robot through a simple floor maze while the crew helps with arrows and blocks.
31. **Ocean Discovery** — the crew explores a kid-friendly underwater observation room with fish, coral shapes, and Buddy watching through a window.
32. **Weather Station** — clouds, sun, wind sock, rain gauge, and the kids recording weather together.
33. **Animal Care Day** — gentle pet-care scene with bowls, brushes, blankets, and Buddy helping welcome another friendly animal.
34. **Team Relay** — cooperative outdoor relay course emphasizing cheering, teamwork, cones, hoops, and finish-line fun.
35. **Dance Studio** — mirrors, music notes, simple dance poses, and the crew learning a routine together.
36. **Cooking Together** — kid-safe kitchen scene mixing fruit, measuring ingredients, decorating healthy snacks, and cleaning as a team.
37. **Nature Hike** — trail signs, leaves, binoculars, bug viewer, water bottles, and a scenic overlook.
38. **Birdwatching Morning** — birdhouse, binoculars, sketchbook, feathers, nests at a respectful distance, and Buddy sitting quietly.
39. **Community Cleanup** — gloves, recycling bins, litter grabbers, flowers, and a park becoming cleaner as everyone helps.
40. **Recycling Invention** — cardboard, bottles, boxes, gears, tape, and a playful invention assembled from reused materials.
41. **Simple Machines Lab** — ramps, pulleys, levers, wheels, and the kids testing how things move.
42. **World Map Adventure** — giant floor map, compass, globe, travel stickers, and doors representing different landscapes without stereotypes.
43. **Dinosaur Museum** — fossils, footprints, skeleton displays, magnifying glass, and a paleontology dig table.
44. **Aquarium Helpers** — observation tanks, sea-creature drawings, water-testing tools, and a conservation message conveyed visually.
45. **Kindness Mail** — the crew writes cheerful cards and sorts them into decorated mailboxes for friends and neighbors.
46. **Puppet Theater** — homemade puppets, curtain stage, props, story cards, and the crew performing for one another.
47. **Playground Designers** — blueprint sheets, rulers, blocks, slide/swing ideas, and a model playground built collaboratively.
48. **Train Station Adventure** — friendly toy-like station, maps, clocks, luggage shapes, and the crew learning how routes connect.
49. **Puzzle Door Challenge** — a magical door surrounded by visual pattern puzzles, shape keys, gears, and teamwork clues.
50. **Big Brighter World Finale** — all five kids and Buddy at a giant open doorway with icons from the whole book, celebrating creativity, kindness, exploration, and teamwork.

## Generation rules for the 22 new pages

- Black-and-white coloring-book line art only: clean white background, bold readable outlines, no gray fill, no color, no photographic shading.
- Portrait composition designed for 8.5×11 inches with safe margins.
- Consistent Tik Tots character appearances and proportions across every page.
- Use the established cast only: Tiko, Mia, Jax, Zee, Lulu, and Buddy.
- No extra recurring child characters unless explicitly approved.
- Buddy keeps the `B` collar tag.
- Avoid embedding website text inside generated artwork. The production pipeline should place the canonical `tiktotskids.com` footer mechanically so spelling cannot drift.
- Avoid large generated text signs unless the wording is later added mechanically in production.
- Each scene must be compositionally distinct from every existing and new interior.

## Release gate

The book is publish-ready only when the final manifest contains exactly 50 distinct coloring interiors, every page passes visual review and preflight, effective print resolution passes the configured threshold, and the front matter/cover are handled separately from the 50-page promise.
