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

import Global as gl
from Devices import SendDataToClients
from Devices import TPs as tps
from gs_jupiter import UpdateChoise

BtnPP = []
TextPowerOff = []
memoryPage = 1


def ResetPpBtnState(panelIndex):
    bt = BtnPP[panelIndex]
    for b in bt:
        if b.ID < 10:
            b.SetState(0)


def showSupportPp(tp, ppList):
    for pp in ppList:
        tp.ShowPopup(pp)


def pageShowEvent(tp, data):
    SendDataToClients('PP page action, :' + str(data) + '\n')
    tp.ShowPage(data['page'])
    tp.HideAllPopups()
    showSupportPp(tp, data['supportPP'])
    if ('defoultPp' in data):
        panelIndex = tps.index(tp)
        tp.ShowPopup(gl.PpData[data['defoultPp']])
        for b in BtnPP[panelIndex]:
            if b.ID == data['defoultPp']:
                b.SetState(1)


def hideAllPagePP(tp, n):
    for i in range(1, 10):
        index = n * 10 + i
        if (index in gl.PpData):
            tp.HidePopup(gl.PpData[index])


def PpControlModule(TPs):
    global BtnPP
    global TextPowerOff

    for tpId in TPs:
        Btns = [Button(tpId, ID, holdTime=3) for ID in sorted(gl.PpData.keys())]
        BtnPP.append(Btns)

    def Initialize():
        SetHomePage()
        ProgramLog('\n PP Module Stor Init \n', 'info')

    def SetHomePage():
        i = 0
        for t in TPs:
            pageShowEvent(t, gl.PpData[1])
            ResetPpBtnState(i)
            i = i + 1

    # ----------------------- Buttons -------------------------------

    for bt in BtnPP:
        @event(bt, ['Tapped', 'Held', 'Released', 'Pressed'])
        def Btn1Event(button, state):
            global OffSMP
            global AutoPowerOff
            global memoryPage
            global selectedLayout

            PanelIndex = TPs.index(button.Host)

            if state == 'Tapped':
                SendDataToClients('PP action, panels ID is:' + str(PanelIndex) + ' ' + str(button.ID) + ' ' + str(button.ID // 10) + '\n')
                if PanelIndex > -1:

                    if (button.ID < 10) or (button.ID == 10000):
                        if ('saveToMemory' in gl.PpData[button.ID]):
                            memoryPage = button.ID
                        pageShowEvent(TPs[PanelIndex], gl.PpData[button.ID])
                        ResetPpBtnState(PanelIndex)
                        button.SetState(1)

                    elif button.ID == 10:
                        pageShowEvent(TPs[PanelIndex], gl.PpData[memoryPage])

                    elif button.ID == 102:
                        TPs[PanelIndex].HidePopup(gl.PpData[102])

                    elif button.ID == 100:
                        TPs[PanelIndex].ShowPopup(gl.PpData[100])

                    elif button.ID == 101:
                        TPs[PanelIndex].HidePopup(gl.PpData[100])

                    elif button.ID < 100:
                        p = button.ID // 10
                        SendDataToClients(gl.PpData[button.ID]+'\n')
                        if p in gl.PpData:
                            if 'defoultPp' in gl.PpData[p]:
                                for b in BtnPP[PanelIndex]:
                                    if b.ID == gl.PpData[p]['defoultPp']:
                                        b.SetState(0)
                                gl.PpData[p]['defoultPp'] = button.ID
                                hideAllPagePP(TPs[PanelIndex], p)
                                TPs[PanelIndex].ShowPopup(gl.PpData[button.ID])
                                button.SetState(1)

    Initialize()