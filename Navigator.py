## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice, SPDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
                                 DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
                                 EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
                                 RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
                                 VolumeInterface)
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import Clock, MESet, Timer, Wait, ProgramLog

import extr_sm_NAVigator_v1_0_1_4 as NavModule
from Devices import SendDataToClients
import Devices as dev
import Global as gl
from Tesira import SetAudioCressCommutation

BtnOut = []
BtnIn = []
BtnInUniversal = []

MaxInputsOnPage = 40

universalBtnShift = 200
universalBtnMemory = []
ppInputActive={}

In = 0
Out = 0

fb = {}

audioComWait = None
audioComStak = []


def VideoComPresset(presset = None):
    SendDataToClients('------- VideoComPresset event, preset = ' + str(presset) + '\n')
    defoultPresset = [
        {'out': 62, 'in': 45},
        {'out': 64, 'in': 47},
        {'out': 65, 'in': 48},
        {'out': 66, 'in': 49},
    ]
    if presset == None:
        presset = defoultPresset

    for p in presset:
        if ((p['out'] in gl.VideoComData['OUT']) and (p['in'] in gl.VideoComData['INPUTS'])):
            SendDataToClients('------- VideoCom sendCommand in: ' + str(p['in']) + ', out: ' + str(p['out']) + '\n')
            dev.DV_Nav.Set('MatrixTieCommand', None, {'Input': p['in'], 'Output': p['out'], 'Tie Type':'Video'})


