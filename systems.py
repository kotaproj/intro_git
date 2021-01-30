# debug
import sys
from icecream import ic

class SystemsData:
    _instance = None
    inited = False

    def __init__(self):
        ic()
        if False == SystemsData.inited:
            ic()
            self.__display = "clear"
            self.__room = {}
            self.__room["temp"] = "no data"
            self.__room["hum"] = "no data"
            self.__room["pressure"] = "no data"
            self.__room["co2"] = "no data"
            self.__veranda = {}
            self.__veranda["temp"] = "no data"
            self.__veranda["hum"] = "no data"
            self.__veranda["pressure"] = "no data"
            self.__webm = {}
            self.__webm["onepan"] = "no data"
            self.__webm["onepan_r"] = "no data"
            self.__webm["jyashin"] = "no data"
            self.__webm["kinnikuman2"] = "no data"
            SystemsData.inited = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    @property
    def display(self):
        return self.__display

    @display.setter
    def display(self, display):
        self.__display = display

    def get_next_display(self):
        conv_tbl = {
            "clear":{"next": "ip", "prev": "graph_v_hum"},
            "ip":{"next": "room", "prev": "clear"},
            "room":{"next": "graph_r_temp", "prev": "ip"},
            "graph_r_temp":{"next": "graph_r_hum", "prev": "room"},
            "graph_r_hum":{"next": "veranda", "prev": "graph_r_temp"},
            "veranda":{"next": "graph_v_temp", "prev": "graph_r_hum"},
            "graph_v_temp":{"next": "graph_v_hum", "prev": "veranda"},
            "graph_v_hum":{"next": "clear", "prev": "graph_v_temp"},
        }

        self.__display = conv_tbl[self.__display]["next"]
        return self.__display

    @property
    def room_temp(self):
        return self.__room["temp"]

    @room_temp.setter
    def room_temp(self, sdata):
        self.__room["temp"] = sdata

    @property
    def room_hum(self):
        return self.__room["hum"]

    @room_hum.setter
    def room_hum(self, sdata):
        self.__room["hum"] = sdata

    @property
    def room_pressure(self):
        return self.__room["pressure"]

    @room_pressure.setter
    def room_pressure(self, sdata):
        self.__room["pressure"] = sdata

    @property
    def room_co2(self):
        return self.__room["co2"]

    @room_co2.setter
    def room_co2(self, sdata):
        self.__room["co2"] = sdata

    @property
    def veranda_temp(self):
        return self.__veranda["temp"]

    @veranda_temp.setter
    def veranda_temp(self, sdata):
        self.__veranda["temp"] = sdata

    @property
    def veranda_hum(self):
        return self.__veranda["hum"]

    @veranda_hum.setter
    def veranda_hum(self, sdata):
        self.__veranda["hum"] = sdata

    @property
    def veranda_pressure(self):
        return self.__veranda["pressure"]

    @veranda_pressure.setter
    def veranda_pressure(self, sdata):
        self.__veranda["pressure"] = sdata

    @property
    def webm_onepan(self):
        return self.__webm["onepan"]

    @webm_onepan.setter
    def webm_onepan(self, sdata):
        self.__webm["onepan"] = sdata

    @property
    def webm_onepan_r(self):
        return self.__webm["onepan_r"]

    @webm_onepan_r.setter
    def webm_onepan_r(self, sdata):
        self.__webm["onepan_r"] = sdata

    @property
    def webm_jyashin(self):
        return self.__webm["jyashin"]

    @webm_jyashin.setter
    def webm_jyashin(self, sdata):
        self.__webm["jyashin"] = sdata

    @property
    def webm_kinnikuman2(self):
        return self.__webm["kinnikuman2"]

    @webm_kinnikuman2.setter
    def webm_kinnikuman2(self, sdata):
        self.__webm["kinnikuman2"] = sdata

    def set_webm(self, title, sdata):
        if title in self.__webm:
            self.__webm[title] = sdata


def main():
    import time

    sysdat = SystemsData()
    
    ic(sysdat.room_temp, sysdat.room_hum, sysdat.room_pressure, sysdat.room_co2)

    sysdat.room_temp = "0"
    sysdat.room_hum = "1"
    sysdat.room_pressure = "2"
    sysdat.room_co2 = "3"

    ic(sysdat.room_temp, sysdat.room_hum, sysdat.room_pressure, sysdat.room_co2)

    return

if __name__ == "__main__":
    main()