# Aliasing and the Sampling Theorem

A hands-on exploration of the Nyquist–Shannon sampling theorem: when
sampling goes wrong, why it goes wrong, what it sounds like, and how to
put a sampled signal back together correctly.

## How to run

The main deliverable, `notebook.ipynb`, is a self-contained Jupyter
notebook. To run it:

```bash
conda env create -f environment.yml
conda activate aliasing-project
jupyter lab notebook.ipynb
```

Run the cells in order. The notebook generates all figures from scratch
and writes audio files into `audio/` as it runs.

To rebuild the interactive widget after changes to `src/build_widget.py`:

```bash
python src/build_widget.py
```

If you don't want to install anything, the widget at
`widget/interactive.html` runs in any browser (double-click to open),
and the audio files in `audio/` play in any audio app.

## Project structure

```
.
├── README.md                ← this file
├── environment.yml          ← conda environment specification
├── .gitignore
├── notebook.ipynb           ← main deliverable: five-act walkthrough
├── audio/                   ← generated audio demonstrating aliasing
│   ├── chirp_reference_44100Hz.wav   (clean rising chirp, the reference)
│   ├── chirp_naive_4009Hz.wav        (naively downsampled — audible aliasing)
│   └── chirp_filtered_4009Hz.wav     (correctly downsampled with anti-alias filter)
├── widget/
│   └── interactive.html     ← standalone interactive widget (no install needed)
└── src/
    └── build_widget.py      ← script that builds widget/interactive.html
```

## Project overview

The notebook tells a story in five acts:

1. **The mystery.** A 440 Hz signal sampled two ways, with two completely
   different spectra. Why?
2. **The theorem.** The Nyquist–Shannon sampling theorem stated cleanly,
   the spectral-folding picture, and a verification table that confirms
   the alias-frequency formula.
3. **The sound of aliasing.** A chirp sampled three ways, with audio
   files and spectrograms showing what aliasing sounds like and how an
   anti-alias filter prevents it.
4. **Reconstruction.** Three methods compared — zero-order hold, linear
   interpolation, and Whittaker–Shannon sinc interpolation — including
   an empirical demonstration that finite-window sinc error decays as
   $1/T$, exactly as the theorem's infinite-sum assumption predicts.
5. **Play with it.** An interactive widget walking through 12 curated
   scenarios that illustrate the full parameter space.

## Author

Patricia Nistor, 2026
