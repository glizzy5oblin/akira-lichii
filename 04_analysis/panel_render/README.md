# panel_render: static + mock-backend copy of the carved "Akira Remote" panel

Everything here uses FAKE data (example.test, 203.0.113.x, "FAKE-..." strings). Nothing real, no outbound
connections from the mock (server binds 127.0.0.1; only the Font Awesome icon CSS comes from cdnjs).

- `panel_view.html` / `theme.css`: first, JS-less static copy (older; the mock below is better).
- `mock/server.mjs`: serves the carved panel (`../panel_source`) and answers `/api/*` with fake data. No websockets.
  Note: `panel_source/theme.css.txt` is really *viewer.css* and `extra_01_1106c4e.txt` is the real *theme.css* (tokens).
- `mock/shoot.mjs`: headless Chrome via CDP; opens each tool and writes PNGs to `screenshots/`.
- Run: `node mock/server.mjs &` then `open http://127.0.0.1:8765/` or `node mock/shoot.mjs`.
