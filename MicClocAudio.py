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

from CamModule import recallPresset

import MicWraper

import VariableTrase

tracer = VariableTrase.VariableTraseClass(0)

stack = []

notifyWait = None

DelayCamEvent = 0.2

def MicInit(TPs, Data):
    global tracer

    def notifyCamEvent():
        global stack
        global notifyWait

        notifyWait = None
        SendDataToClients('=stack=='+ str(stack)+'\n')
        if len(stack) > 0:
            p = stack[-1]
        else:
            p = 0
        SendDataToClients('--> autoCam presset event = '+ str(p)+'\n')

        recallPresset(p)

    def waitCamEvent():
        global notifyWait

        if notifyWait != None:
            notifyWait.Cancel()
        notifyWait = Wait(DelayCamEvent, notifyCamEvent)

    def addToStack(n):
        global stack
        if n not in stack:
            stack.append(n)

    def removeFromStack(n):
        global stack
        if n in stack:
            stack.remove(n)

    def TraceEventHandler():
        global stack
        micData = tracer.Get()
        if micData['state'] == b'ON':
            addToStack(micData['mic'])
        else:
            removeFromStack(micData['mic'])
        waitCamEvent()

    tracer.Trace(TraceEventHandler)

    for k in Data['Devices'].keys():
        MicWraper.MicWraperInit(Data['Devices'][k], tracer)

