import numpy as np
import matplotlib.artist as martist
import matplotlib.lines as mlines
import matplotlib.text as mtext
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms
from matplotlib.axes import Axes
from matplotlib import pyplot as plt
import shutil
import matplotlib

matplotlib.rcParams['text.usetex'] = shutil.which('latex') is not None
# matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amssymb}'
# matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amssymb}\usepackage{cmbright}'
matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}\usepackage{newtxtext}\usepackage{newtxmath}'
matplotlib.rcParams['figure.dpi'] = 200

plot = Axes.plot
scatter = Axes.scatter
axvline = Axes.axvline

CM = 1 / 2.54
SLIDE_FIG_DIMS = np.array([32*CM, 14.17*CM])
MPL_DEFAULT_DIMS = np.array([6.4, 4.8])

def cols_from_xlabels(xlabels: np.ndarray) -> int:
    if xlabels.ndim == 2:
        return xlabels.shape[1]
    elif xlabels.ndim == 1:
        return len(xlabels)
    elif xlabels.ndim == 0:
        return 1
    else:
        raise ValueError('invalid number of dimensions of xlabels')

def rows_from_ylabels(ylabels: np.ndarray) -> int:
    if ylabels.ndim == 2:
        return ylabels.shape[0]
    elif ylabels.ndim == 1:
        return len(ylabels)
    elif ylabels.ndim == 0:
        return 1
    else:
        raise ValueError('invalid number of dimensions of ylabels')

def xlabel(xlabels: np.ndarray, i: int, j: int, rows: int, cols: int) -> str | None:
    if xlabels.ndim == 2:
        return xlabels[i][j]
    elif xlabels.ndim == 1 and len(xlabels) == cols and i==rows-1:
        return xlabels[j]
    elif xlabels.ndim == 1 and len(xlabels) == rows != cols:
        return xlabels[i]
    elif xlabels.ndim == 0 and i==rows-1:
        return xlabels.item()
    else:
        return None

def ylabel(ylabels: np.ndarray, i: int, j: int, rows: int, cols: int) -> str | None:
    if ylabels.ndim == 2:
        return ylabels[i][j]
    elif ylabels.ndim == 1 and len(ylabels) == rows and j==0:
        return ylabels[i]
    elif ylabels.ndim == 1 and len(ylabels) == cols != rows:
        return ylabels[j]
    elif ylabels.ndim == 0 and j==0:
        return ylabels.item()
    else:
        return None

def subplotgrid(xlabels=None, ylabels=None, intitles=None, rows=None, cols=None, *,
                figsize=None, subplotsize=(4, 4), tight_layout=True, sharex=True, sharey=True,
                xlims=None, ylims=None, xmargins=0, ymargins=None,
                squeeze=True):
    """Opinionated wrapper around matplotlib's subplots that allows for a more declarative
    style of figure creation.

    Parameters
    ----------

    xlabels: array_like, default is None
        x-axes labels,
        applied per grid cell if shape is (rows, cols),
        to last row if shape == (cols),
        to each row if shape == (rows) != (cols),
        to last row in all columns if scalar or 0d array,
        used to infer number of grid columns if cols is None
    """
    xlabels = np.asarray(xlabels)
    ylabels = np.asarray(ylabels)
    if intitles is not None:
        intitles = np.atleast_2d(intitles)
        rows, cols = intitles.shape
    rows = rows if rows is not None else rows_from_ylabels(ylabels)
    cols = cols if cols is not None else cols_from_xlabels(xlabels)

    if rows is None or cols is None:
        raise ValueError('cannot infer number of rows and columns')

    if figsize is None and subplotsize is not None:
        figsize = (subplotsize[0]*cols, subplotsize[1]*rows)
    
    fig, ax = plt.subplots(rows, cols, figsize=figsize, # type: ignore
                           sharex=sharex, sharey=sharey, tight_layout=tight_layout,
                           squeeze=False) 
    
    for i, j in np.ndindex(rows, cols):
        if (label := ylabel(ylabels, i, j, rows, cols)) is not None:
            ax[i][j].set_ylabel(label)
        if (label := xlabel(xlabels, i, j, rows, cols)) is not None:
            ax[i][j].set_xlabel(label)

        if intitles is not None: 
            ax[i][j].text(0.01, 0.99, intitles[i][j], transform=ax[i][j].transAxes, verticalalignment='top')
        if xmargins is not None:
            ax[i][j].set_xmargin(xmargins)
        if ymargins is not None:
            ax[i][j].set_ymargin(ymargins)
        if xlims is not None:
            ax[i][j].set_xlim(xlims)
        if ylims is not None:
            ax[i][j].set_ylim(ylims)
    
    if squeeze:
        ax = ax.item() if ax.size == 1 else np.squeeze(ax)

    return fig, ax

