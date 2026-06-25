import numpy as np
import matplotlib.artist as martist
import matplotlib.lines as mlines
import matplotlib.text as mtext
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms
from matplotlib.axes import Axes

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


# def superimpose_axis(ax, positions, labels=None, axis='x', side='positive',
#                      color='k', tick_size=5, label_pad=4, fontsize=9, rotation=0,
#                      limits=None):
#     labels = labels or [f'{p:g}' for p in positions]
#     phi = rotation
#     if axis == 'x':
#         ax_dir   = np.array([ np.cos(phi),  np.sin(phi)])
#         tick_dir = np.array([-np.sin(phi),  np.cos(phi)])
#     else:
#         ax_dir   = np.array([-np.sin(phi),  np.cos(phi)])
#         tick_dir = np.array([ np.cos(phi),  np.sin(phi)])

#     sign = 1 if side == 'positive' else -1
#     tick_dir = sign * tick_dir

#     inv      = ax.transData.inverted()
#     origin_d = ax.transData.transform([0.0, 0.0])
#     tick_d   = ax.transData.transform(tick_dir) - origin_d
#     tick_d  /= np.linalg.norm(tick_d)
#     tick_vec = inv.transform(origin_d + tick_d) - inv.transform(origin_d)

#     ha = 'left'   if tick_vec[0] > 0 else ('right'  if tick_vec[0] < 0 else 'center')
#     va = 'bottom' if tick_vec[1] > 0 else ('top'    if tick_vec[1] < 0 else 'center')

#     if limits is not None:
#         p1, p2 = limits[0] * ax_dir, limits[1] * ax_dir
#         ann = ax.annotate('', xy=p2, xytext=p1,
#                           arrowprops=dict(arrowstyle='->', color=color, lw=0.8,
#                                           shrinkA=0, shrinkB=0),
#                           annotation_clip=False)
#         ann.arrow_patch.set_clip_on(False)

#     for pos, lbl in zip(positions, labels):
#         c  = pos * ax_dir
#         t  = c + tick_size * tick_vec
#         ax.plot([c[0], t[0]], [c[1], t[1]], color=color, lw=0.8, clip_on=False)
#         lp = c + (tick_size + label_pad) * tick_vec
#         ax.text(lp[0], lp[1], lbl, ha=ha, va=va, color=color, fontsize=fontsize)


# def superimpose_axis(ax, positions, labels=None, axis='x', side='positive',
#                      color='k', tick_size=5, label_pad=4, fontsize=9, rotation=0,
#                      limits=None):
#     labels = labels or [f'{p:g}' for p in positions]
#     phi = rotation
#     if axis == 'x':
#         ax_dir   = np.array([ np.cos(phi),  np.sin(phi)])
#         tick_dir = np.array([-np.sin(phi),  np.cos(phi)])
#     else:
#         ax_dir   = np.array([-np.sin(phi),  np.cos(phi)])
#         tick_dir = np.array([ np.cos(phi),  np.sin(phi)])

#     sign = 1 if side == 'positive' else -1
#     tick_dir = sign * tick_dir

#     # convert tick_dir to a vector of length tick_size in pixels
#     inv      = ax.transData.inverted()
#     origin_d = ax.transData.transform([0.0, 0.0])
#     tick_d   = ax.transData.transform(tick_dir) - origin_d
#     tick_d  /= np.linalg.norm(tick_d)                              # 1 px unit vector
#     tick_vec = inv.transform(origin_d + tick_d) - inv.transform(origin_d)  # in data coords

#     ha = 'left'   if tick_d[0] > 0 else ('right'  if tick_d[0] < 0 else 'center')
#     va = 'bottom' if tick_d[1] < 0 else ('top'    if tick_d[1] > 0 else 'center')

#     if limits is not None:
#         p1, p2 = limits[0] * ax_dir, limits[1] * ax_dir
#         ann = ax.annotate('', xy=p2, xytext=p1,
#                           arrowprops=dict(arrowstyle='->', color=color, lw=0.8,
#                                           shrinkA=0, shrinkB=0),
#                           annotation_clip=False)
#         ann.arrow_patch.set_clip_on(False)

