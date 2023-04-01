# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 14:45:24 2023

@author: sergi
"""


import os
import sys
import pandas as pd
import numpy as np
from scipy.stats import entropy
#%matplotlib qt
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
        self.num_points = None
        self.sorting_order = None
        self.decimals = None
        self.slices_entropy = {'x': None, 'y': None, 'z': None}
        self.grid_dim = None
        self.are_int = False
        if points is not None:
            self.points = points
            self._update()
        if file is not None:
            self.load(file)
            self._update()

        
    def __str__(self):
        s = 'Point cloud with ' + str(self.num_points) + \
        ' points in a grid of shape ' + str(self.grid_dim)
        if self.sorting_order is not None:
            s += ' sorted by the order ' + str(self.sorting_order[0]) + ', ' 
            str(self.sorting_order[1]) + ', ' + str(self.sorting_order[2])
        return s
    
    def __repr__(self):
        return self.__str__()
    
    def _remove_duplicates(self):
        indexes = np.unique(self.points, return_index=True, axis=0)[1]
        self.points = np.array([self.points[index] for index in sorted(indexes)])
        
    def _compute_binary_entropy_by_slice(self, axis):
        if not self.are_int:
            return

        if axis == 'x':
            n = self.grid_dim[1] * self.grid_dim[2]
            ax = 0
        elif axis == 'y':
            n = self.grid_dim[0] * self.grid_dim[2]
            ax = 1
        elif axis == 'z':
            n = self.grid_dim[0] * self.grid_dim[1]
            ax = 2

        entropies = []
        
        unique, counts = np.unique(self.points[:, ax], return_counts=True)
        
        counts_dict = dict(zip(unique, counts))
        
        prev = 0
        for i, (s, c) in enumerate(counts_dict.items()):
            if i != 0:
                prev = unique[i - 1]
            for _ in range(int(prev + 1), s):
                entropies.append(0)
            p1 = c / n
            entropies.append(calculate_binary_entropy(p1))

        self.slices_entropy[axis] = entropies
            
    def _update(self):
        self.num_points = self.points.shape[0]
        self.grid_dim = np.array([self.points[:, i].max() + 1 for i in range(3)])
        self.decimals = get_decimal_positions(self.points)
        for axis in 'xyz':
            self._compute_binary_entropy_by_slice(axis)
            
    def sort_by_coords(self, order='xyz', points=None):
        other = True
        if points is None:
            points = self.points
            other = False
        d = {'x':0, 'y':1, 'z':2}
        order_list = [d[x] for x in order]
        indices = np.lexsort((points[:, order_list[2]],
                              points[:, order_list[1]],
                              points[:, order_list[0]]))
        points = points[indices]
        if other:
            return points
        else:
            self.sorting_order = order
    
        
    def preprocess(self, decimals=None, sorting_order=None):
        self.are_int = True
        
        if decimals is None:
            decimals = self.decimals
        if sorting_order is not None:
            self.sort_by_coords(sorting_order)

        self._remove_duplicates()

        self.points *= 10 ** decimals
        for i in range(self.points.shape[1]):
            self.points[:,i] -= self.points[:,i].min()
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
                
    def plot(self):
        #skip = 100   # Skip every n points

        fig = plt.figure()
        figure(figsize=(1, 1))
        ax = fig.add_subplot(111, projection='3d')
        #point_range = range(0, points.shape[0], 10000) # skip points to prevent crash
        ax.scatter(self.points[:, 0],   # x
                   self.points[:, 1],   # y
                   self.points[:, 2],   # z
                   #c=points[point_range, 2], # height data for color
                   cmap='spectral',
                   marker=".")
        #ax.axis('scaled')  # {equal, scaled}
        plt.show()
        
        
class MultiplePointClouds():
    
    def __init__(self, folder=None):
        self.point_clouds = None
        self.points = None
        self.num_point_clouds = None
        self.files = None
        if folder is not None:
            self.load(folder)
        
    def __str__(self):
        return str(self.num_point_clouds) + 'point clouds'

    def __repr__(self):
        return self.__str__()

    def preprocess(self, decimals=None, sorting_order=None):
        for pc in self.point_clouds:
            pc.preprocess(decimals, sorting_order)
    
    def load(self, folder):
        if folder[-1] != '/':
            folder += '/'
        self.files = os.listdir(folder)
        self.point_clouds = []
        for f in self.files:
            self.point_clouds.append(PointCloud(file=folder+f))
        self.num_point_clouds = len(self.files)
        
    def save(self, folder, preprocess=True, decimals=None, sorting_order=None):
        if folder[-1] != '/':
            folder += '/'
        digits = int(np.log10(self.num_point_clouds)) + 1
        
        for i, pc in enumerate(self.point_clouds):
            if preprocess:
                pc.preprocess(decimals, sorting_order)
            out = 'file' + '0'*(digits - int(np.log10(i+1)) - 1) + str(i+1) + '.ply'
            pc.save(folder+out, preprocess=True, decimals=None, sorting_order=None)
            
    def plot(self, create=True):
        if create:
            self._points = self.point_clouds[0].points
            for pc in self.point_clouds[1:]:
                self._points = np.append(self._points, pc.points, axis=0)
            self._point_cloud = PointCloud(points=self._points)
        self._point_cloud.plot()
        


if __name__ == '__main__':
    
    #pc = PointCloud(file='pc.pts')
    #pc.save('pc.ply', sorting_order='zyx')
    
    mpc = MultiplePointClouds('pc')
    mpc.save('ply')
