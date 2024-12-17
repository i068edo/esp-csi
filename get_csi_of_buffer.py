import sys
import csv
import json
import argparse
import pandas as pd
import numpy as np

import serial
from os import path
from io import StringIO

from PyQt5.Qt import *
from pyqtgraph import PlotWidget
from PyQt5 import QtCore
import pyqtgraph as pq

import threading
import time
import datetime

DATA_COLUMNS_NAMES = ["type", "id", "mac", "rssi", "rate", "sig_mode", "mcs", "bandwidth", "smoothing", "not_sounding", "aggregation", "stbc", "fec_coding",
                      "sgi", "noise_floor", "ampdu_cnt", "channel", "secondary_channel", "local_timestamp", "ant", "sig_len", "rx_state", "len", "first_word", "data", "timestamp"]

# バッファサイズの設定
BUFFER_SIZE = 10

class csi_data_graphical_window(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(1280, 720)
        self.total_packet_count = 0
        self.write_thread_running = True  # 終了フラグを追加

    def closeEvent(self, event):
        print(f"Total packets: {self.total_packet_count}")
        self.write_thread_running = False  # 終了フラグを設定
        event.accept()

def csi_data_read_parse(port: str, buffer, log_file_fd, window):
    ser = serial.Serial(port=port, baudrate=1500000,
                        bytesize=8, parity='N', stopbits=1)
    if ser.isOpen():
        print("open success")
    else:
        print("open failed")
        return
    
    packet_count = 0
    start_time = time.time()

    while True:
        strings = str(ser.readline())
        if not strings:
            break

        # タイムスタンプの取得
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        strings = strings.lstrip('b\'').rstrip('\\r\\n\'')
        index = strings.find('CSI_DATA')

        if index == -1:
            log_file_fd.write(strings + '\n')
            log_file_fd.flush()
            continue

        csv_reader = csv.reader(StringIO(strings))
        csi_data = next(csv_reader)

        if len(csi_data) != len(DATA_COLUMNS_NAMES)-1:
            print("element number is not equal")
            log_file_fd.write("element number is not equal\n")
            log_file_fd.write(strings + '\n')
            log_file_fd.flush()
            continue

        try:
            csi_raw_data = json.loads(csi_data[-1])
        except json.JSONDecodeError:
            print("data is incomplete")
            log_file_fd.write("data is incomplete\n")
            log_file_fd.write(strings + '\n')
            log_file_fd.flush()
            continue

        if len(csi_raw_data) != 128 and len(csi_raw_data) != 256 and len(csi_raw_data) != 384:
            print(f"element number is not equal: {len(csi_raw_data)}")
            log_file_fd.write(f"element number is not equal: {len(csi_raw_data)}\n")
            log_file_fd.write(strings + '\n')
            log_file_fd.flush()
            continue

        csi_data.append(timestamp)  # タイムスタンプをデータに追加
        buffer.append(csi_data)  # データをバッファに追加
            
        packet_count += 1
        window.total_packet_count += 1

        current_time = time.time()
        if current_time - start_time >= 1:
            print(f"Packets per second: {packet_count}")
            packet_count = 0
            start_time = current_time

    ser.close()
    return

def csi_data_write(buffer, csv_writer):
    while True:
        if buffer:
            data = buffer.pop(0)
            csv_writer.writerow(data)
        else:
            time.sleep(0.005)  # バッファが空の場合、少し待機
            if(not(window.write_thread_running)):
                return

class SubThread (QThread):
    def __init__(self, serial_port, save_file_name, log_file_name, window):
        super().__init__()
        self.serial_port = serial_port
        self.window = window

        save_file_fd = open(save_file_name, 'w')
        self.log_file_fd = open(log_file_name, 'w')
        self.csv_writer = csv.writer(save_file_fd)
        self.csv_writer.writerow(DATA_COLUMNS_NAMES)

        self.buffer = []  # バッファを初期化

        # 書き込みスレッドを開始
        self.write_thread = threading.Thread(target=csi_data_write, args=(self.buffer, self.csv_writer))
        self.write_thread.start()

    def run(self):
        csi_data_read_parse(self.serial_port, self.buffer, self.log_file_fd, self.window)

    def __del__(self):
        self.wait()
        self.log_file_fd.close()

if __name__ == '__main__':
    if sys.version_info < (3, 6):
        print(" Python version should >= 3.6")
        exit()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")

    parser = argparse.ArgumentParser(
        description="Read CSI data from serial port and display it graphically")
    parser.add_argument('-p', '--port', dest='port', action='store', required=True,
                        help="Serial port number of csv_recv device")
    parser.add_argument('-s', '--store', dest='store_file', action='store', default=f"./{timestamp}.csv",
                        help="Save the data printed by the serial port to a file")
    parser.add_argument('-l', '--log', dest="log_file", action="store", default="./csi_data_log.txt",
                        help="Save other serial data the bad CSI data to a log file")

    args = parser.parse_args()
    serial_port = args.port
    file_name = args.store_file
    log_file_name = args.log_file

    app = QApplication(sys.argv)

    window = csi_data_graphical_window()
    subthread = SubThread(serial_port, file_name, log_file_name, window)
    subthread.start()

    window.show()

    sys.exit(app.exec())