def apply(method, objs, *args, **kwargs):
    """
    Calls method on each element of array obs with provided arguments. Useful for
    plotting consistently on an axes array.
    """
    from itertools import repeat
    def _iter(a):
        a = np.asarray(a)
        if a.shape[:objs.ndim] == objs.shape:
            return (a[idx] for idx in np.ndindex(objs.shape))
        return repeat(a.item() if a.ndim == 0 else a)

    kw_iters = {k: _iter(v) for k, v in kwargs.items()}
    for vals in zip(objs.flat, *[_iter(a) for a in args]):
        method(*vals, **{k: next(it) for k, it in kw_iters.items()})

    # from itertools import repeat
    # def _iter(a):
    #     a = np.asarray(a)
    #     if a.shape[:objs.ndim] == objs.shape:
    #         return (a[idx] for idx in np.ndindex(objs.shape))
    #     return repeat(a)
    # for vals in zip(objs.flat, *[_iter(a) for a in args]):
    #     method(*vals, **kwargs)

def centre_spines(ax: Axes):
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_position('zero')
    for spine in ['right', 'top']:
        ax.spines[spine].set_visible(False)
    ax.xaxis.set_major_formatter(lambda x, pos: '' if x == 0 else f'{x:g}')
    ax.yaxis.set_major_formatter(lambda x, pos: '' if x == 0 else f'{x:g}')

Axes.centre_spines = centre_spines

class SuperimposedAxis(martist.Artist):

    def __init__(self, ax, positions, labels=None, axis='x', side='positive',
                 color='k', tick_size=5, label_pad=4, fontsize=9, rotation=0,
                 limits=None):
        super().__init__()
        self._positions = list(positions)
        self._labels    = list(labels) if labels is not None else [f'{p:g}' for p in positions]
        self._axis      = axis
        self._side      = side
        self._color     = color
        self._tick_size = tick_size
        self._label_pad = label_pad
        self._fontsize  = fontsize
        self._rotation  = rotation
        self._limits    = limits

        self.axes = ax
        self.set_figure(ax.get_figure())

        trans = ax.transData
        self._tick_lines = [
            mlines.Line2D([], [], color=color, lw=0.8, transform=trans, clip_on=False)
            for _ in self._positions
        ]
        self._tick_labels = [
            mtext.Text(0, 0, str(lbl), color=color, fontsize=fontsize, transform=trans)
            for lbl in self._labels
        ]
        self._arrow = None
        if limits is not None:
            self._arrow = mpatches.FancyArrowPatch(
                posA=(0, 0), posB=(1, 1), arrowstyle='->',
                color=color, lw=0.8, shrinkA=0, shrinkB=0,
                transform=trans, clip_on=False
            )
        for child in self.get_children():
            child.set_figure(ax.get_figure())

    def get_children(self):
        children = self._tick_lines + self._tick_labels
        return children + [self._arrow] if self._arrow is not None else children

    def _update_children(self):
        phi = self._rotation
        if self._axis == 'x':
            ax_dir   = np.array([ np.cos(phi),  np.sin(phi)])
            tick_dir = np.array([-np.sin(phi),  np.cos(phi)])
        else:
            ax_dir   = np.array([-np.sin(phi),  np.cos(phi)])
            tick_dir = np.array([ np.cos(phi),  np.sin(phi)])

        sign     = 1 if self._side == 'positive' else -1
        tick_dir = sign * tick_dir

        trans    = self.axes.transData
        inv      = trans.inverted()
        origin_d = trans.transform([0.0, 0.0])
        tick_d   = trans.transform(tick_dir) - origin_d
        tick_d  /= np.linalg.norm(tick_d)
        tick_vec = inv.transform(origin_d + tick_d) - inv.transform(origin_d)

        ha = 'left'   if tick_vec[0] > 0 else ('right'  if tick_vec[0] < 0 else 'center')
        va = 'bottom' if tick_vec[1] > 0 else ('top'    if tick_vec[1] < 0 else 'center')

        if self._arrow is not None:
            self._arrow.set_positions(tuple(self._limits[0] * ax_dir),
                                       tuple(self._limits[1] * ax_dir))

        for line, text, pos in zip(self._tick_lines, self._tick_labels, self._positions):
            c  = pos * ax_dir
            t  = c + self._tick_size * tick_vec
            lp = c + (self._tick_size + self._label_pad) * tick_vec
            line.set_data([c[0], t[0]], [c[1], t[1]])
            text.set_position((lp[0], lp[1]))
            text.set_ha(ha)
            text.set_va(va)

    def draw(self, renderer):
        if not self.get_visible():
            return
        self._update_children()
        if self._arrow is not None:
            self._arrow.draw(renderer)
        for line, text in zip(self._tick_lines, self._tick_labels):
            line.draw(renderer)
            text.draw(renderer)

    def get_window_extent(self, renderer=None):
        if renderer is None:
            renderer = self.figure.canvas.get_renderer()
        self._update_children()
        bboxes = (  [l.get_window_extent(renderer) for l in self._tick_lines]
                  + [t.get_window_extent(renderer) for t in self._tick_labels])
        if self._arrow is not None:
            bboxes.append(self._arrow.get_window_extent(renderer))
        return mtransforms.Bbox.union(bboxes) if bboxes else mtransforms.Bbox.null()


