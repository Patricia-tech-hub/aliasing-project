"""
Builds widget/interactive.html — a standalone interactive widget that
walks through 12 curated scenarios illustrating different sampling regimes.
"""

from pathlib import Path
import numpy as np
import plotly.graph_objects as go


# ---------- The curated scenarios ----------
# Each: (f Hz, fs Hz, short_label, caption)
# Captions use <br> at natural breakpoints so they wrap inside the figure title.

SCENARIOS = [
    (200, 4000,
     "1. Comfortable oversampling",
     "fs is 20× the signal frequency. The samples trace the signal closely;<br>the spectrum shows a single clean peak at 200 Hz."),
    (200, 1000,
     "2. Lower fs, still safe",
     "Reduced to 5× oversampling. Sparser dots, but Nyquist is still comfortably satisfied<br>and the peak remains at 200 Hz."),
    (200, 800,
     "3. Just above Nyquist",
     "fs = 4 × f. We are approaching the limit, but still on the safe side:<br>the peak stays at 200 Hz."),
    (200, 350,
     "4. First failure: aliasing begins",
     "fs < 2f, so Nyquist is violated. The closest spectral copy is at |200 − 350| = 150 Hz,<br>which now sits inside the visible band. The signal pretends to be a lower tone."),
    (500, 800,
     "5. Heavier aliasing",
     "f = 500, fs = 800. The closest copy is at |500 − 800| = 300 Hz.<br>The further f is above the Nyquist limit fs/2, the further the alias from the truth."),
    (440, 600,
     "6. The Act 1 case",
     "440 Hz sampled at 600 Hz: the example that opened the notebook.<br>The aliased peak appears at |440 − 600| = 160 Hz."),
    (1000, 600,
     "7. Signal frequency above fs",
     "Now f > fs entirely. The aliasing formula picks the nearest multiple of fs to f:<br>round(1000/600) = 2, so the alias is at |1000 − 2·600| = 200 Hz."),
    (600, 600,
     "8. f = fs — alias collapses to DC",
     "When f = fs, we sample at the same phase every cycle. Every sample has the same value,<br>and the alias formula gives |600 − 600| = 0 Hz. The signal disappears into a constant."),
    (1200, 600,
     "9. f = 2·fs — same DC trap",
     "Two full cycles between samples. Same outcome as scenario 8: |1200 − 2·600| = 0.<br>Any integer multiple of fs aliases to DC."),
    (700, 600,
     "10. Slightly above fs",
     "f just above fs. Closest copy: |700 − 600| = 100 Hz.<br>A 700 Hz signal pretends to be a 100 Hz tone."),
    (500, 1050,
     "11. Just above Nyquist — alias just escapes",
     "fs = 1050 Hz, just above the Nyquist requirement of 1000. The peak stays at 500 Hz;<br>the nearest spectral copy lands at |500 − 1050| = 550 Hz, just outside the visible band."),
    (800, 2000,
     "12. Back to comfortable — closing the arc",
     "f = 800, fs = 2000: 2.5× oversampling, peak at 800 Hz.<br>Sampling done right preserves the signal exactly; sampling done wrong destroys it irreversibly."),
]

CYCLES = 4
N_CONT = 800
N_FFT_WINDOW = 1.0
F_VIEW_MAX = 5000


# ---------- Helpers ----------

def predicted_alias(f, fs):
    """Distance from f to the nearest integer multiple of fs."""
    k = round(f / fs)
    return abs(f - k * fs)


def title_for(f, fs, label, caption):
    """
    Build a three-line title:
      1. Bold scenario label
      2. Parameter subtitle (peak/alias info)
      3. Caption (the teaching point)
    All wrapped via <br>. This avoids the annotation-vs-slider collision
    we'd get from a free-floating caption box.
    """
    is_safe = fs > 2 * f
    if is_safe:
        params = f"f = {f} Hz, fs = {fs} Hz — peak at {f} Hz (no aliasing)"
    else:
        alias = predicted_alias(f, fs)
        params = f"f = {f} Hz, fs = {fs} Hz — aliased to {alias:.0f} Hz"

    return (
        f"<b>{label}</b>"
        f"<br><span style='font-size:13px;color:#555'>{params}</span>"
        f"<br><span style='font-size:12px;color:#222'>{caption}</span>"
    )


