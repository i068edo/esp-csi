import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def read_csi_data():
    file_path = './../pre-processing/import_csidata/20241218_153152419243.csv'
    data = pd.read_csv(file_path)
    print(data.head())
    return data

def set_amplitude(df):
    plt_data = []
    for index, row in df.iterrows():
        subcarrier = [int(x) for x in row['subc_20'].strip('[]').split(',')]
        complex_data = complex(subcarrier[0], subcarrier[1])
        amplitude = np.abs(complex_data)
        plt_data.append(amplitude)
        
    return plt_data

def set_time(df):
    plt_time = []
    for index, row in df.iterrows():
        timestamp = row['timestamp']
        plt_time.append(timestamp)

    return plt_time

def time_plt(plt_data, plt_time, step=1):
    plt.figure(figsize=(12, 6))
    plt.plot(plt_time[10000:20000], plt_data[10000:20000], marker=",")
    """ plt.plot(plt_time[::step], plt_data[::step], marker=",") """
    plt.title('Time series data')
    plt.xlabel('time')
    plt.ylabel('amplitude')
    plt.grid()
    plt.show()

def main():
    df = read_csi_data()
    plt_data = set_amplitude(df)
    """ plt_data = []
    for index, row in df.iterrows():
        plt_data.append(row['subc_20']) """

    plt_time = set_time(df)
    time_plt(plt_data, plt_time)

if __name__ == "__main__":
    main()