#     for pos, lbl in zip(positions, labels):
#         c = pos * ax_dir
#         t = c + tick_size * tick_vec
#         ax.plot([c[0], t[0]], [c[1], t[1]], color=color, lw=0.8, clip_on=False)
#         lp = c + (tick_size + label_pad) * tick_vec
#         ax.text(lp[0], lp[1], lbl, ha=ha, va=va, color=color, fontsize=fontsize)


# def superimpose_axis(ax, positions, labels=None, axis='x', side='positive',
#                      color='k', tick_size=5, label_pad=4, fontsize=9, rotation=0,
#                      limits=None):
#     labels = labels or [f'{p:g}' for p in positions]
#     phi = rotation
#     if axis == 'x':
#         ax_dir = np.array([ np.cos(phi),  np.sin(phi)])
#     else:
#         ax_dir = np.array([-np.sin(phi),  np.cos(phi)])

#     # perpendicular in display space (pixels)
#     inv = ax.transData.inverted()
#     origin_d = ax.transData.transform([0.0, 0.0])
#     ax_dir_d = ax.transData.transform(ax_dir) - origin_d
#     ax_dir_d /= np.linalg.norm(ax_dir_d)
#     sign = 1 if side == 'positive' else -1
#     perp_d = sign * np.array([-ax_dir_d[1], ax_dir_d[0]])  # screen-space perpendicular

#     if limits is not None:
#         p1, p2 = limits[0] * ax_dir, limits[1] * ax_dir
#         ann = ax.annotate('', xy=p2, xytext=p1,
#                           arrowprops=dict(arrowstyle='->', color=color, lw=0.8,
#                                           shrinkA=0, shrinkB=0),
#                           annotation_clip=False)
#         ann.arrow_patch.set_clip_on(False)

#     for pos, lbl in zip(positions, labels):
#         c   = pos * ax_dir
#         c_d = ax.transData.transform(c)
#         t   = inv.transform(c_d + tick_size * perp_d)
#         ax.plot([c[0], t[0]], [c[1], t[1]], color=color, lw=0.8, clip_on=False)
#         lp  = inv.transform(c_d + (tick_size + label_pad) * perp_d)
#         ha  = 'left'   if perp_d[0] > 0 else ('right'  if perp_d[0] < 0 else 'center')
#         va  = 'bottom' if perp_d[1] > 0 else ('top'    if perp_d[1] < 0 else 'center')
#         ax.text(lp[0], lp[1], lbl, ha=ha, va=va, color=color, fontsize=fontsize)


# def superimpose_axis(ax: Axes, positions, labels=None, axis='x', side='positive',
#                      color='k', tick_size=0.15, fontsize=9, rotation=0.0,
#                      limits=None):
#     labels = labels or [f'{p:g}' for p in positions]
#     phi = rotation
#     if axis == 'x':
#         ax_dir = np.array([ np.cos(phi),  np.sin(phi)])
#         perp   = np.array([-np.sin(phi),  np.cos(phi)])
#     else:
#         ax_dir = np.array([-np.sin(phi),  np.cos(phi)])
#         perp   = np.array([ np.cos(phi),  np.sin(phi)])

#     sign = 1 if side == 'positive' else -1
#     dp = sign * perp

#     if limits is not None:
#         p1, p2 = limits[0] * ax_dir, limits[1] * ax_dir
#         ann = ax.annotate('', xy=p2, xytext=p1,
#                   arrowprops=dict(arrowstyle='<->', color=color, lw=0.8, shrinkA=0, shrinkB=0),
#                   annotation_clip=False)
#         ann.arrow_patch.set_clip_on(False)

#     for pos, lbl in zip(positions, labels):
#         c  = pos * ax_dir
#         t  = c + tick_size * dp
#         ax.plot([c[0], t[0]], [c[1], t[1]], color=color, lw=0.8, clip_on=False)
#         lp = c + 1.8 * tick_size * dp
#         ha = 'left' if dp[0] > 0 else ('right' if dp[0] < 0 else 'center')
#         va = 'bottom' if dp[1] > 0 else ('top'  if dp[1] < 0 else 'center')
#         ax.text(lp[0], lp[1], lbl, ha=ha, va=va, color=color, fontsize=fontsize)