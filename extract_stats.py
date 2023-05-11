from pointclouds import PointCloud
import numpy as np
import pandas as pd
import argparse
import os


def generate_stats_csv(input_folder, output_folder, all=False, info=False):
    """It generates a csv file for each folder of the preprocessed dataset
       (in ply format)"""

    for folder in sorted(os.listdir(input_folder)):
        csv_exists = False
        if folder + '.csv' in os.listdir(output_folder):
            if all:
                os.remove(output_folder + '/' + folder + '.csv')
            else:
                csv_exists = True
                prev_df = pd.read_csv(output_folder + '/' + folder + '.csv')
                filenames = np.array(prev_df['File name'])
                print('filenames', filenames)
        if info:
            print('''Generating stats from the folder "''' + folder + '''"''')
        for i, file in enumerate(sorted(os.listdir(input_folder + '/' + folder))):
            if all or not csv_exists:
                print(i, file)
                pc = PointCloud(input_folder + '/' + folder + '/' + file)
                pc.are_int = True
                if i == 0:
                    df = pc.get_info(df=True)
                    df.insert(0, 'File name', file)
                else:
                    dic = pc.get_info(dic=True)
                    dic['File name'] = file
                    df = df.append(dic, ignore_index=True)
                del pc
            elif not all and csv_exists and file not in filenames:
                print(i, file)
                pc = PointCloud(input_folder + '/' + folder + '/' + file)
                pc.are_int = True
                dic = pc.get_info(dic=True)
                dic['File name'] = file
                prev_df = prev_df.append(dic, ignore_index=True)
                del pc
            # else: pass
        if not all and csv_exists:
            prev_df.to_csv(output_folder + '/' + folder + '.csv', index=False)
        else:
            df.to_csv(output_folder + '/' + folder + '.csv', index=False)
        try:
            del df
        except:
            pass
        try:
            del prev_df
        except:
            pass

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', dest='input', type=str, help='Path of the input folder')
    parser.add_argument('--output', dest='output', type=str, help='Path of the output folder', default='.')
    parser.add_argument('--all', dest='all', type=bool, help='If the stats have to be calculated for each file ignoring if they are in the csv files', default=False)
    parser.add_argument('--info', dest='info', type=bool, help='If information of which folder is being treated wants to be shown', default=False)
    args = parser.parse_args()

    generate_stats_csv(input_folder=args.input,
                       output_folder=args.output,
                       all=args.all,
                       info=args.info)