def build_scenario_traces(f, fs):
    duration = CYCLES / f
    t_cont = np.linspace(0, duration, N_CONT)
    x_cont = np.sin(2 * np.pi * f * t_cont)
    t_samp = np.arange(0, duration, 1 / fs)
    x_samp = np.sin(2 * np.pi * f * t_samp)

    n_fft = int(round(N_FFT_WINDOW * fs))
    t = np.linspace(0, N_FFT_WINDOW, n_fft, endpoint=False)
    x = np.sin(2 * np.pi * f * t)
    N = len(x)
    X = np.fft.fft(x)
    spec_freqs = np.fft.fftfreq(N, d=1 / fs)[:N // 2]
    spec_mag = np.abs(X[:N // 2]) * 2 / N

    alias = predicted_alias(f, fs)
    spec_xmax = min(fs / 2, max(2 * alias + 200, 1.5 * f, 300))

    peaks_in_x, peaks_in_y = [], []
    peaks_out_x, peaks_out_y = [], []
    n_copies = int(np.ceil(F_VIEW_MAX / fs)) + 1
    for k in range(-n_copies, n_copies + 1):
        for sign in (+1, -1):
            p = sign * f + k * fs
            if -F_VIEW_MAX <= p <= F_VIEW_MAX:
                if -fs / 2 <= p <= fs / 2:
                    peaks_in_x.extend([p, p, None])
                    peaks_in_y.extend([0, 1, None])
                else:
                    peaks_out_x.extend([p, p, None])
                    peaks_out_y.extend([0, 0.6, None])

    return [
        # Trace 0: continuous signal — hoverable, shows time and amplitude
        go.Scatter(x=t_cont * 1000, y=x_cont, mode="lines",
                   line=dict(color="#888", width=1.5),
                   name="continuous signal",
                   hovertemplate="t = %{x:.2f} ms<br>amplitude = %{y:.3f}<extra></extra>",
                   xaxis="x1", yaxis="y1", showlegend=False),
        # Trace 1: samples — hoverable, shows time and amplitude
        go.Scatter(x=t_samp * 1000, y=x_samp, mode="markers",
                   marker=dict(color="#1f77b4", size=8),
                   name="sample",
                   hovertemplate="t = %{x:.2f} ms<br>amplitude = %{y:.3f}<extra></extra>",
                   xaxis="x1", yaxis="y1", showlegend=False),
        # Trace 2: spectrum — hoverable, shows frequency and magnitude
        go.Scatter(x=spec_freqs, y=spec_mag, mode="lines",
                   line=dict(color="#d62728", width=1.5),
                   name="spectrum",
                   hovertemplate="f = %{x:.1f} Hz<br>magnitude = %{y:.3f}<extra></extra>",
                   xaxis="x2", yaxis="y2", showlegend=False),
        # Trace 3: predicted alias line — decorative, no hover
        go.Scatter(x=[alias, alias], y=[0, 1.1], mode="lines",
                   line=dict(color="#1f77b4", width=2, dash="dash"),
                   hoverinfo="skip",
                   xaxis="x2", yaxis="y2", showlegend=False),
        # Trace 4: in-band spectral copies — decorative, no hover
        go.Scatter(x=peaks_in_x, y=peaks_in_y, mode="lines",
                   line=dict(color="#1f77b4", width=3),
                   hoverinfo="skip",
                   xaxis="x3", yaxis="y3", showlegend=False),
        # Trace 5: out-of-band spectral copies — decorative, no hover
        go.Scatter(x=peaks_out_x, y=peaks_out_y, mode="lines",
                   line=dict(color="#bbbbbb", width=2),
                   hoverinfo="skip",
                   xaxis="x3", yaxis="y3", showlegend=False),
        # Trace 6: visible band rectangle — decorative, no hover
        go.Scatter(
            x=[-fs/2, fs/2, fs/2, -fs/2, -fs/2],
            y=[0, 0, 1.1, 1.1, 0],
            fill="toself", mode="lines",
            line=dict(color="#ffe9b3", width=0),
            fillcolor="rgba(255,233,179,0.5)",
            hoverinfo="skip",
            xaxis="x3", yaxis="y3", showlegend=False),
    ], spec_xmax


def panel_header_annotations():
    """The three panel-header annotations. Same on every frame."""
    return [
        dict(text="<b>Time domain</b> — does the sample trace the signal?",
             xref="paper", yref="paper", x=0, y=1.02,
             showarrow=False, xanchor="left",
             font=dict(size=12, color="#444")),
        dict(text="<b>Spectrum</b> — red: measured FFT;  blue dashed: predicted alias",
             xref="paper", yref="paper", x=0, y=0.65,
             showarrow=False, xanchor="left",
             font=dict(size=12, color="#444")),
        dict(text="<b>Spectral folding</b> — yellow: visible band;  blue: in-band peaks;  gray: out-of-band peaks",
             xref="paper", yref="paper", x=0, y=0.27,
             showarrow=False, xanchor="left",
             font=dict(size=12, color="#444")),
    ]


# ---------- Build frames ----------

initial_traces, initial_spec_xmax = build_scenario_traces(*SCENARIOS[0][:2])
f0, fs0, label0, caption0 = SCENARIOS[0]

frames = []
for i, (f, fs, label, caption) in enumerate(SCENARIOS):
    traces, spec_xmax = build_scenario_traces(f, fs)
    frames.append(go.Frame(
        name=str(i),
        data=traces,
        layout=go.Layout(
            title=dict(
                text=title_for(f, fs, label, caption),
                x=0.02, xanchor="left",
                y=0.98, yanchor="top",
            ),
            xaxis2=dict(range=[0, spec_xmax]),
            annotations=panel_header_annotations(),
        ),
    ))


# ---------- Build the figure ----------

fig = go.Figure(data=initial_traces, frames=frames)

fig.update_layout(
    title=dict(
        text=title_for(f0, fs0, label0, caption0),
        x=0.02, xanchor="left",
        y=0.98, yanchor="top",
    ),
    height=1000,
    # Larger top margin to fit the three-line title.
    # Smaller bottom margin since there's no caption box anymore.
    margin=dict(t=160, b=120, l=70, r=30),
    xaxis1=dict(domain=[0, 1], anchor="y1", title="Time (ms)"),
    yaxis1=dict(domain=[0.72, 0.98], anchor="x1",
                title="Amplitude", range=[-1.2, 1.2]),
    xaxis2=dict(domain=[0, 1], anchor="y2", title="Frequency (Hz)",
                range=[0, initial_spec_xmax]),
    yaxis2=dict(domain=[0.40, 0.60], anchor="x2",
                title="Magnitude", range=[0, 1.1]),
    xaxis3=dict(domain=[0, 1], anchor="y3",
                title="Frequency (Hz)",
                range=[-F_VIEW_MAX, F_VIEW_MAX]),
    yaxis3=dict(domain=[0.04, 0.22], anchor="x3",
                showticklabels=False, range=[0, 1.2]),
    annotations=panel_header_annotations(),
)

slider_steps = [
    dict(method="animate",
         label=label.split(". ", 1)[-1],
         args=[[str(i)],
               dict(mode="immediate",
                    frame=dict(duration=0, redraw=True),
                    transition=dict(duration=0))])
    for i, (f, fs, label, caption) in enumerate(SCENARIOS)
]

fig.update_layout(
    sliders=[dict(
        active=0,
        currentvalue=dict(prefix="Scenario: ", font=dict(size=14)),
        pad=dict(t=30, b=10),
        steps=slider_steps,
        y=-0.04,
        len=0.95,
        x=0.025,
    )]
)


# ---------- Write to HTML ----------

OUT_PATH = Path(__file__).resolve().parent.parent / "widget" / "interactive.html"
OUT_PATH.parent.mkdir(exist_ok=True)
fig.write_html(
    str(OUT_PATH),
    include_plotlyjs="cdn",
    full_html=True,
    config=dict(displayModeBar=False),
)
print(f"Wrote: {OUT_PATH}")
print(f"Total scenarios: {len(SCENARIOS)}")
print(f"File size: {OUT_PATH.stat().st_size / 1024:.0f} KB")
