import pandas as pd
import numpy as np

def read_csi_data():
    file_path = './../csidata/1218平本さん/20241218_153152419243.csv'
    data = pd.read_csv(file_path, usecols=[24, 25], comment=",")
    print(data.head())
    return data

def add_valid_subcarrier(df):
    # 有効なサブキャリアの列名を作成
    invalid_subcarrier = [0, 1, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 64, 93, 94, 95, 96, 97, 98, 99]
    valid_subcarriers = [i for i in range(128) if i not in invalid_subcarrier]
    new_columns = {f"subc_{i}": pd.Series([np.nan] * len(df), dtype='object') for i in valid_subcarriers}
    new_df = pd.DataFrame(new_columns)

    # 元のデータフレームと新しい列を持つデータフレームを結合
    df = pd.concat([df, new_df], axis=1)

    # 値を設定
    for index, row in df.iterrows():
        csi_data_str = row['data']
        csi_data = [int(x) for x in csi_data_str.strip('[]').split(',')]
        for i in valid_subcarriers:
            add_subc_value = [csi_data[i*2], csi_data[i*2+1]]
            df.at[index, f"subc_{i}"] = str(add_subc_value)

    # 元のデータを削除
    df = df.drop(columns=['data'])
    return df


def main():
    raw_data_frame = read_csi_data()   
    df_subc_added = add_valid_subcarrier(raw_data_frame)
    print(df_subc_added)
    df_subc_added.to_csv('./import_csidata/20241218_153152419243.csv', index=False, encoding='utf-8-sig')


if __name__ == "__main__":
    main()