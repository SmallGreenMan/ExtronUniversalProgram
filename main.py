from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
                                 DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
                                 EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
                                 RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
                                 VolumeInterface)
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import Clock, MESet, Timer, Wait, ProgramLog, RFile, File

import json
import jsonVav

import Global as gl
import Devices as dev


print(Version())
ProgramLog('------- Controller Online ---------', 'info')

# -------------------------------- Data/File -----------------------------------
FileName = 'ConfigData'

readMasterDataFromFileFlag = True
debugFlag = False


def ReadFile():
    if File.Exists(FileName):
        dev.SendDataToClients('\n >>>>>>>>>>>>>>>>> Try to Read Config file <<<<<<<<<<<<<<<<<<<<<<<<<< \n')
        ProgramLog('\n >>>>>>>>>>>>>>>>> Config file Loaded, Program started OK <<<<<<<<<<<<<<<<<<<<<<<<<< \n', 'info')

        str1 = gl.Read(FileName)
        dev.SendDataToClients('\nFile data is\n')
        dev.SendDataToClients('\n'+str1+'\n')


        if readMasterDataFromFileFlag:
            gl.masterData = jsonVav.vavJson(json.loads(jsonVav.remoweComents(str1)))

            ProgramLog('\n >>>>>>>>>>>>>>>>> RoomName '+ str(gl.masterData['RoomName']) +' <<<<<<<<<<<<<<<<<<<<<<<<<< \n', 'info')

            ProgramLog('\n\nmasterData', 'info')
            ProgramLog(str(gl.masterData), 'info')

            gl.PpData = gl.masterData['PpData']
            gl.TesiraData = gl.masterData['TesiraData']

        StartAllModules()

        dev.SendDataToClients('\n >>>>>>>>>>>>>>>>> Config file Loaded, Program started OK <<<<<<<<<<<<<<<<<<<<<<<<<< \n')
        ProgramLog('\n >>>>>>>>>>>>>>>>> Config file Loaded, Program started OK <<<<<<<<<<<<<<<<<<<<<<<<<< \n', 'info')
    else:
        dev.SendDataToClients('\n >>>>>>>>>>>>>>>>> Config file doesn`t exist <<<<<<<<<<<<<<<<<<<<<<<<<< \n')
        ProgramLog('\n >>>>>>>>>>>>>>>>> Config file doesn`t exist <<<<<<<<<<<<<<<<<<<<<<<<<< \n', 'info')

# ------------------------------------------ START PROGRAM ------------------------------------
def Initialize():
    global FileName

    dev.startServer()

    for t in File.ListDir(''):
        dev.SendDataToClients('File name is: '+ t)
        ProgramLog('File name is: '+ t, 'info')
        if t[:10] == 'ConfigData':
            FileName = t

    if File.Exists(FileName):
        ReadFile()

