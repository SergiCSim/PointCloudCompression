import sys
import pandas as pd
import numpy as np
import open3d as o3d

def print_perc(x):
    if x < 10:
        print('  ' + str(x) + '% processed')
    elif x != 100:
        print(' ' + str(x) + '% processed')
    else:
        print(str(x) + '% processed')

def preprocess(input_folder, output_folder='ply', decimals=5, info=None):
    """Given a folder with a point cloud stored in files in .pts format, it
    prepares and transforms them to .ply format to be compressed using FRL"""

    # Take all the file names
    import os
    if 'ply' not in os.listdir('/'.join(output_folder.split('/')[0:-1])):
        raise FileNotFoundError
    files = os.listdir(input_folder)
    num_files = len(files)
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
            """
            if i == 0:
                print('0/' + str(num_files) + ' processed')
            elif i % info == 0:
                print(str(i) + '/' + str(num_files) + ' processed')
            """

        """out = f[0:f.index('.')] + '.ply'"""

        # Load the PTS file into a pandas DataFrame
        df = pd.read_csv(input_folder+'/'+f, delimiter=' ', header=None)

        # Convert the DataFrame to a NumPy array
        points = np.unique(np.array(df), axis=0)

        # Transformate points
        points = np.copy(points)
        points *= 10 ** (decimals)
        points -= points.min()
        points = np.array(points, np.uint32)

        header = 'ply\nformat ascii 1.0\nelement vertex ' + str(len(points))
        header += '\nproperty float x\nproperty float y\nproperty float z\n'
        header += 'end_header\n'

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


if __name__ == '__main__':

    input_folder = sys.argv[1]
    output_folder = 'ply'
    info = None

    if len(sys.argv) == 3:
        try:
            info = int(sys.argv[2])
        except ValueError:
            output_folder = sys.argv[2]
    elif len(sys.argv):
        try:
            info = int(sys.argv[2])
            output_folder = sys.argv[3]
        except ValueError:
            output_folder = sys.argv[2]
            info = int(sys.argv[3])

    preprocess(input_folder, output_folder=output_folder, decimals=5, info=info)
