from queue import Queue
import threading
import pigpio
import time

# LEDのピン設定
PIN_RED_LED = 16
PIN_BLUE_LED = 20

LED_DICT = {
    "red" : PIN_RED_LED,
    "blue" : PIN_BLUE_LED,
}


class LedThread(threading.Thread):
    """
    LED管理
    例:
    queue経由で、{"name":"red", "action":"on"}
    を取得すると、赤色のLEDを点灯
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.setDaemon(True)

        self._rcv_que = Queue()
        self._led = {}

        self._pi = pigpio.pi()
        # BCM指定, 各ピンを出力に設定
        for key in LED_DICT:
            pin = LED_DICT[key]
            self._pi.set_mode(pin, pigpio.OUTPUT)
            self._led[key] = {}
            self._led[key]["pin"] = pin
        return

    def stop(self):
        self.stop_event.set()
        # cleanup
        for key in self._led:
            pin = self._led[key]["pin"]
            self._pi.set_mode(pin, pigpio.INPUT)
        self._pi.stop()
        return


    def run(self):
        while True:
            # time.sleep(0.050)
            value = self.rcv_que.get()
            print("[led_th]", "run : get : ", value)
            
            if "led" not in value["type"]:
                print("[led_th]", "error : type")
                continue
            
            if value["name"] in self._led:
                name = value["name"]
                on_off = True if ("on" in value["action"]) else False
                self._write_led(name, on_off)
        return

    @property
    def rcv_que(self):
        return self._rcv_que

    def _write_led(self, name, on_off):
        gpio_logic = 1 if on_off else 0
        self._pi.write(self._led[name]["pin"], gpio_logic)
        return


def main():
    import time

    led_th = LedThread()
    led_th.start()
    q = led_th.rcv_que

    q.put({"type": "led", "name": "red", "action": "on"})
    time.sleep(1)
    q.put({"type": "led", "name": "red", "action": "off"})
    time.sleep(1)
    q.put({"type": "led", "name": "blue", "action": "on"})
    time.sleep(1)
    q.put({"type": "led", "name": "blue", "action": "off"})
    time.sleep(1)

    led_th.stop()
   
    return

if __name__ == "__main__":
    main()