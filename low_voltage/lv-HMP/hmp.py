import paho.mqtt.client as mqtt
from dataclasses import dataclass
import time
import json
import os
from typing import Union

# import visa
import pyvisa as visa

from dotenv import dotenv_values


@dataclass
class Channel(object):
    number: int
    on: bool = False
    vreq: float = 0.0
    # curr: float =0.


class HMP(object):
    rm = visa.ResourceManager("/usr/lib64/librsvisa.so@ivi")
    config = dotenv_values("hmp.env")
    print("config ", config)
    ip = os.getenv("IP", config["IP"])
    print("hmp ip ", ip)
    port = os.getenv("PORT", config["PORT"])
    print("hmp port ", port)
    # HMP4040 = rm.open_resource(f"TCPIP::{ip}::{port}::SOCKET")
    connection_string = "TCPIP::{}::{}::SOCKET".format(ip, port)
    print("Connection string:", connection_string)
    HMP4040 = rm.open_resource(connection_string)
    # HMP4040 = rm.open_resource("TCPIP::{}::{}::SOCKET".format(ip, port))

    num_of_channels = 5

    def __init__(self, name: str, n_channels: int = 5):
        self.channels = [Channel(i) for i in range(n_channels)]
        self.name = name
        self.num_of_channels = n_channels

        self.HMP4040.read_termination = "\n"
        self.HMP4040.write_termination = "\n"
        self.HMP4040.write("*IDN?")  # check the instrument identification.
        idn = self.HMP4040.read()
        print("IDN:", idn)
        # need to enable the VI_ATTR_TERMCHAR_EN = 1 (and/or VI_ATTR_SUPPRESS_END_EN=0) to see a quick response.
        self.HMP4040.set_visa_attribute(
            visa.constants.VI_ATTR_TERMCHAR_EN, True
        )  # Set the state of an attribute.
        attr = self.HMP4040.get_visa_attribute(
            visa.constants.VI_ATTR_TERMCHAR_EN
        )  # Retrieves the state of an attribute in this resource.
        print("Attrib. TERMCHAR_EN:", attr)
        self.HMP4040.set_visa_attribute(visa.constants.VI_ATTR_SUPPRESS_END_EN, False)
        attr = self.HMP4040.get_visa_attribute(visa.constants.VI_ATTR_SUPPRESS_END_EN)
        print("Attrib. SUPPRESS_END_EN:", attr)
        print()

    def command(self, topic: str, message: Union[bytes, float, int]) -> None:
        device, cmd, command, channel = topic.split("/")[1:]
        if cmd != "cmd":
            raise ValueError("command messages should be of the form /device/cmd/#")
        commands = ["switch", "setv"]
        if device != self.name:
            raise ValueError("wrong hv! ", device, self.name)
        nchannel = int(channel)
        if command == "switch":
            # Channel selection commands INSTrument: Select (NSEL)
            cmd = "INST:NSEL " + channel  # selects a channel on LV device
            print(f"CMD to select a channel in LV {cmd}")
            self.HMP4040.write(cmd)
            self.HMP4040.write("INST:NSEL?")  # queries number of the channel selection
            Channel_hmp = self.HMP4040.read()
            print("Channel  :  ", Channel_hmp)
            lv_channel_state = 0
            message = message.decode("utf-8")
            if message == "on":
                self.channels[nchannel].on = True
                lv_channel_state = 1
            elif message == "off":
                self.channels[nchannel].on = False
                lv_channel_state = 0
            else:
                msg = "can only switch on or off"
                raise ValueError(msg)
            # OUTPut commands for activating the output channels.
            cmd = "OUTP " + str(int(lv_channel_state))
            print(
                f"CMD for activating the output of the selected channel on LV : {cmd}"
            )
            self.HMP4040.write(cmd)  # enter the data into the HMP4040
            self.HMP4040.write("OUTP?")  # queries the output state
            Status = self.HMP4040.read()  # read output
            print("Status : ", Status)

        elif command == "setv":
            cmd = "INST:NSEL " + channel  # selects a channel on LV device
            # print(f"CMD to select a channel in LV {cmd}")
            self.HMP4040.write(cmd)
            self.HMP4040.write("INST:NSEL?")  # select channel
            Channel_hmp = self.HMP4040.read()
            print("Channel  :  ", Channel_hmp)
            # print(message)
            # VOLTage: Configuring the output voltage
            cmd = "VOLT " + str(float(message))
            print(f"CMD to set the Voltage for selected channel in LV: {cmd}")
            self.HMP4040.write(cmd)
            # self.HMP4040.write("MEAS:VOLT?")
            self.HMP4040.write("VOLT?")  # check voltage on selected channel
            V = self.HMP4040.read()
            print("V : ", V)
            self.channels[nchannel].vreq = float(V)  # send command
        else:
            raise ValueError("only possible commands are", commands)

    def status(self):
        """TODO: Write unittest"""
        print("!!--------------------------------------------!!")
        # loop on each channel and read/write volt/curr/status of them
        for ch in range(self.num_of_channels - 1):

            var1 = "INST:NSEL "
            var2 = var1 + str(ch + 1)
            # print(var2)
            self.HMP4040.write(var2)
            self.HMP4040.write("INST:NSEL?")  # Queries number of the channel selection
            Channel_hmp = self.HMP4040.read()
            print("Channel  :  ", Channel_hmp)
            self.channels[ch + 1].number = int(Channel_hmp)
            # MEAS: VOLT/CURR :Measurement commands= queries the current/voltage value of the selected channel
            self.HMP4040.write(
                "MEAS:VOLT?"
            )  # Queries the voltage value of the selected channel.
            V = self.HMP4040.read()
            print("V : ", V)
            self.channels[ch + 1].vreq = float(V)

            self.HMP4040.write(
                "MEAS:CURR?"
            )  # Queries the current value of the selected channel.
            I = self.HMP4040.read()
            print("I : ", I)

            self.HMP4040.write("OUTP?")  # Queries the output state of the channels
            State = self.HMP4040.read()
            print("State : ", State)
            self.channels[ch + 1].on = int(State)

        status_channels = []
        for channel in self.channels:
            status_channels.append(
                {
                    "number": channel.number,
                    "on": int(channel.on),  # issue with bools in telegraf/influxdb
                    "vreq": channel.vreq,
                }
            )
        print("!!--------------------------------------------!!")
        return status_channels


def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(f"/{client.device.name}/cmd/#")


def on_message(client, userdata, msg):
    print("recv", msg.topic, msg.payload)
    client.device.command(msg.topic, msg.payload)


def run(device, mqtt_host):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.device = device
    client.connect(mqtt_host, 1883, 60)
    client.loop_start()
    while 1:
        client.publish("/{}/status".format(device.name), json.dumps(device.status()))
        time.sleep(4)
    time.sleep(4)
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    import sys

    device_name, mqtt_host = sys.argv[1:]
    device = HMP(device_name)
    run(device, mqtt_host)
