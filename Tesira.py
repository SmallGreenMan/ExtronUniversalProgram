## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
                                 DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
                                 EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
                                 RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
                                 VolumeInterface)
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import Clock, MESet, Wait, ProgramLog
import array
import connection_handler_dc as ch
from ConnectionHandler import GetConnectionHandler
import re

from Devices import SendDataToClients


DV_CH = None
DV = None

Max_Level = 0
Min_Level = 0

PatternFbLevel = re.compile('! "publishToken":"VAV_LVL(?P<index>[0-9]{1,3})" "value":(?P<value>[-,0-9]{1,9})')
PatternFbMute  = re.compile('! "publishToken":"VAV_MUTE(?P<index>[0-9]{1,3})" "value":(?P<value>[-,0-9]{1,9}|false|true)')


maxLevels = 0

MuteFB = None
levelFB = None

Buff = ''
ButtonsId = {}

BtnsShiftMute = 0
BtnsShiftUp = 100
BtnsShiftDown = 200
BtnsShiftText = 400
BtnsShiftLevel = 500
BtnsShiftName = 600

def SetAudioCrossCommutation(commutationData):
    global DV
    for d in commutationData:
        DV.Send('Mixer1 set crosspointLevelState '+str(d['inp'])+' '+str(d['out'])+' '+str(d['cross'])+'\r')
        SendDataToClients('----> to Tesira crosspoint: Mixer1 set crosspointLevelState '+str(d['inp'])+' '+str(d['out'])+' '+str(d['cross'])+'\т')


