import csv
from collections import defaultdict
from pathlib import Path
from statistics import median

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Figure name -> (size in inches, panels); panel = (threads, commits), lettered (a), (b), ...
# Bars compare to the first commit at that thread count; no thread count draws scaling
FIGURES = {
    'opt1_to_opt4': ((3.72, 1.9), [(1, ['base', 'opt1', 'opt2', 'opt3', 'opt4'])]),
    'opt5_to_opt14': ((7, 1.7), [
        (1, ['opt4', 'opt5', 'opt6', 'opt7', 'opt8', 'opt9', 'opt10', 'opt11']),
        (None, ['opt9']),
        (32, ['opt9', 'opt10', 'opt11', 'opt12', 'opt13', 'opt14']),
    ]),
}
BENCHMARKS = {'diabetes': 'Diabetes', 'cancer': 'Cancer', 'housing': 'Housing',
              'silk-wave': 'Silk Waves', 'square-wave': 'Square Waves'}
COLORS = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6']
MARKERS = 'osD^v'
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'

plt.rcParams.update({
    'font.family': 'serif', 'font.serif': ['Linux Libertine O', 'STIXGeneral'],
    'font.size': 7.5, 'pdf.fonttype': 42,
    'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'text.color': INK,
    'xtick.color': INK2, 'ytick.color': INK2,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.grid': True, 'axes.axisbelow': True, 'axes.grid.axis': 'y',
    'grid.color': GRID, 'grid.linewidth': 0.5,
})

if __name__ == '__main__':
    runs = defaultdict(list)
    for row in csv.DictReader(Path('plots/data/times.csv').read_text().splitlines()):
        runs[row['commit'], row['benchmark'], int(row['threads'])].append(float(row['seconds']))
    secs = {key: median(vals) for key, vals in runs.items()}
    Path('plots/figures').mkdir(parents=True, exist_ok=True)
    for name, (size, panels) in FIGURES.items():
        fig, axs = plt.subplots(1, len(panels), figsize=size, squeeze=False,
                                layout='constrained' if len(panels) > 1 else None)
        for k, (ax, (threads, commits)) in enumerate(zip(axs.flat, panels)):
            if threads:
                # Commits that have no times yet are left out
                commits = [c for c in commits if (c, 'diabetes', threads) in secs]
                n = len(commits) - 1
                ncol = n if n <= 4 else (n + 1) // 2
                width = 0.8 / n
                # Draw in legend order so wrapped rows read left to right
                for i, commit in sorted(enumerate(commits[1:]), key=lambda ic: ic[0] % ncol):
                    xs, ys = [], []
                    for j, bench in enumerate(BENCHMARKS):
                        xs.append(j + (i - (n - 1) / 2) * width)
                        ys.append(secs[commits[0], bench, threads] / secs[commit, bench, threads])
                    bars = ax.bar(xs, ys, width, color=COLORS[i], edgecolor='white',
                                  linewidth=0.5, label=commit)
                    # Rotated value at each bar tip, last bar only when crowded
                    if n <= 4 or i == n - 1:
                        ax.bar_label(bars, fmt='%.1fx', rotation=90, padding=2, fontsize=7)
                ax.set_xlim(-0.5, len(BENCHMARKS) - 0.5)
                ax.set_xticks(range(len(BENCHMARKS)))
                ax.set_xticklabels([b.replace(' ', '\n') for b in BENCHMARKS.values()])
                ax.tick_params(axis='x', length=0, labelsize=7)
                ax.set_ylabel(f'Speedup over {commits[0]}'
                              + (f',\n{threads} threads' if threads > 1 else ''))
                ax.yaxis.set_major_locator(MaxNLocator(5, integer=True))
                ax.set_ylim(0, ax.get_ylim()[1] * 1.2)
            else:
                # One curve per benchmark, speedup over its own 1 thread
                ncol = 3
                ts = sorted({t for c, _, t in secs if c == commits[0]})
                for j, (bench, title) in enumerate(BENCHMARKS.items()):
                    ys = [secs[commits[0], bench, 1] / secs[commits[0], bench, t] for t in ts]
                    ax.plot(ts, ys, color=COLORS[j], marker=MARKERS[j], markersize=3.5,
                            linewidth=1, label=title)
                ax.plot([1, ts[-1]], [1, ts[-1]], color=INK2, linewidth=0.5, zorder=1,
                        label='Ideal')
                # Log2 axes make ideal scaling the diagonal
                ax.set_xscale('log', base=2)
                ax.set_yscale('log', base=2)
                ax.set_xticks(ts, ts)
                ax.set_yticks(ts, ts)
                ax.minorticks_off()
                ax.set_xlabel('Threads')
                ax.set_ylabel('Speedup over 1 thread')
            # Smaller text keeps the line legend within its panel
            ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=ncol,
                      frameon=False, handlelength=1, handletextpad=0.4, columnspacing=0.8,
                      fontsize=None if threads else 6.5)
            if len(panels) > 1:
                # Letter beside the first legend row
                ax.annotate(f'({chr(97 + k)})', (0, 1), xycoords='axes fraction', xytext=(-2, 11),
                            textcoords='offset points', ha='right', va='center', weight='bold')
        # Constrained layout keeps the full size, so only a lone panel is cropped
        fig.savefig(f'plots/figures/{name}.pdf', bbox_inches=None if len(panels) > 1 else 'tight',
                    pad_inches=0.02)
