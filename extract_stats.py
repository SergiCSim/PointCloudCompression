from pointclouds import PointCloud
import argparse
import os


def generate_stats_csv(input_folder, output_folder, info=False):
    """It generates a csv file for each folder of the preprocessed dataset
       (in ply format)"""

    for folder in sorted(os.listdir(input_folder)):
        if info:
            print('''Generating stats from the folder "''' + folder + '''"''')
        for i, file in enumerate(sorted(os.listdir(input_folder + '/' + folder))):
            print(i, file)
            pc = PointCloud(input_folder + '/' + folder + '/' + file)
            pc.are_int = True
            if i == 0:
                df = pc.get_info(df=True)
                df.insert(0, 'File name', file.split('.')[0])
            else:
                dic = pc.get_info(dic=True)
                dic['File name'] = file
                df = df.append(dic, ignore_index=True)
            del pc
        df.to_csv(output_folder + '/' + folder + '.csv', index=False)
        del df

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', dest='input', type=str, help='Path of the input folder')
    parser.add_argument('--output', dest='output', type=str, help='Path of the output folder', default='.')
    parser.add_argument('--info', dest='info', type=bool, help='If information of which folder is being treated wants to be shown', default=False)
    args = parser.parse_args()

    generate_stats_csv(input_folder=args.input,
                       output_folder=args.output,
                       info=args.info)