def TesiraModule(TPs, Data):

    global DV
    global DV_CH
    global MuteFB
    global levelFB
    global ButtonsId

    maxLevels = len(Data['chanels'])
    bShift = int(Data['buttonShift'])

    MuteFB = [0] * (maxLevels+1)
    levelFB = [0] * (maxLevels+1)

    DV = EthernetClientInterface(Data['ip'], 23)
    DV_CH = ch.StandardConnectionHandler(DV , 'DEVICE get ipConfig control\n', polling_interval=10)

    BtnAudioMute = []
    BtnAudioUp = []
    BtnAudioDown = []
    BtnAudioLevel = []
    BtnText = []
    BtnName = []

    n = 0
    for i in Data['chanels'].keys():
        ButtonsId[i] = n
        n = n + 1

    for tp in TPs:
        BtnsM = [Button(tp, ID + bShift + BtnsShiftMute) for ID in Data['chanels'].keys()]
        BtnAudioMute.append(BtnsM)
        BtnsU = [Button(tp, ID + bShift + BtnsShiftUp) for ID in Data['chanels'].keys()]
        BtnAudioUp.append(BtnsU)
        BtnsD = [Button(tp, ID + bShift + BtnsShiftDown) for ID in Data['chanels'].keys()]
        BtnAudioDown.append(BtnsD)
        BtnsT = [Label(tp, ID + bShift + BtnsShiftText) for ID in Data['chanels'].keys()]
        BtnText.append(BtnsT)
        BtnsN = [Label(tp, ID + bShift + BtnsShiftName) for ID in Data['chanels'].keys()]
        BtnName.append(BtnsN)

        BtnsL = [Slider(tp, ID + bShift + BtnsShiftLevel) for ID in Data['chanels'].keys()]
        for b in BtnsL:
            b.SetRange(int(Data['TesiraMinLevel']),int(Data['TesiraMaxLevel']),1)
        BtnAudioLevel.append(BtnsL)

    Data['buttons'] = {
        'mute':  BtnAudioMute,
        'up':    BtnAudioUp,
        'down':  BtnAudioDown,
        'level': BtnAudioLevel,
        'text':  BtnText,
        'name':  BtnName,
    }

    @event(DV_CH, 'ReceiveData')                                  #--------RECEIVE DATA -----------#
    def Dev_Audio_ReciveData(interface, rcvString):
        SendDataToClients('--- Tesira --- resiving data is:{}\n'.format(rcvString))
        if b'\xFF\xFD\x18\xFF\xFD\x20\xFF\xFD\x23\xFF\xFD\x27\xFF\xFD\x24' in rcvString:
            DV.Send(b'\xFF\xFC\x18\xFF\xFC\x20\xFF\xFC\x23\xFF\xFC\x27\xFF\xFC\x24')
        elif b'\xFF\xFB\x03\xFF\xFD\x01\xFF\xFD\x22\xFF\xFD\x1F\xFF\xFB\x05\xFF\xFD\x21' in rcvString:
            DV.Send(b'\xFF\xFE\x03\xFF\xFC\x01\xFF\xFC\x22\xFF\xFC\x1F\xFF\xFE\x05\xFF\xFC\x21')
        elif b'\xFF\xFB\x01\xFF\xFD\x06\xFF\xFD\x00' in rcvString:
            DV.Send(b'\xFF\xFE\x01\xFF\xFC\x06\xFF\xFC\x00')
        elif b'\xFF\xFB\x03\xFF\xFB\x01' in rcvString:
            DV.Send(b'\xFF\xFE\x03\xFF\xFE\x01')

        elif b'login:' in rcvString:
            DV.Send(Login)
            SendDataToClients('---to Tesira --- login is:{}\n'.format(Login))
        elif b'Password:' in rcvString:
            DV.Send(Password)
            SendDataToClients('---to Tesira --- Password is:{}\n'.format(Password))
            DV.Send(password + '\r\n')

        elif b'Welcome to the Tesira Text Protocol Server' in rcvString:
            @Wait(5)
            def GetLevelUnsubscribe():
                Set_Level_Unsubscribe()
            @Wait(10)
            def GetMuteUnsubscribe():
                Set_Mute_Unsubscribe()
            @Wait(15)
            def GetLevelSubscribe():
                Set_Level_Subscribe()
            @Wait(20)
            def GetMuteSubscribe():
                Set_Mute_Subscribe ()
        if b'\r\n' in rcvString:
            global Buff
            Buff = Buff + rcvString.decode()
            FbAudio ()

    @event(DV_CH, ['Connected', 'Disconnected'])
    def DV_CH_connection_status(interface, state):
        ProgramLog('------- TESIRA net status = ' + str(state), 'info')
        SendDataToClients('------- TESIRA net status = ' + str(state))
        if 'Disconnected' in state:
            ProgramLog('------- TESIRA Disconnected ---------', 'info')
            print('TESIRA Disconnected')
            SendDataToClients('+++ TESIRA +++ Connection status is: Disconnected\n')
        else:
            ProgramLog('------- TESIRA Connected ---------', 'info')
            print('TESIRA Connected')
            SendDataToClients('+++ TESIRA +++ Connection status is: Connected\n')

    def Connect_Audio_Tesira():
        DV.Connect(5)

    def Set_Level_Unsubscribe ():
        for i in Data['chanels'].keys():
            DV.Send(Data['chanels'][i]['nameTag'] +' unsubscribe level '+ Data['chanels'][i]['IdChanel'] +' VAV_LVL'+ str(Data['chanels'][i]['FbBtn']) +'\r') #FbBtn
    def Set_Level_Subscribe ():
        for i in Data['chanels'].keys():
            DV.Send(Data['chanels'][i]['nameTag'] +' subscribe level '+ Data['chanels'][i]['IdChanel'] +' VAV_LVL'+ str(Data['chanels'][i]['FbBtn']) +'\r')
            DV.Send(Data['chanels'][i]['nameTag'] +' set maxLevel '+ Data['chanels'][i]['IdChanel'] +' '+ Data['TesiraMaxLevel'] +'\r')
            DV.Send(Data['chanels'][i]['nameTag'] +' set minLevel '+ Data['chanels'][i]['IdChanel'] +' '+ Data['TesiraMinLevel'] +'\r')

    def Set_Mute_Unsubscribe ():
        for i in Data['chanels'].keys():
            DV.Send(Data['chanels'][i]['nameTag'] +' unsubscribe mute '+ Data['chanels'][i]['IdChanel'] +' VAV_MUTE'+ str(Data['chanels'][i]['FbBtn']) +'\r')

    def Set_Mute_Subscribe ():
        for i in Data['chanels'].keys():
            DV.Send(Data['chanels'][i]['nameTag'] +' subscribe mute '+ Data['chanels'][i]['IdChanel'] +' VAV_MUTE'+ str(Data['chanels'][i]['FbBtn']) +'\r')

    def FbAudio ():
        global Buff
        while '\r\n' in Buff:
            poz = Buff.find('\r\n')
            Minibuff = Buff[:poz]
            Buff = Buff[poz+1:]
            machPatern = PatternFbLevel.search(Minibuff)
            machPatern2 = PatternFbMute.search(Minibuff)

            if machPatern:
                index = int(machPatern.group('index'))
                btnPossition = ButtonsId[index]
                level_value = int(machPatern.group('value'))
                print(level_value)
                global Max_Level
                global Min_Level
                Max_Level = int(Data['TesiraMaxLevel'])
                Min_Level = int(Data['TesiraMinLevel'])
                Range = Max_Level - Min_Level
                Curent = level_value - Min_Level
                Precent = round((Curent/Range)*100)
                for b in Data['buttons']['level']:
                    b[btnPossition].SetFill(level_value)

                for b in Data['buttons']['text']:
                    b[btnPossition].SetText(str(Precent))
                if level_value <= Min_Level:
                    Data['chanels'][index]['FbLevel'] = 1

                elif level_value > Min_Level:
                    Data['chanels'][index]['FbLevel'] = 0

            if machPatern2:
                index = int(machPatern2.group('index'))
                btnPossition = ButtonsId[index]
                text_value = str(machPatern2.group('value'))
                if text_value == str('false'):
                    for b in Data['buttons']['mute']:
                        b[btnPossition].SetState(1)
                        Data['chanels'][index]['FbMute'] = 0
                elif text_value == str('true'):
                    for b in Data['buttons']['mute']:
                        b[btnPossition].SetState(0)
                        Data['chanels'][index]['FbMute'] = 1


    for BtnAudioLevelMute in Data['buttons']['mute']:
        @event(BtnAudioLevelMute, 'Pressed')                                 #------- Mute_On_Off_Level---------------------#
        def BtnAudioLevelMuteEvent(button, state):
            btn = button.ID - bShift - BtnsShiftMute
            if Data['chanels'][btn]['FbMute'] == 0:
                DV.Send(Data['chanels'][btn]['nameTag'] +' set mute '+ Data['chanels'][btn]['IdChanel'] +' true\r')
            else:
                DV.Send(Data['chanels'][btn]['nameTag'] +' set mute '+ Data['chanels'][btn]['IdChanel'] +' false\r')

    def AutoMute(btn):
        global var_value
        if var_value[btn] == 1:
            DV.Send(Data['chanels'][btn]['nameTag'] +' set mute '+ Data['chanels'][btn]['IdChanel'] +' true\r')
        elif var_value[btn] == 0:
            DV.Send(Data['chanels'][btn]['nameTag'] +' set mute '+ Data['chanels'][btn]['IdChanel'] +' false\r')


    for BtnAudioLevelUp in Data['buttons']['up']:
        @event(BtnAudioLevelUp, ['Released', 'Pressed', 'Repeated'])                                 #------- Vol_Level_Up---------------------#
        def BtnAudioLevelUpEvent(button, state):
            btn = button.ID - bShift - BtnsShiftUp
            global var_value
            if state == 'Pressed' or state == 'Repeated':
                button.SetState(0)
                DV.Send(Data['chanels'][btn]['nameTag'] +' increment level '+ Data['chanels'][btn]['IdChanel'] +' 1\r')
            else:
                button.SetState(1)


    for BtnAudioLevelDown in Data['buttons']['down']:
        @event(BtnAudioLevelDown, ['Released', 'Pressed', 'Repeated'])                                 #------- Vol_Level_Down---------------------#
        def BtnAudioLevelDownEvent(button, state):
            global var_value
            btn = button.ID - bShift - BtnsShiftDown
            if state == 'Pressed' or state == 'Repeated':
                button.SetState(0)
                DV.Send(Data['chanels'][btn]['nameTag'] +' decrement level '+ Data['chanels'][btn]['IdChanel'] +' 1\r')
            else:
                button.SetState(1)

    for BtnAudioLevel in Data['buttons']['level']:
        @event(BtnAudioLevel, 'Changed')
        def BtnBtnLevel(slider, state, value):
            i = int(slider.ID) - bShift - BtnsShiftLevel
            DV.Send(Data['chanels'][i]['nameTag'] +' set level '+ Data['chanels'][i]['IdChanel'] +' '+ str(value) + '\r')


    def DisplayLevelNames():
        for t in Data['buttons']['name']:
            for b in t:
                index = b.ID - BtnsShiftName - bShift
                if (index in Data['chanels']):
                    b.SetText(Data['chanels'][index]['name'])


    def Initialize():
        DisplayLevelNames()
        Connect_Audio_Tesira()

    Initialize()