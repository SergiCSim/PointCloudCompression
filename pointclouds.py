# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 14:45:24 2023

@author: sergi
"""


import os
import sys
import pandas as pd
import numpy as np


def get_decimal_positions(array):

    decimals, _ = np.modf(array)
    
    # Convert decimal parts to strings
    decimal_strings = np.char.mod('%f', decimals).reshape((1, -1))[0]
    
    # Count the number of non-zero decimal places for each number
    num_decimals = [len(s.rstrip('0').split('.')[1]) for s in decimal_strings]
    
    # Return the maximum number of decimal places
    return max(num_decimals)


class PointCloud():
    
    def __init__(self, file=None):
        self.num_points = None
        self.sorting_order = None
        self.decimals = None
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
            
    def _update(self):
        self.num_points = self.points.shape[0]
        self.grid_dim = np.array([self.points[:, i].max() for i in range(3)])
        self.decimals = get_decimal_positions(self.points)
            
    def sort_by_coords(self, order='xyz'):
        d = {'x':0, 'y':1, 'z':2}
        order_list = [d[x] for x in order]
        indices = np.lexsort((self.points[:, order_list[2]],
                              self.points[:, order_list[1]],
                              self.points[:, order_list[0]]))
        self.points = self.points[indices]
        self.sorting_order = order
    
    def load(self, file):
        df = pd.read_csv(file, delimiter=' ', header=None)
        self.points = np.array(df)[:, 0:3]
        self._update()
        
    def preprocess(self, decimals=None, sorting_order=None):
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
        


if __name__ == '__main__':
    
    pc = PointCloud('pc.pts')
    pc.save('pc.ply')
    
