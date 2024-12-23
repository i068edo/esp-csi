import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

invalid_subcarrier = [0, 1, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 64, 93, 94, 95, 96, 97, 98, 99]
valid_subcarriers = [i for i in range(128) if i not in invalid_subcarrier]

# 省略せずに全ての要素を表示する設定
""" np.set_printoptions(threshold=np.inf) """

def read_csi_data(file_path):
    data = pd.read_csv(file_path)
    print(data.head())
    return data

def set_amplitude(df, idx):
    subc_data = []
    for index, row in df.iterrows():
        subcarrier = [int(x) for x in row[f"subc_{idx}"].strip('[]').split(',')]
        complex_data = complex(subcarrier[0], subcarrier[1])
        amplitude = np.abs(complex_data)
        subc_data.append(amplitude)
           
    return np.array(subc_data)

def Hampel(x, k, thr=3):
    arraySize = len(x)
    idx = np.arange(arraySize)
    output_x = x.copy()
    output_Idx = np.zeros_like(x)
 
    for i in range(arraySize):
        mask1 = np.where( idx >= (idx[i] - k) ,True, False)
        mask2 = np.where( idx <= (idx[i] + k) ,True, False)
        kernel = np.logical_and(mask1, mask2)
        median = np.median(x[kernel])
        std = 1.4826 * np.median(np.abs(x[kernel] - median))
        
        if np.abs(x[i] - median) > thr * std:
            output_Idx[i] = 1
            output_x[i] = median
            x[i] = median #データを置き換え
 
    # return output_x, output_Idx.astype(bool)
    return output_x, output_Idx, x

# 正規化の関数
""" def max_min_normalize(data):
    min_val = np.min(data)
    max_val = np.max(data)
    return (data - min_val) / (max_val - min_val) """

def z_score_normalize(data):
    mean_val = np.mean(data)
    std_val = np.std(data)
    return (data - mean_val) / std_val

def main():
    df = read_csi_data('./import_csidata/20241218_153152419243.csv')

    normalized_df = pd.DataFrame()
    normalized_df['timestamp'] = df['timestamp']
    # Dictionary to hold all normalized data
    normalized_data_dict = {}

    for i in valid_subcarriers:
        subc_data = set_amplitude(df, i)
        result = Hampel(subc_data, k=2, thr=3)
        filtered_data = result[2]
        normalized_data = z_score_normalize(filtered_data)
        normalized_data_dict[f'subcarrier_{i}'] = normalized_data

    # Use pd.concat to add all columns at once
    normalized_df = pd.concat([normalized_df, pd.DataFrame(normalized_data_dict)], axis=1)
    print(normalized_df.head())
    normalized_df.to_csv('./filtered_csidata/20241218_153152419243.csv', index=False, encoding='utf-8-sig')
        
    """ plt_time = set_time(df)
    time_plt(filtered_data, plt_time) """


if __name__ == "__main__":
    main()
