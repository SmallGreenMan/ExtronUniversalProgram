## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (ContactInterface, DigitalIOInterface,
                                 EthernetClientInterface, EthernetServerInterfaceEx, FlexIOInterface,
                                 IRInterface, RelayInterface, SerialInterface, SWPowerInterface,
                                 VolumeInterface)
from extronlib.ui import Button, Knob, Label, Level
from extronlib.system import Clock, MESet, Wait

class VariableTraseClass:
    def __init__(self, v):
        self.v=v
        self.command=None
    def Set(self, v):
        self.v=v
        if self.command!=None:
            self.command()
    def Get(self):
        return self.v
    def Trace(self, command):
        self.command=command