def NavInit(TPs, Data):
    global BtnOut
    global BtnIn
    global BtnInUniversal
    global In
    global Out

    NAVigatorDevice = SPDevice('SPD_Nav') # Alias Name of NAVigator
    dev.DV_Nav = NavModule.SPIClass(NAVigatorDevice, 'NAVigator')

    for tpId in TPs:
        BtnsOut = [Button(tpId, ID + Data['buttonShift']) for ID in Data['OUT']]
        BtnOut.append(BtnsOut)
        BtnsIn = [Button(tpId, ID + Data['buttonShift']) for ID in Data['INPUTS']]
        BtnIn.append(BtnsIn)
        BtnsUni = [Button(tpId, ID + Data['buttonShift'] + universalBtnShift + 1, holdTime = 2) for ID in range(MaxInputsOnPage)]
        BtnInUniversal.append(BtnsUni)

    def ConnectionStatusHandler(command, value, qualifier):
        ProgramLog('------- Navigator net status = ' + str(command) + ' ' + str(value) + ' ' + str(qualifier), 'info')

    '''
    ---------------------------------   out
        'audio':{
            'out': [41], 
            'outStereo': [43],
            'posibleIntuts':[
                41, 42, 43, 44, 45, 46, 47, 50,
                54, 55, 
                51, 
                31, 33,
                35, 37
                ],
            'posibleIntutsStereo':[
                41, 42, 43, 44, 45, 46, 47, 50,
                54, 55,
                51, 
                32, 34,
                36, 38
                ]
            }
    ---------------------------------   inp
        'audio':{
            'input': [35,37], 
            'inputStereo': [36,38], 
            }
    '''

    def SetAudioRow(out, posibleIntuts, inputs):
        cmd = []
        for inp in posibleIntuts:
            if inp not in inputs:
                cmd.append({
                    'out': out,
                    'inp': inp,
                    'cross': 'false'
                })
        for inp in inputs:
            cmd.append({
                'out': out,
                'inp': inp,
                'cross': 'true'
            })
        SetAudioCressCommutation(cmd)


    def SetAudionCommutation():
        global audioComStak
        global fb
        while(len(audioComStak)):
            out = audioComStak.pop()
            inp = fb[out]
            if 'audio' in Data['OUT'][out] and 'audio' in Data['INPUTS'][inp]:
                outAudionData = Data['OUT'][out]['audio']
                inpAudionData = Data['INPUTS'][inp]['audio']
                if 'outStereo' in outAudionData:
                    SetAudioRow(outAudionData['out'][0], outAudionData['posibleIntuts'], inpAudionData['input'])
                    if 'inputStereo' in inpAudionData:
                        inpSteret = inpAudionData['inputStereo']
                    else:
                        inpSteret = inpAudionData['input']
                    SetAudioRow(outAudionData['outStereo'][0], outAudionData['posibleIntutsStereo'], inpSteret)
                else:
                    inpSteret = inpAudionData['input']
                    if 'inputStereo' in inpAudionData:
                        inpSteret.append(inpAudionData['input'])
                    SetAudioRow(outAudionData['out'][0], outAudionData['posibleIntuts'], inpAudionData['input'])


    def OutputTieStatusHandler(command, value, qualifier):
        global audioComWait
        global audioComStak
        global fb
        input = value
        output = int(qualifier['Output'])
        if (qualifier['Tie Type'] == 'Video'):
            fb[output] = input
            if output not in audioComStak:
                audioComStak.append(output)
            if audioComWait:
                audioComWait.Cancel()
                audioComWait = None
            audioComWait = Wait(1, SetAudionCommutation)

            if ((output in Data['OUT']) and (input in Data['INPUTS'])):
                if ('textFb' in Data['OUT'][output]):
                    for t in BtnOut:
                        for b in t:
                            if (b.ID - Data['buttonShift'] == output):
                                b.SetText(Data['INPUTS'][input]['Name'])


    # ----------------------- Buttons -------------------------------

    def displayInputsName(inputs, PanelIndex):
        i = 0
        l = len(inputs)
        for b in BtnInUniversal[PanelIndex]:
            if (i < l):
                index = inputs[i]
                if (index in Data['INPUTS']):
                    b.SetText(Data['INPUTS'][index]['Name'])
                else:
                    b.SetText('')
            else:
                b.SetText('')
            i = i + 1


    '''
    masterData = {
	   "RoomName": "29",
	   
	   {
            'Name': 'Recoder',
            'flaxibleInputs': True,
            'Inputs': {
                '29': [
                    13, 24, 26, 27, 28, 29, 30, 31, 32, 14, 
                    15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 
                    45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 
                    34, 35, 42, 33, 37, 3, 4
                ],
                '30': [50, 46, 34, 35, 36, 42, 43, 38, 39, 10, 11, 12, 40, 41, 5, 6, 7, 44, 8, 9],
                '31': [
                    13, 24, 26, 27, 28, 29, 30, 31, 32, 14, 
                    15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 
                    45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 
                    34, 35, 42, 38, 39, 10, 11, 12, 44, 8, 9
                ],
            },
            'ConnectionType':[],
            'InputPP': {
                '29': 'Pp.5_GroupsInputs_4',
                '30': 'Pp.5_GroupsInputsForRecorder_31_30',
                '31': 'Pp.5_GroupsInputsForRecorder_31_31',
            },
            'textFb':True,
        },	
        
    '''
    for bt in BtnOut:
        @event(bt, ['Tapped','Released','Pressed'])
        def BtnOutEvent(button, state):
            global In
            global Out
            global universalBtnMemory
            global ppInputActive

            PanelIndex = TPs.index(button.Host)
            ButIndex = button.ID - Data['buttonShift']
            SendDataToClients('Navigator out event '+str(ButIndex)+'\n')

            if state == 'Pressed':
                if 'flaxibleInputs' in Data['OUT'][ButIndex]:
                    room = gl.masterData['RoomName']
                    pp = Data['OUT'][ButIndex]['InputPP'][room]
                    universalBtnMemory = Data['OUT'][ButIndex]['Inputs'][room]
                else:

                    if ('InputPP' in Data['OUT'][ButIndex]):
                        pp = Data['OUT'][ButIndex]['InputPP']
                    else:
                        pp = Data['InputsPP'][0]
                    universalBtnMemory = Data['OUT'][ButIndex]['Inputs']

                ppInputActive[PanelIndex] = pp

                TPs[PanelIndex].ShowPopup(pp)
                Out = ButIndex

                displayInputsName(universalBtnMemory, PanelIndex)

    for bt in BtnIn:
        @event(bt, ['Tapped','Released','Pressed'])
        def BtnInEvent(button, state):
            global In
            global Out
            global ppInputActive
            PanelIndex = TPs.index(button.Host)
            ButIndex = button.ID - Data['buttonShift']
            SendDataToClients('-- Video Com event: out = '+str(Out)+', In = '+str(In)+' \n')

            if state == 'Pressed':
                TPs[PanelIndex].HidePopup(ppInputActive[PanelIndex])
                In = ButIndex
                dev.DV_Nav.Set('MatrixTieCommand', None, {'Input': In, 'Output': Out, 'Tie Type':'Video'})

    def comutationAdditionalInputs(input, output):
        if ('AdditionalOut' in Data['OUT'][output]) and (('AdditionalInput' in Data['INPUTS'][input])):
            if (len(Data['OUT'][output]['AdditionalOut']) > 0):
                if (len(Data['INPUTS'][input]['AdditionalInput']) > 0):
                    inp = Data['INPUTS'][input]['AdditionalInput'][0]
                    out = Data['OUT'][output]['AdditionalOut'][0]
                    dev.DV_Nav.Set('MatrixTieCommand', None, {'Input': inp, 'Output': out, 'Tie Type':'Video'})
                    SendDataToClients('-- Video Com event additional inputs: out = '+str(out)+', In = '+str(inp)+' \n')

    def comutationUsb(input, output):
        if ('ConnectionType' in Data['OUT'][output]) and (('ConnectionType' in Data['INPUTS'][input])):
            if ('usb' in Data['OUT'][output]['ConnectionType']):
                if ('usb' in Data['INPUTS'][input]['ConnectionType']):
                    dev.DV_Nav.Set(
                        'USBMatrixTieCommand', None,
                        {
                            'Device I/O Number': input,
                            'Device Type':'Output',
                            'Host I/O Number': output,
                            'Host Type': 'Input'
                        })
                    SendDataToClients('-- Video Com event USB: out = '+str(output)+', In = '+str(input)+' \n')

    for bt in BtnInUniversal:
        @event(bt, ['Tapped','Held'])
        def BtnInEvent(button, state):
            global Inц
            global Out
            global universalBtnMemory
            global ppInputActive
            PanelIndex = TPs.index(button.Host)
            ButIndex = button.ID - Data['buttonShift'] - universalBtnShift

            if (len(universalBtnMemory) > ButIndex-1):
                In = universalBtnMemory[ButIndex-1]
            else:
                In = 0
            SendDataToClients('-- Video Com event With BtnInUniversal: out = '+str(Out)+', In = '+str(In)+' \n')

            if state == 'Tapped':
                dev.DV_Nav.Set('MatrixTieCommand', None, {'Input': In, 'Output': Out, 'Tie Type':'Video'})

                comutationAdditionalInputs(In, Out)
                comutationUsb(In, Out)

                TPs[PanelIndex].HidePopup(ppInputActive[PanelIndex])

            elif state == 'Held':
                if (Out in Data['ThirdArmMonitors']):
                    for out in Data['ThirdArmMonitors']:
                        dev.DV_Nav.Set('MatrixTieCommand', None, {'Input': In, 'Output': out, 'Tie Type':'Video'})

                TPs[PanelIndex].HidePopup(ppInputActive[PanelIndex])


    dev.DV_Nav.SubscribeStatus('ConnectionStatus', None, ConnectionStatusHandler)
    dev.DV_Nav.SubscribeStatus('OutputTieStatus', None, OutputTieStatusHandler)

    dev.DV_Nav.Update('PartNumber')

    def SetOutNames():
        for t in BtnOut:
            for b in t:
                index = b.ID - Data['buttonShift']
                if (index in Data['OUT']):
                    if (len(Data['OUT'][index]['Name']) > 0):
                        b.SetText(Data['OUT'][index]['Name'])

    def init():
        SetOutNames()

    init()