def StartAllModules():
    dev.SendDataToClients('\n StartAllModules \n')
    ProgramLog('\n StartAllModules \n', 'info')

    import PP

    @Wait(0)
    def start0():
        PP.PpControlModule(dev.TPs)
        ProgramLog('\n\n PpControlModule started\n\n', 'info')

    @Wait(1)
    def start1():
        import Tesira
        Tesira.TesiraModule(dev.TPs, gl.TesiraData)
        ProgramLog('\n\n TesiraModule started\n\n', 'info')

    @Wait(2)
    def start2():
        import Navigator
        Navigator.NavInit(dev.TPs, gl.VideoComData)
        ProgramLog('\n\n navigator started\n\n', 'info')

    if "CamModule" in gl.masterData["Imports"]:
        @Wait(3)
        def start3():
            import CamModule
            CamModule.CamInit(dev.TPs, gl.CamData)
            ProgramLog('\n\n Cameras module started\n\n', 'info')

    if "gs_projectors" in gl.masterData["Imports"]:
        gl.ProjData = gl.masterData #["ProjData"]['Devices']
        @Wait(4)
        def start4():
            if not debugFlag:
                import gs_projectors
                gs_projectors.Initialize(gl.ProjData)
                ProgramLog('\n\n ProjectorsModule started\n\n', 'info')

    if "gs_Led" in gl.masterData["Imports"]:
        gl.LedsData = gl.masterData["LedsData"]['Devices']
        @Wait(5)
        def start5():
            if not debugFlag:
                import gs_Led
                gs_Led.Initialize(gl.LedsData)
                ProgramLog('\n\n LedModule started\n\n', 'info')

    if "gui_WatchOut" in gl.masterData["Imports"]:
        @Wait(6)
        def start6():
            if not debugFlag:
                import gui_WatchOut
                gui_WatchOut.Initialize()
                ProgramLog('\n\n GuiWatchout started\n\n', 'info')

    if "gs_dtp204t" in gl.masterData["Imports"]:
        gl.DtpData = gl.masterData['DtpData']['Devices']
        @Wait(7)
        def start7():
            if not debugFlag:
                import gs_dtp204t
                gs_dtp204t.Initialize(gl.DtpData)
                ProgramLog('\n\n Dtp204t started\n\n', 'info')

    if "gs_WatchOut" in gl.masterData["Imports"]:
        gl.WatchoutData = gl.masterData['WatchoutData']
        @Wait(8)
        def start8():
            if not debugFlag:
                import gs_WatchOut
                gs_WatchOut.Initialize(gl.WatchoutData)
                ProgramLog('\n\n GsWatchout started\n\n', 'info')

    if "gs_dataServ" in gl.masterData["Imports"]:
        gl.DDServData = gl.masterData['DDServData']['Devices']
        @Wait(9)
        def start9():
            if not debugFlag:
                import gs_dataServ
                gs_dataServ.Initialize(gl.DDServData)
                ProgramLog('\n\n Dynamic Data Servers started\n\n', 'info')

    if "gs_Codec_Vcs_Granat_C4" in gl.masterData["Imports"]:
        gl.VcsData = gl.masterData['VcsData']['Devices'][0]
        @Wait(10)
        def start10():
            if not debugFlag:
                import gs_Codec_Vcs_Granat_C4
                gs_Codec_Vcs_Granat_C4.Initialize(gl.VcsData)
                ProgramLog('\n\n gs_Codec_Vcs_Granat_C4 started\n\n', 'info')

    if "smp352" in gl.masterData["Imports"]:
        gl.Smp352Data = gl.masterData['Smp352Data']['Devices']
        @Wait(11)
        def start11():
            if not debugFlag:
                import smp352
                smp352.Initialize(gl.Smp352Data)
                ProgramLog('\n\n smp352 started\n\n', 'info')

    if "gs_screen_kauber" in gl.masterData["Imports"]:
        gl.ScreenData = gl.masterData['screenData']['Devices']
        @Wait(12)
        def start12():
            if not debugFlag:
                import gs_screen_kauber
                gs_screen_kauber.Initialize(gl.ScreenData)
                ProgramLog('\n\n Kauber started\n\n', 'info')

    if "gs_wb_ms_v2" in gl.masterData["Imports"]:
        gl.SensorsData = gl.masterData['SensorsData']['Devices']
        @Wait(12)
        def start13():
            if not debugFlag:
                import gs_wb_ms_v2
                gs_wb_ms_v2.Initialize(gl.SensorsData)
                ProgramLog('\n\n Sensors started\n\n', 'info')

    if "gs_artur_holm_monitors" in gl.masterData["Imports"]:
        gl.ArturHolmData = gl.masterData['ArturHolmData']['Devices']
        @Wait(13)
        def start14():
            if not debugFlag:
                import gs_artur_holm_monitors
                gs_artur_holm_monitors.Initialize(gl.ArturHolmData)
                ProgramLog('\n\n Artur Holm started\n\n', 'info')

    @Wait(14)
    def start15():
        if not debugFlag:
            gl.JupiterData = gl.masterData['JupiterData']['Devices']
            import gs_jupiter
            gs_jupiter.Initialize(gl.JupiterData)
            ProgramLog('\n\n Jupiter started\n\n', 'info')

    if "MicClocAudio" in gl.masterData["Imports"]:
        gl.CamData = gl.masterData['CamData']
        @Wait(4.5)
        def start16():
            import MicClocAudio
            MicClocAudio.MicInit(dev.TPs, gl.MicData)
            ProgramLog('\n\n MicClocAudio started\n\n', 'info')

    if "ShureCeiling" in gl.masterData["Imports"]:
        gl.ShureData = gl.masterData['ShureData']
        @Wait(4.5)
        def start17():
            import ShureCeiling
            ShureCeiling.ShureModule(gl.ShureData)
            ProgramLog('\n\n ShureCeiling started\n\n', 'info')

    if "DocCam" in gl.masterData["Imports"]:
        gl.DocCamData = gl.masterData['DocCam']
        @Wait(15)
        def start16():
            import DocCam
            DocCam.DocCamModule(dev.TPs, gl.DocCamData)
            ProgramLog('\n\n DocCam started\n\n', 'info')

@Wait(2)
def start():
    Initialize()
