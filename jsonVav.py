## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
                                 DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
                                 EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
                                 RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
                                 VolumeInterface)
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import Clock, MESet, Timer, Wait, ProgramLog

from Devices import SendDataToClients

import re

comment_pattern = re.compile('(\/\/[^\n]*|\/\*.*?\*\/)')

def vavJson(data):
    new = {}
    for k in data.keys():
        if k == 'PpData':
            new[k] = ppObject(data[k])
        elif k == 'TesiraData':
            new[k] = tesiraObject(data[k])
        else:
            new[k] = data[k]

    return new

def tesiraObject(data):
    new = {}
    for k in data.keys():
        if k == 'chanels':
            new[k] = ppObject(data[k])
        else:
            new[k] = data[k]
    return new

def ppObject(pp):
    new = {}
    for k in pp.keys():
        new[int(k)] = pp[k]
    return new


def remoweComents(data):
    return re.sub(comment_pattern, '', data)
