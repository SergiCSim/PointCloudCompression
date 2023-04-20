import os
import sys
import argparse
import pandas as pd
import numpy as np
#import open3d as o3d

def print_perc(x):
    if x < 10:
        print('  ' + str(x) + '% processed')
    elif x != 100:
        print(' ' + str(x) + '% processed')
    else:
        print(str(x) + '% processed')

def sort_by_coords(points, order='zyx'):
    d = {'x':0, 'y':1, 'z':2}
    order_list = [d[x] for x in order]
    indices = np.lexsort((points[:, order_list[2]],
                          points[:, order_list[1]],
                          points[:, order_list[0]]))
    return points[indices]

def preprocess(input_folder,
               output_folder='ply',
               decimals=5,
               info=None,
               sorting_order=None,
               extension='.pts'):
    """Given a folder with a point cloud stored in files in .pts format, it
    prepares and transforms them to .ply format to be compressed using FRL"""

    # Take all the file names
    #print(os.listdir('/'.join(output_folder.split('/')[0:-1])))
    #if 'ply' not in os.listdir('/'.join(output_folder.split('/')[0:-1])):
    #    raise FileNotFoundError
    files = [f for f in os.listdir(input_folder) if f.endswith(extension)]
    num_files = len(files)
    if num_files == 0:
        return False
    digits = int(np.log10(num_files)) + 1

    last = 0
    count = 0
    out = 'file' + '0'*digits + '.ply'

    # Iterate for each file
    for i, f in enumerate(files):
        if info is not None:
            while i >= last * num_files / 100:
                print_perc(last)
                last += info

        # Load the PTS file into a pandas DataFrame
        df = pd.read_csv(input_folder+'/'+f, delimiter=' ', header=None)

        # Convert the DataFrame to a NumPy array
        points = np.array(df)[:, 0:3]

        indexes = np.unique(points, return_index=True, axis=0)[1]
        points = np.array([points[index] for index in sorted(indexes)])

        # Transformate points
        points = np.copy(points)
        points *= 10 ** (decimals)
        for j in range(points.shape[1]):
            points[:, j] -= points[:, j].min()
        #points -= points.min()
        points = np.array(points, np.uint32)

        if sorting_order is not None:
            points = sort_by_coords(points, sorting_order)

        header = 'ply\nformat ascii 1.0\nelement vertex ' + str(len(points)) + \
                 '\nproperty float x\nproperty float y\nproperty float z\n' + \
                 'end_header\n'

        with open(output_folder+'/'+out, 'w') as f:
            f.write(header)
            np.savetxt(f, points, delimiter=' ', fmt='%d %d %d')

        out = 'file' + '0'*(digits - int(np.log10(i+1)) - 1) + str(i+1) + '.ply'

    if info is not None:
        last += info
        while last < 100:
            print_perc(last)
            last += info
        print_perc(100)

    return True

def preprocess_dataset(input_folder,
                       output_folder,
                       decimals=5,
                       info=None,
                       sorting_order=None,
                       extension='.pts'):
    #print(os.walk(dataset_folder))
    for root, dirs, files in os.walk(input_folder):
        relative_path = os.path.relpath(root, input_folder)
        new_folder = os.path.join(output_folder, relative_path)
        os.makedirs(new_folder, exist_ok=True)
        if info is not None:
            print('\n---------------------------------------------------------')
            print('Preprocessing folder', root)
            print()
        ok = preprocess(input_folder=root,
                        output_folder=new_folder,
                        decimals=decimals,
                        info=info,
                        sorting_order=sorting_order,
                        extension=extension)
        if info is not None and ok:
            print('\nFolder', root, 'preprocessed')
            print('---------------------------------------------------------\n')
        elif info is not None:
            print('Nothing to preprocess here')
            print('---------------------------------------------------------\n')



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', dest='dataset', type=bool, help='If an entire dataset has to be processed', default=False)
    parser.add_argument('--input', dest='input', type=str, help='Path of the input folder', default=os.getcwd())
    parser.add_argument('--output', dest='output', type=str, help='Path of the output folder', default='./ply')
    parser.add_argument('--sort', dest='sort', type=str, help='Sorting order')
    parser.add_argument('--decimals', dest='decimals', type=int, help='Number of decimals of the data files', default=5)
    parser.add_argument('--info', dest='info', type=int, help='Number of decimals of the data files', default=None)
    parser.add_argument('--extension', dest='extension', type=str, help='Extension of the files to read', default='.pts')
    args = parser.parse_args()

    if args.dataset:
        preprocess_dataset(input_folder=args.input,
                           output_folder=args.output,
                           decimals=args.decimals,
                           info=args.info,
                           sorting_order=args.sort,
                           extension=args.extension)
    else:
        preprocess(input_folder=args.input,
                    output_folder=args.output,
                    decimals=args.decimals,
                    info=args.info,
                    sorting_order=args.sort,
                    extension=args.extension)
