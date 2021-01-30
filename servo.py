from queue import Queue
import threading
import pigpio
import time

# SG90のピン設定
SERVO_LEFT_PIN = 17  # SG90-1
SERVO_RIGHT_PIN = 27  # SG90-2

MIN_DEGREE = 500        # 000 : -90degree
# MID_DEGREE = 1450     # 090 : 0degree
MAX_DEGREE = 2350       # 180 : +90degree

LEFT_OFFSET = 100
RIGHT_OFFSET = 0


SERVO_DICT = {
    "left" : SERVO_LEFT_PIN,
    "right" : SERVO_RIGHT_PIN,
}


class ServoThread(threading.Thread):
    """
    サーボ管理
    例:
    queue経由で、{"type":"servo", "name": "right", "action": "raise/down/swing"}
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.setDaemon(True)

        self._rcv_que = Queue()
        self._servo = {}

        self._pi = pigpio.pi()
        for key in SERVO_DICT:
            self._servo[key] = {}
            pin = SERVO_DICT[key]
            self._servo[key]["pin"] = pin
        return

    def stop(self):
        self.stop_event.set()
        # cleanup
        for key in self._servo:
            pin = self._servo[key]["pin"]
            self._pi.set_mode(pin, pigpio.INPUT)
        self._pi.stop()
        return


    def run(self):
        while True:
            # time.sleep(0.050)
            item = self.rcv_que.get()
            print("[servo_th]", "run : get : ", item)
            
            if "servo" not in item["type"]:
                print("[servo_th]", "error : type")
                continue
            self._recvice(item)
        return

    @property
    def rcv_que(self):
        return self._rcv_que
    
    def _recvice(self, item):
        name = item["name"]
        action = item["action"]
        if action in ["raise", "down"]:
            deg = 90 if action == "raise" else 0
            pulse = self._cal_degree2pulse(name, deg)
            pin = self._servo[name]["pin"]
            self._pi.set_servo_pulsewidth(pin, pulse)
        elif action in ["swing"]:
            pin = self._servo[name]["pin"]
            for deg in ([45, 90] * 5):
                pulse = self._cal_degree2pulse(name, deg)
                self._pi.set_servo_pulsewidth(pin, pulse)
                time.sleep(0.15)
        else:
            print("[ServoThread] - _recvice - error!!!")
        return

    def _cal_degree2pulse(self, name, degree):
        if "left" in name:
            degree = 180 - degree
            offset = LEFT_OFFSET
        else:
            offset = RIGHT_OFFSET
        return (MAX_DEGREE - MIN_DEGREE)/180 * degree + MIN_DEGREE + offset

def main():
    import time

    servo_th = ServoThread()
    servo_th.start()
    q = servo_th.rcv_que

    # q.put({"type": "servo", "name": "left", "action": "raise"})
    # time.sleep(2)
    # q.put({"type": "servo", "name": "left", "action": "down"})
    # time.sleep(2)
    # q.put({"type": "servo", "name": "right", "action": "raise"})
    # time.sleep(2)
    # q.put({"type": "servo", "name": "right", "action": "down"})
    # time.sleep(2)
    q.put({"type": "servo", "name": "left", "action": "swing"})
    time.sleep(5)
    q.put({"type": "servo", "name": "right", "action": "swing"})
    time.sleep(5)

    servo_th.stop()
   
    return

if __name__ == "__main__":
    main()