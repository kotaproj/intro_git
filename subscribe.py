from queue import Queue
import threading
import time
from time import sleep
import paho.mqtt.client as mqtt
from commands import SUBSC_DICT


HOST = '192.168.11.12'
PORT = 1883
TOPIC = 'topic_1'


class SubscThread(threading.Thread):
    """
    MQTT - Subscribe管理
    """
    def __init__(self, snd_que=None):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.setDaemon(True)

        self._snd_que = snd_que
        return


    def stop(self):
        self.stop_event.set()
        return


    def run(self):

        def on_connect(client, userdata, flags, respons_code):
            print('status {0}'.format(respons_code))
            client.subscribe(TOPIC)

        def on_message(client, userdata, msg):
            msg_payload = str(msg.payload,'utf-8')
            print(msg.topic + ':' + msg_payload)
            # # 完全一致
            if msg_payload in SUBSC_DICT:
                print("subprocess" + ':' + msg_payload)
                self._send_msg(SUBSC_DICT[msg_payload])
                return
            # 部分一致
            elif "twilite" in msg_payload:
                self._send_msg_for_twilite(msg_payload)
            elif "pi0" in msg_payload:
                self._send_msg_for_pi0(msg_payload)
            elif "co2m" in msg_payload:
                self._send_msg_for_co2m(msg_payload)
            elif "webmanga" in msg_payload:
                self._send_msg_for_webmanga(msg_payload)
            else:
                print("!!!on_message - ERROR!!!")  

        client = mqtt.Client(protocol=mqtt.MQTTv311)

        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(HOST, port=PORT, keepalive=60)

        client.loop_forever()
        return

   
    def _send_msg(self, item):
        if self._snd_que is None:
            return
        print("[subsc_th]", "_send_msg:", item)
        self._snd_que.put(item)
        return

    def _send_msg_for_twilite(self, msg):
        if self._snd_que is None:
            return
        item = {"type": "subsc", "action": "twilite"}
        item["msg"] = msg
        self._snd_que.put(item)
        return

    def _send_msg_for_pi0(self, msg):
        if self._snd_que is None:
            return
        item = {"type": "subsc", "action": "pi0"}
        item["msg"] = msg
        self._snd_que.put(item)
        return

    def _send_msg_for_co2m(self, msg):
        if self._snd_que is None:
            return
        item = {"type": "subsc", "action": "co2m"}
        item["msg"] = msg
        self._snd_que.put(item)
        return

    def _send_msg_for_webmanga(self, msg):
        if self._snd_que is None:
            return
        item = {"type": "subsc", "action": "webmanga"}
        item["msg"] = msg
        self._snd_que.put(item)
        return


def main():
    q = Queue()
    subsc_th = SubscThread(q)
    subsc_th.start()
    time.sleep(10)
    subsc_th.stop()
    
    while True:
        if q.empty():
            print("!!! q.empty !!!")
            break
        print(q.get())
    return

if __name__ == "__main__":
    main()