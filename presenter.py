from queue import Queue
import threading
from systems import SystemsData
import ast

class PreThread(threading.Thread):
    """
    プレゼンター
    """
    def __init__(self, snd_ques={}):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.setDaemon(True)

        self._rcv_que = Queue()
        self._snd_ques = snd_ques
        self._sysdat = SystemsData()
        return

    def stop(self):
        self.stop_event.set()
        return


    def run(self):
        while True:
            # time.sleep(0.050)
            item = self.rcv_que.get()
            print("[pre_th]", "run : get : ", item)
            if "sw" in item["type"]:
                self._recvice_sw(item)
            elif "subsc" in item["type"]:
                self._recvice_subsc(item)
            else:
                print("[pre_th]", "Error : ", item)

        return
    
    def _recvice_sw(self, item):
        print("[pre_th]", "run : _recvice_sw")

        def send_que_sw_red():
            if "oled" not in self._snd_ques:
                print("[pre_th]", "que not found!", "send_que_oled")
                return
            val_time = "3000"
            val_disp = "ip"
            self._snd_ques["oled"].put({"type": "oled", "time": val_time, "disp": val_disp})
            return

        def send_que_sw_blue():
            if "oled" not in self._snd_ques:
                print("[pre_th]", "que not found!", "send_que_oled")
                return
            val_time = "3000"
            val_disp = self._sysdat.get_next_display()
            self._snd_ques["oled"].put({"type": "oled", "time": val_time, "disp": val_disp})
            return

        name = item["name"]
        if "red" in name:
            send_que_sw_red()
        elif "blue" in name:
            send_que_sw_blue()
        else:
            print("[pre_th]", "command not found!", name)
        return
    
    def _recvice_subsc(self, item):
        print("[pre_th]", "run : _recvice_subsc")

        def send_que_led(action):
            if "led" not in self._snd_ques:
                print("[pre_th]", "que not found!", "send_que_led")
                return
            val_name = "red" if "red" in action else "blue"
            val_act = "on" if "on" in action else "off"
            self._snd_ques["led"].put({"type": "led", "name": val_name, "action": val_act})
            return

        def send_que_buzzer(action):
            if "buzzer" not in self._snd_ques:
                print("[pre_th]", "que not found!", "send_que_buzzer")
                return
            val_time = "500" if "short" in action else "3000"
            val_bfreq = "10000"
            self._snd_ques["buzzer"].put({"type": "buzzer", "name": "buzzer", "time": val_time, "bfreq": val_bfreq})
            return

        def send_que_servo(action):
            print("[pre_th]", "run : send_que_servo")
            if "servo" not in self._snd_ques:
                print("[pre_th]", "que not found!", "send_que_servo")
                return
            val_name = "left" if "left" in action else "right"
            val_act = "raise" if "raise" in action else "down"
            self._snd_ques["servo"].put({"type": "servo", "name": val_name, "action": val_act})
            return

        def send_que_dcm(action):
            print("[pre_th]", "run : send_que_dcm")
            if "dcm" not in self._snd_ques:
                print("[pre_th]", "que not found!", "send_que_dcm")
                return

            acts = ["forward", "back", "stop", "left", "right", "brake"]
            
            val_act = ""
            for act in acts:
                if act in action:
                    val_act = act
                    break
            val_speed = "fast"
            self._snd_ques["dcm"].put({"type": "dcm", "action": val_act, "speed": val_speed})
            return

        def send_que_oled(action):
            print("[pre_th]", "run : send_que_oled")
            if "oled" not in self._snd_ques:
                print("[pre_th]", "que not found!", "send_que_oled")
                return
            val_time = "3000"
            val_disp = action.replace("oled_", "")

            self._snd_ques["oled"].put({"type": "oled", "time": val_time, "disp": val_disp})
            return

        def store_twilite(msg):
            print("[pre_th]", "run : store_pi0")
            veranda = ast.literal_eval(msg)
            self._sysdat.veranda_temp = veranda["temp"]
            self._sysdat.veranda_hum = veranda["hum"]
            self._sysdat.veranda_pressure = veranda["pressure"]
            return

        def store_pi0(msg):
            print("[pre_th]", "run : store_pi0")
            room = ast.literal_eval(msg)
            self._sysdat.room_temp = room["temp"]
            self._sysdat.room_hum = room["hum"]
            self._sysdat.room_pressure = room["pressure"]
            return

        def store_co2m(msg):
            print("[pre_th]", "run : store_co2m")
            room = ast.literal_eval(msg)
            self._sysdat.room_co2 = room["co2"]
            return

        def store_webmanga(msg):
            print("[pre_th]", "run : store_webmanga")
            # 内部に保存
            print(msg)
            webm = ast.literal_eval(msg)
            self._sysdat.set_webm(webm["title"], webm["episode"])

            # 左腕を振って通知
            val_name = "left"
            val_act = "swing"
            self._snd_ques["servo"].put({"type": "servo", "name": val_name, "action": val_act})
            return

        action = item["action"]
        print("item :", item)
        if "buzzer" in action:
            send_que_buzzer(action)
        elif "servo" in action:
            send_que_servo(action)
        elif "motor" in action:
            send_que_dcm(action)
        elif "oled" in action:
            send_que_oled(action)
        elif "led" in action:
            send_que_led(action)
        elif "twilite" in action:
            store_twilite(item["msg"])
        elif "pi0" in action:
            store_pi0(item["msg"])
        elif "co2m" in action:
            store_co2m(item["msg"])
        elif "webmanga" in action:
            store_webmanga(item["msg"])
        else:
            print("[pre_th]", "command not found!", action)
        return
    
    
    @property
    def rcv_que(self):
        return self._rcv_que


def main():
    import time

    pre_th = PreThread()
    pre_th.start()
    q = pre_th.rcv_que
    q.put("123")
    time.sleep(1)

    for i in range(5):
        q.put(i)
        time.sleep(1)
    pre_th.stop()
   
    return



# def main():
#     import time

#     from led import LedThread

#     led_th = LedThread()
#     led_th.start()
#     que_led = led_th.rcv_que

#     pre_th = PreThread({"led": que_led})
#     pre_th.start()



#     q = pre_th.rcv_que
#     q.put("123")
#     time.sleep(1)


#     q.put({"type": "led", "name": "red", "action": "on"})
#     time.sleep(1)
#     q.put({"type": "led", "name": "red", "action": "off"})
#     time.sleep(1)
#     q.put({"type": "led", "name": "blue", "action": "on"})
#     time.sleep(1)
#     q.put({"type": "led", "name": "blue", "action": "off"})
#     time.sleep(1)

#     led_th.stop()




#     pre_th = PreThread()
#     pre_th.start()
#     q = pre_th.rcv_que
#     q.put("123")
#     time.sleep(1)

#     for i in range(5):
#         q.put(i)
#         time.sleep(1)
#     pre_th.stop()
   
#     return




if __name__ == "__main__":
    main()