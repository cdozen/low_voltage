import pyvisa as visa
import os


def load_env_file():
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r") as file:
            for line in file:
                key, value = line.strip().split("=", 1)
                os.environ[key] = value


load_env_file()  # Load environment variables from .env file

rm = visa.ResourceManager("/usr/lib64/librsvisa.so@ivi")
HMP4040_IP = os.environ.get("HMP_IP")
HMP4040_PORT = os.environ.get("HMP_PORT")
HMP4040 = rm.open_resource(f"TCPIP::{HMP4040_IP}::{HMP4040_PORT}::SOCKET")
HMP4040.read_termination = "\n"
HMP4040.write_termination = "\n"
HMP4040.write("*IDN?")
idn = HMP4040.read()
print("IDN:", idn)

# Rest of your code below...
HMP4040.write("INST:NSEL 1")
HMP4040.write("INST:NSEL?")
Channel = HMP4040.read()
print("Channel  :  ", Channel)
HMP4040.write("MEAS:VOLT?")
V1 = HMP4040.read()
print("V1 : ", V1)
HMP4040.write("MEAS:CURR?")
I1 = HMP4040.read()
print("I1 : ", I1)
print()

HMP4040.write("INST:NSEL 2")
HMP4040.write("INST:NSEL?")
Channel = HMP4040.read()
print("Channel  :  ", Channel)
HMP4040.write("MEAS:VOLT?")
V2 = HMP4040.read()
print("V2 : ", V2)
HMP4040.write("MEAS:CURR?")
I2 = HMP4040.read()
print("I2 : ", I2)
print()

HMP4040.write("INST:NSEl 3")
HMP4040.write("INST:NSEL?")
Channel = HMP4040.read()
print("Channel  :  ", Channel)
HMP4040.write("MEAS:VOLT?")
V3 = HMP4040.read()
print("V3 : ", V3)
HMP4040.write("MEAS:CURR?")
I3 = HMP4040.read()
print("I3 : ", I3)
print()

HMP4040.write("INST:NSEL 4")
HMP4040.write("INST:NSEL?")
Channel = HMP4040.read()
print("Channel  :  ", Channel)
HMP4040.write("MEAS:VOLT?")
V4 = HMP4040.read()
print("V4 : ", V4)
HMP4040.write("MEAS:CURR?")
I4 = HMP4040.read()
print("I4 : ", I4)
print()

HMP4040.close()
