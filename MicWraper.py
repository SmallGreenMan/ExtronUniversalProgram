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
import re

from Devices import SendDataToClients

import VariableTrase

patternAllMic = re.compile(b'ACK QUERY PP1=(?P<a>ON|OFF) PP2=(?P<b>ON|OFF) PP3=(?P<c>ON|OFF) PP4=(?P<d>ON|OFF) ID=OFF')
patternSingleMic = re.compile(b'BSTATUS B(?P<mic>[\d]{1,2})=(?P<state>[\d]{1,2})')


def MicWraperInit(Data, Tracer):

    Data['DV'] = EthernetClientInterface(Data['IP'], IPPort = 49494, Protocol = 'UDP', ServicePort = 0)
    Data['DV_FB'] = EthernetClientInterface(Data['IP'], IPPort = Data['Port'], Protocol = 'UDP', ServicePort = Data['Port'])

    @event(Data['DV_FB'], 'ReceiveData')
    def handleRecvData(interface, data):
        SendDataToClients('------- Mic2 '+str(Data['dvName'])+' ReceiveData Event = ' + data)

        m = {
            '1': b'ON',
            '2': b'OFF'
        }

        machPatern = patternSingleMic.search(data)
        if machPatern:
            Tracer.Set({
                'mic': int(machPatern.group('mic')),
                'state': m[machPatern.group('state')]
            })

    @event(Data['DV'], 'ReceiveData')
    def handleRecvData(interface, data):
        SendDataToClients('------- Mic '+str(Data['dvName'])+' ReceiveData Event = ' + str(data))

        machPatern = patternAllMic.search(data)
        if machPatern:
            mic = {}
            mic[0] = machPatern.group('a')
            mic[1] = machPatern.group('b')
            mic[2] = machPatern.group('c')
            mic[3] = machPatern.group('d')

            for k in mic.keys():
                if Data['micPositions'][k] > 0:
                    Tracer.Set({
                        'mic': int(Data['micPositions'][k]),
                        'state': mic[k]
                    })

    def Initialize():
        Data['DV'].Send('QUERY\r')

    Initialize()
