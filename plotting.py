import numpy as np
from matplotlib.axes import Axes

def centre_spines(ax: Axes):
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_position('zero')
    for spine in ['right', 'top']:
        ax.spines[spine].set_visible(False)
    ax.xaxis.set_major_formatter(lambda x, pos: '' if x == 0 else f'{x:g}')
    ax.yaxis.set_major_formatter(lambda x, pos: '' if x == 0 else f'{x:g}')

def superimpose_axis(ax, positions, labels=None, axis='x', side='positive',
                     color='k', tick_size=5, label_pad=4, fontsize=9, rotation=0,
                     limits=None):
    labels = labels or [f'{p:g}' for p in positions]
    phi = rotation
    if axis == 'x':
        ax_dir   = np.array([ np.cos(phi),  np.sin(phi)])
        tick_dir = np.array([-np.sin(phi),  np.cos(phi)])
    else:
        ax_dir   = np.array([-np.sin(phi),  np.cos(phi)])
        tick_dir = np.array([ np.cos(phi),  np.sin(phi)])

    sign = 1 if side == 'positive' else -1
    tick_dir = sign * tick_dir

    inv      = ax.transData.inverted()
    origin_d = ax.transData.transform([0.0, 0.0])
    tick_d   = ax.transData.transform(tick_dir) - origin_d
    tick_d  /= np.linalg.norm(tick_d)
    tick_vec = inv.transform(origin_d + tick_d) - inv.transform(origin_d)

    ha = 'left'   if tick_vec[0] > 0 else ('right'  if tick_vec[0] < 0 else 'center')
    va = 'bottom' if tick_vec[1] > 0 else ('top'    if tick_vec[1] < 0 else 'center')

    if limits is not None:
        p1, p2 = limits[0] * ax_dir, limits[1] * ax_dir
        ann = ax.annotate('', xy=p2, xytext=p1,
                          arrowprops=dict(arrowstyle='->', color=color, lw=0.8,
                                          shrinkA=0, shrinkB=0),
                          annotation_clip=False)
        ann.arrow_patch.set_clip_on(False)

    for pos, lbl in zip(positions, labels):
        c  = pos * ax_dir
        t  = c + tick_size * tick_vec
        ax.plot([c[0], t[0]], [c[1], t[1]], color=color, lw=0.8, clip_on=False)
        lp = c + (tick_size + label_pad) * tick_vec
        ax.text(lp[0], lp[1], lbl, ha=ha, va=va, color=color, fontsize=fontsize)


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