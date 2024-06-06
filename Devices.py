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

Processor = ProcessorDevice('ProcessorAlias')

TP1 = UIDevice('TP_1')
TP2 = UIDevice('TP_2')

TPs = [TP1, TP2]

DV_Nav = None


# ------------------------------ console ------------------------------
VavServ = EthernetServerInterfaceEx(10000, 'TCP')
VavInterfeses = [VavServ]


# --------------------------------------------- VAV VDV Server -----------------------------------------
def SendDataToClients(cmd):
    for interfes in VavInterfeses:
        if interfes.Clients:
            for client in interfes.Clients:
                client.Send(cmd)
                print(cmd)


def startServer():
    flag = 0
    for srv in VavInterfeses:
        if srv.StartListen() != 'Listening':
            print('Port unavailable')
            flag = 1
    if flag == 1:
        Wait(1, startServer)


@event(VavInterfeses, 'ReceiveData')
def HandleReceiveData(interface, rcvString):
    interface.Send('\nResiving data ok\n')
    cmd = rcvString.decode()

    if 'get nav' in cmd:
        Value = str(DV_Nav.ReadStatus('ConnectionStatus'))
        interface.Send('ConnectionStatus = '+ str(Value) +'\n')

        DV_Nav.Update('PartNumber')
        PartNumber = DV_Nav.ReadStatus('PartNumber', None)

        interface.Send('PartNumber = '+ str(PartNumber) +'\n')

    elif 'read file' in cmd:
        ReadFile()

