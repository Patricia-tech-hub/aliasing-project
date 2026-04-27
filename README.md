# Aliasing and the Sampling Theorem

A hands-on exploration of the Nyquist–Shannon sampling theorem: when sampling
goes wrong, why it goes wrong, what it sounds like, and how to put a sampled
signal back together correctly.

## What's in here

- **`notebook.ipynb`** — the main deliverable. A self-contained walkthrough
  from "here's a sine wave" to "here are three reconstruction methods compared".
  Open and run top-to-bottom.
- **`widget/interactive.html`** — a standalone interactive widget. Sliders for
  signal frequency and sample rate; spectrum updates live. Double-click to open
  in any browser; no install required.
- **`audio/`** — generated audio demonstrating audible aliasing. Listen to
  `chirp_original.wav` then `chirp_aliased_*.wav`.
- **`report/report.pdf`** — the written report.
- **`figures/`** — figures used in the report, exported from the notebook.

## How to run

```bash
conda env create -f environment.yml
conda activate aliasing-project
jupyter lab notebook.ipynb
```

If you don't want to install anything, the widget at `widget/interactive.html`
runs in any browser, and the audio files in `audio/` play in any audio app.

## Project structure

[tree from above]

## Author

Patricia Nistor, 2026