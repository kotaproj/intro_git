from queue import Queue
import threading
import time
from systems import SystemsData

# Imports the necessary libraries...
import socket
import fcntl
import struct
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# graph
import pandas as pd
import matplotlib as plt

# debug
import sys
from icecream import ic

# OLED設定
DISP_WIDTH = 128
DISP_HEIGHT = 64
DEVICE_ADDR = 0x3C

CSV_FILE_VERANDA = "/tmp/env_temp.csv"
CSV_FILE_ROOM = "/tmp/room_temp.csv"

# PATH_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
PATH_FONT = "/home/pi/pim_rev1/camrobo2/ipaexm.ttf"

class OledThread(threading.Thread):
    """
    OLED管理
    例:
    queue経由で、{"type":"oled", "time": "3000", "disp":"ip"}
    disp : ip / clear
    を取得すると、ブザー音を300msec鳴らす
    """
    def __init__(self):
        ic()
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.setDaemon(True)

        self._rcv_que = Queue()
        self._sysdat = SystemsData()

        # Setting some variables for our reset pin etc.
        RESET_PIN = digitalio.DigitalInOut(board.D4)
        TEXT = ""

        # Very important... This lets py-gaugette 'know' what pins to use in order to reset the display
        i2c = board.I2C()
        # oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3D, reset=RESET_PIN)
        self._oled = adafruit_ssd1306.SSD1306_I2C(DISP_WIDTH, DISP_HEIGHT, i2c, addr=DEVICE_ADDR, reset=RESET_PIN)

        # font
        self._font10 = ImageFont.truetype(PATH_FONT, 10)
        self._font12 = ImageFont.truetype(PATH_FONT, 12)
        self._font14 = ImageFont.truetype(PATH_FONT, 14)
        self._font16 = ImageFont.truetype(PATH_FONT, 16)
        self._font18 = ImageFont.truetype(PATH_FONT, 18)

        # Clear display.
        self._oled.fill(0)
        self._oled.show()
        return

    def stop(self):
        ic()
        self.stop_event.set()
        # cleanup
        self._oled.fill(0)
        self._oled.show()
        return


    def run(self):
        ic()
        while True:
            item = self.rcv_que.get()
            ic(sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, item)
            # print("[oled_th]", "run : get : ", item)
            
            if "oled" not in item["type"]:
                print("[oled_th]", "error : type")
                continue
            
            self._recvice(item)
        return

    @property
    def rcv_que(self):
        return self._rcv_que

    def _recvice(self, item):
        ic()
        val_time = int(item["time"]) / 1000
        val_disp = item["disp"]

        def display_ip():
            ic()
            def get_ip_address(ifname):
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                return socket.inet_ntoa(
                    fcntl.ioctl(
                        s.fileno(),
                        0x8915,  # SIOCGIFADDR
                        struct.pack("256s", str.encode(ifname[:15])),
                    )[20:24]
                )
            # This sets TEXT equal to whatever your IP address is, or isn't
            try:
                TEXT = get_ip_address("wlan0")  # WiFi address of WiFi adapter. NOT ETHERNET
            except IOError:
                try:
                    TEXT = get_ip_address("eth0")  # WiFi address of Ethernet cable. NOT ADAPTER
                except IOError:
                    TEXT = "NO INTERNET!"


            # Clear display.
            self._oled.fill(0)
            self._oled.show()

            # Create blank image for drawing.
            image = Image.new("1", (self._oled.width, self._oled.height))
            draw = ImageDraw.Draw(image)

            # Draw the text
            intro = "カムロボです。"
            ip = "IPアドレス:"
            draw.text((0, 46), TEXT, font=self._font14, fill=255)
            draw.text((0, 0), intro, font=self._font18, fill=255)
            draw.text((0, 30), ip, font=self._font14, fill=255)

            # Display image
            self._oled.image(image)
            self._oled.show()

            return


        def display_temp_hum_press(place="veranda"):
            # Clear display.
            self._oled.fill(0)
            self._oled.show()

            # Create blank image for drawing.
            image = Image.new("1", (self._oled.width, self._oled.height))
            draw = ImageDraw.Draw(image)

            # Draw the text
            line = "<veranda>" if place is "veranda" else "<room>"
            draw.text((0, 0*16), line, font=self._font14, fill=255)

            moji_temp = self._sysdat.veranda_temp if place is "veranda" else self._sysdat.room_temp
            line = "temp:" + moji_temp[:6] + " deg"
            draw.text((10, 1*16), line, font=self._font14, fill=255)

            moji_hum = self._sysdat.veranda_hum if place is "veranda" else self._sysdat.room_hum
            line = "hum:" + moji_hum[:6] + " %"
            draw.text((10, 2*16), line, font=self._font14, fill=255)

            if place is "veranda":
                moji_pressure = self._sysdat.veranda_pressure
                line = "pres:" + moji_pressure[:7] + " hPa"
            else:
                moji_co2 = self._sysdat.room_co2
                line = "co2:" + moji_co2 + " PPM"
            draw.text((10, 3*16), line, font=self._font14, fill=255)
            
            # Display image
            self._oled.image(image)
            self._oled.show()
            return


        def display_graph(mes_item="temp", place="veranda"):

            # Clear display.
            self._oled.fill(0)
            self._oled.show()

            # oled描画
            if place is "veranda":
                png_path = "/tmp/camroboveranda_temp_mono.png"
            elif place is "room_co2":
                png_path = "/tmp/camroboroom_co2_mono.png"
            else:
                png_path = "/tmp/camroboroom_temp_mono.png"
            im_mono = Image.open(png_path)
            self._oled.image(im_mono)
            self._oled.show()
            return

        def display_webmanga(page="0"):
            # Clear display.
            self._oled.fill(0)
            self._oled.show()

            # Create blank image for drawing.
            image = Image.new("1", (self._oled.width, self._oled.height))
            draw = ImageDraw.Draw(image)

            # Draw the text
            line = "ワンパンマン:" + self._sysdat.webm_onepan
            draw.text((0, 0*16), line, font=self._font14, fill=255)

            line = "ワンパンR:" + self._sysdat.webm_onepan_r
            draw.text((0, 1*16), line, font=self._font14, fill=255)

            line = "邪神ちゃん" + self._sysdat.webm_jyashin
            draw.text((0, 2*16), line, font=self._font14, fill=255)

            line = "キン肉マン:" + self._sysdat.webm_kinnikuman2
            draw.text((0, 3*16), line, font=self._font14, fill=255)
            
            # Display image
            self._oled.image(image)
            self._oled.show()
            return


        def display_clear():
            self._oled.fill(0)
            self._oled.show()
            return

        if "ip" in val_disp:
            display_ip()
        elif "room" in val_disp:
            display_temp_hum_press("room")
        elif "graph_r_co2" in val_disp:
            display_graph("co2", "room_co2")
        elif "graph_r_temp" in val_disp:
            display_graph("temp", "room")
        elif "graph_r_hum" in val_disp:
            display_graph("hum", "room")
        elif "veranda" in val_disp:
            display_temp_hum_press("veranda")
        elif "graph_v_temp" in val_disp:
            display_graph("temp", "veranda")
        elif "graph_v_hum" in val_disp:
            display_graph("hum", "veranda")
        elif "webmanga" in val_disp:
            display_webmanga()
        else:
            # Clear display.
            display_clear()
        return

def main():
    import time

    oled_th = OledThread()
    oled_th.start()
    q = oled_th.rcv_que

    q.put({"type": "oled", "time": "3000", "disp":"ip"})
    time.sleep(3)
    q.put({"type": "oled", "time": "3000", "disp":"room"})
    time.sleep(3)
    q.put({"type": "oled", "time": "3000", "disp":"webmanga"})
    time.sleep(3)
    q.put({"type": "oled", "time": "3000", "disp":"clear"})
    time.sleep(3)

    oled_th.stop()
   
    return

if __name__ == "__main__":
    main()