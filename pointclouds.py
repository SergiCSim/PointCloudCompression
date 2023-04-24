# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 14:45:24 2023

@author: sergi
"""


import os
import sys
import pandas as pd
import numpy as np
# %matplotlib qt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.pyplot import figure


def get_decimal_positions(array):

    decimals, _ = np.modf(array)

    # Convert decimal parts to strings
    decimal_strings = np.char.mod('%f', decimals).reshape((1, -1))[0]

    # Count the number of non-zero decimal places for each number
    num_decimals = [len(s.rstrip('0').split('.')[1]) for s in decimal_strings]

    # Return the maximum number of decimal places
    return max(num_decimals)


def calculate_binary_entropy(p1):
    if p1 == 0 or p1 == 1:
        return 0
    p0 = 1 - p1
    return - (p0 * np.log2(p0) + p1 * np.log2(p1))


class PointCloud():

    def __init__(self, points=None, file=None):
        if type(points) is str:
            file = points
            points = None
        self.num_points = None
        self.num_empty_slices = None
        self.sorting_order = None
        self.decimals = None

        d = {'x': None, 'y': None, 'z': None}
        self.points_per_slice = d.copy()
        self.sr_per_slice = d.copy()
        self.sr_3d = [None, None, None]
        self.entropy_per_slice = d.copy()
        self.sr_entropy_per_slice = d.copy()

        self.are_int = False

        if points is not None:
            self.points = points
            self._update()
        if file is not None:
            self.load(file)
            # self._update()

    def __str__(self):
        return 'Point cloud with ' + str(self.num_points) + ' points'

    def __repr__(self):
        return self.__str__()

    def _remove_duplicates(self):
        indexes = np.unique(self.points, return_index=True, axis=0)[1]
        self.points = np.array([self.points[index]
                               for index in sorted(indexes)])

    def _update(self):
        self.num_points = self.points.shape[0]

    def sort_by_coords(self, order='xyz', points=None):
        other = True
        if points is None:
            points = self.points
            other = False
        d = {'x': 0, 'y': 1, 'z': 2}
        order_list = [d[x] for x in order]
        indices = np.lexsort((points[:, order_list[2]],
                              points[:, order_list[1]],
                              points[:, order_list[0]]))
        points = points[indices]
        if other:
            return points
        else:
            self.sorting_order = order

    def compute_axis_stats(self, axis):
        if not self.are_int:
            return

        for j in range(self.points.shape[1]):
            self.sr_3d[j] = int(self.points[:, j].max())

        self.points_per_slice[axis] = []
        self.sr_per_slice[axis] = []
        self.entropy_per_slice[axis] = []
        self.sr_entropy_per_slice[axis] = []

        d = {'x': 0, 'y': 1, 'z': 2}
        ax = d[axis]
        ax_w, ax_h = [ax for ax in d.values() if ax != d[axis]]

        n = (self.sr_3d[ax_w] + 1) * (self.sr_3d[ax_h] + 1)
        
        self.num_empty_slices = 0

        # For each slice:
        for s in range(self.sr_3d[ax] + 1):

            # Select the points of the slice s
            points = self.points[self.points[:, ax] == s]

            num_points = points.shape[0]
            self.points_per_slice[axis].append(num_points)
            
            if num_points == 0:
                sr = ((np.nan, np.nan), (np.nan, np.nan))
                self.sr_per_slice[axis].append(sr)
                self.entropy_per_slice[axis].append(0)
                self.sr_entropy_per_slice[axis].append(0)
                self.num_empty_slices += 1
            else:
                sr = ((int(points[:, ax_w].min()), int(points[:, ax_h].min())),
                      (int(points[:, ax_w].max()), int(points[:, ax_h].max())))
                self.sr_per_slice[axis].append(sr)

                n_slice = (sr[1][0] - sr[0][0] + 1) * (sr[1][1] - sr[0][1] + 1)

                entropy = calculate_binary_entropy(num_points / n)
                self.entropy_per_slice[axis].append(entropy)

                sr_entropy = calculate_binary_entropy(num_points / n_slice)
                self.sr_entropy_per_slice[axis].append(sr_entropy)

        self.points_per_slice[axis] = np.array(self.points_per_slice[axis])
        self.sr_per_slice[axis] = np.array(self.sr_per_slice[axis])
        self.entropy_per_slice[axis] = np.array(self.entropy_per_slice[axis])
        self.sr_entropy_per_slice[axis] = np.array(self.sr_entropy_per_slice[axis])

    def preprocess(self, decimals=None, sorting_order=None):
        self.are_int = True

        if decimals is None:
            decimals = get_decimal_positions(self.points)
        if sorting_order is not None:
            self.sort_by_coords(sorting_order)

        self._remove_duplicates()

        self.points *= 10 ** decimals
        for j in range(self.points.shape[1]):
            self.points[:, j] -= self.points[:, j].min()
        #points -= points.min()
        self.points = np.array(self.points, np.uint64)

        self._update()

    def load(self, file):
        df = pd.read_csv(file, delimiter=' ', header=None)
        self.points = np.array(df)[:, 0:3]
        self._update()

    def save(self, file, preprocess=True, decimals=None, sorting_order=None):
        if preprocess:
            self.preprocess(decimals, sorting_order)

        if '.ply' in file:
            header = 'ply\nformat ascii 1.0\nelement vertex ' + \
                str(self.num_points) + \
                '\nproperty float x\nproperty float y\nproperty float z\n' + \
                'end_header\n'

            with open(file, 'w') as f:
                f.write(header)
                np.savetxt(f, self.points, delimiter=' ', fmt='%d %d %d')

    def plot(self, skip=1):
        # skip = 100   # Skip every n points

        fig = plt.figure()
        figure(figsize=(1, 1))
        ax = fig.add_subplot(111, projection='3d')
        # skip points to prevent crash
        point_range = range(0, self.points.shape[0], skip)
        ax.scatter(self.points[point_range, 0],   # x
                   self.points[point_range, 1],   # y
                   self.points[point_range, 2],   # z
                   # c=points[point_range, 2], # height data for color
                   cmap='spectral',
                   marker=".")
        # ax.axis('scaled')  # {equal, scaled}
        plt.show()

    def get_info(self, df=True):
        for axis in 'xyz':
            self.compute_axis_stats(axis)

        info_num_points = []
        info_sr = []
        info_entropy = []
        info_sr_entropy = []

        for axis in 'xyz':
            info_num_points += [self.points_per_slice[axis].min(),
                                self.points_per_slice[axis].max(),
                                self.points_per_slice[axis].mean(),
                                np.median(self.points_per_slice[axis])]
            info_entropy += [self.entropy_per_slice[axis].min(),
                             self.entropy_per_slice[axis].max(),
                             self.entropy_per_slice[axis].mean()]
            info_sr_entropy += [self.sr_entropy_per_slice[axis].min(),
                                self.sr_entropy_per_slice[axis].max(),
                                self.sr_entropy_per_slice[axis].mean()]
            xb = self.sr_per_slice[axis][:, 0, 0]
            yb = self.sr_per_slice[axis][:, 0, 1]
            xt = self.sr_per_slice[axis][:, 1, 0]
            yt = self.sr_per_slice[axis][:, 1, 1]
            arrays = [xb, yb, xt, yt]
            for a in arrays:
                b = a[np.invert(np.isnan(a))]
                info_sr += [b.min(), b.max(), b.mean(), np.median(b)]

        info = [self.sr_3d] + \
            info_num_points + \
            info_sr + \
            info_entropy + \
            info_sr_entropy

        if not df:
            return info

        stats = ['min', 'max', 'mean', 'median']
        names = ['Ocup. voxels', 'Bottom hor.', 'Bottom vert.', 'Top  hor.',
                 'Top vert.', 'Entropy', 'SR entropy']

        colnames = ['3D SR (range)']
        for n in names:
            for axis in 'xyz':
                for s in stats:
                    if not ((n == 'Entropy' or n == 'SR entropy') and
                            s == 'median'):
                        colnames.append(n + ' ' + axis + ' (' + s + ')')

        dataframe = pd.DataFrame(columns=colnames)
        return dataframe.append(pd.DataFrame([info], columns=colnames))


if __name__ == '__main__':

    path = '../ShapeNet/shapenetcore_partanno_v0/PartAnnotation/02691156/points/'
    pc_path = path + '1a04e3eab45ca15dd86060f189eb133.pts'

    pc = PointCloud(pc_path)
    pc.preprocess(decimals=5)
    
    print(pc.get_info())

    