def superimpose_axis(ax, positions, labels=None, **kwargs):
    artist = SuperimposedAxis(ax, positions, labels, **kwargs)
    ax.add_artist(artist)
    return artist

Axes.superimpose_axis = superimpose_axis

def plotf(ax, f, a, b, res=200, **kwargs):
    xs = np.linspace(a, b, res)
    ax.plot(xs, f(xs), **kwargs)

def histo(ax, y, bins=None, range=None):
    """Plots histogram density with correct normalisation by overall
    number of data points (instead of only number of datapoints falling into
    range as in matplotlib.pyplot.histo)
    """
    bins = bins if bins is not None else int((np.log2(len(y))))
    counts, edges = np.histogram(y, bins=bins, range=range)
    ax.stairs(counts / (len(y) * (edges[1] - edges[0])), edges, fill=True)

def plot_pmf(ax, x, pmf):
    p = pmf(x)
    ax.vlines(x, 0, p, colors='k', linestyles='--')
    ax.scatter(x, p, facecolors='white', linewidths=1.5, edgecolors='k', zorder=3)

def histo_int(ax, y, a=None, b=None, width=0.6, pmf=None):
    """Plots a histogram for integer data with bins that are centred around the 
    corresponding integer value and an optional pmf overlay.
    """
    y = np.asarray(y)
    a = a if a is not None else y.min()
    b = b if b is not None else y.max()
    counts, _ = np.histogram(y, bins=np.arange(a - 0.5, b + 1.5))
    ax.bar(np.arange(a, b + 1), counts / len(y), width=width)
    if pmf is not None: plot_pmf(ax, np.arange(a, b + 1), pmf)

# def histo_1d(ax, y, pmf=None):
#     x = np.arange(y.min(), y.max()+1)
#     ax.hist(y, np.arange(y.min() - 0.5, y.max() + 1.5), density=True, align='mid')
#     if pmf is not None: plot_pmf(ax, x, pmf)
#     ax.set_ylim(ax.get_ylim()*np.array([0, 1.01]))
#     ax.margins(x=0)
#     ax.set_xlabel('$x$')
#     ax.set_ylabel(r'$|\{i: x_i = x\}|/n$')

