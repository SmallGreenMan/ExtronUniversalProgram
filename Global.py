## Begin ControlScript Import --------------------------------------------------
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

masterData = {
    "RoomName": "29",
    "Imports":[
        "CamModule",
        "gs_projectors",
        "gs_Led",
        "gui_WatchOut",
        "gs_WatchOut",
        "gs_dtp204t",
        "gs_dataServ",
        "gs_Codec_Vcs_Granat_C4"
    ],
}

# ------------------------------ pp -------------------------------------
BtnsState = ['Tapped', 'Held', 'Released', 'Pressed']

PpData = {
    1: {
        'page': '5.Video',
        'saveToMemory': True,
        'defoultPp': 12,
        'supportPP': [
            'Pp_Header',
            'Pp_Pages',
            'Pp.5_GroupsOutputs//',
        ]
    },

    6: {
        'page': '5.Video',
        'saveToMemory': True,
        'defoultPp': 61,
        'supportPP': [
            'Pp_Header',
            'Pp_Pages',
            'Pp.5_Jupiter\'sConfig',
        ]
    },
    2: {
        'page': '6.Audio',
        'saveToMemory': True,
        'defoultPp': 21,
        'supportPP': [
            'Pp_Header',
            'Pp_Pages',
        ]
    },

    3: {
        'page': '7.Cams',
        'saveToMemory': True,
        'supportPP': [
            'Pp_Header',
            'Pp_Pages',
        ]
    },

    5: {
        'page': '8.Lighting',
        'saveToMemory': True,
        'supportPP': [
            'Pp_Header',
            'Pp_Pages',
        ]
    },
    4: {
        'page': '9.Power',
        'saveToMemory': True,
        'supportPP': [
            'Pp_Header',
            'Pp_Pages',
        ]
    },


    7: {
        'page': '3.Vcs',
        'supportPP': [
            'Pp_Header_for_vcs_page',
        ]
    },

    8: {
        'page': '2.ControlRoom(Show)',
        'supportPP': [],
        'defoultPp': 80
    },
    9: {
        'page': '4.Presentations(FromServ)',
        'supportPP': []
    },

    10:'BackToSystemControl',

    11:'Pp.5_Recording',
    12:'Pp.5_OperatorsMonitors',

    21:'Pp.6_Inputs',
    22:'Pp.6_Inputs_mic',
    23:'Pp.6_Inputs_arm',
    24:'Pp.6_Outputs',

    61:'Pp.5_VW_1',
    62:'Pp.5_VW_2',
    63:'Pp.5_VW_3',
    64:'Pp.5_VW_4',
    65:'Pp.5_VW_5',
    66:'Pp.5_VW_6',
    67:'Pp.5_VW_7',
    68:'Pp.5_VW_8',

    80: 'popScenarios',

    100:'Pp_General_Audio',

    102:'Pp.5_GroupsInputs',


    10000: {
        'page': '5.Video',
        'saveToMemory': True,
        'defoultPp': 12,
        'supportPP': [
            'Pp_Header',
            'Pp_Pages',
            'Pp.5_VideoOutputs'
        ]
    },
}

VscCallInPP = 'Modal_PP_CallIn'

RebootPP = 'Modal_PP_Reboot'


# ------ Cameras ------
CamData = {
    'buttonShift':3000,
    'numPressets':9,
    'videoOut': 122,
    'Devices': [
        {
            'ID': 1,
            'IP':'10.75.41.151',
            'login':'Admin',
            'pass':'Admin',
            'videoIn': 3
        },
        {
            'ID': 2,
            'IP':'10.75.41.152',
            'login':'Admin',
            'pass':'Admin',
            'videoIn': 4
        },
    ]
}

# ------ Tesira ------
TesiraData = {
    'ip': '10.75.42.178',
    'buttonShift': "1000",
    'levelData':{
        'levelMin': "-30",
        'levelMax': "0",
        'levelDelta': "2"
    },
    'TesiraMaxLevel': '0',
    'TesiraMinLevel': '-30',
    'chanels': {
        # --- outs
        0: {
            "name": "Main звук",
            'nameTag': 'Level150',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 0,
        },
        1: {
            "name": "Сабвуфер",
            'nameTag': 'Level151',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 1,

        },
        2: {
            "name":"Балкон",
            'nameTag': 'Level152',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 2,

        },
        3: {
            "name":"на VCS Main",
            'nameTag': 'Level115',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 3,
        },
        4: {
            "name":"на VCS резервный",
            'nameTag': 'Level116',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 4,
        },
        5: {
            "name":"Запись",
            'nameTag': 'Level136',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 5,
        },

        # --- inputs ---
        10: {
            "name":"Презентация",
            "nameTag": "Level159",
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 10,
        },
        11: {
            "name":"Контроллер",
            'nameTag': 'Level158',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 11,
        },
        12: {
            "name":"Сервер статических данных",
            'nameTag': 'Level160',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 12,
        },
        13: {
            "name":"Сервер динамических данных",
            'nameTag': 'Level161',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 13,
        },
        14: {
            "name":"Mediaplayer",
            'nameTag': 'Level85',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 14,
        },
        15: {
            "name":"VCS Main",
            'nameTag': 'Level130',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 15,
        },
        16: {
            "name":"VCS резервный",
            'nameTag': 'Level131',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 16,
        },

        # --- microfons ---
        20: {
            "name":"Микрофон 1",
            'nameTag': 'Level26',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 20,
        },
        21: {
            "name":"Микрофон 2",
            'nameTag': 'Level27',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 21,
        },
        22: {
            "name":"Микрофон 3",
            'nameTag': 'Level28',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 22,
        },
        23: {
            "name":"Микрофон 4",
            'nameTag': 'Level29',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 23,
        },
        24: {
            "name":"Микрофон 5",
            'nameTag': 'Level30',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 24,
        },
        25: {
            "name":"Микрофон 6",
            'nameTag': 'Level31',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 25,
        },
        26: {
            "name":"Микрофон 7",
            'nameTag': 'Level32',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 26,
        },
        27: {
            "name":"Микрофон 8",
            'nameTag': 'Level33',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 27,
        },

        # --- ФКЬ ---
        30: {
            "name":"АРМ 1",
            'nameTag': 'Level77',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 30,
        },
        31: {
            "name":"АРМ 2",
            'nameTag': 'Level78',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 31,
        },
        32: {
            "name":"АРМ 3",
            'nameTag': 'Level79',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 32,
        },
        33: {
            "name":"АРМ 4",
            'nameTag': 'Level80',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 33,
        },
        34: {
            "name":"АРМ 5",
            'nameTag': 'Level81',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 34,
        },
        35: {
            "name":"АРМ 6",
            'nameTag': 'Level82',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 35,
        },
        36: {
            "name":"АРМ 7",
            'nameTag': 'Level83',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 36,
        },
        37: {
            "name":"АРМ 8",
            'nameTag': 'Level84',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 37,
        },
        38: {
            "name":"АРМ 8",
            'nameTag': 'Level75',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 38,
        },
        39: {
            "name":"АРМ 8",
            'nameTag': 'Level76',
            'IdChanel': "1",
            'FbMute':0,
            'FbLevel':0,
            'FbBtn': 39,
        },

    }
}

# ------ VideoCommutation ------
VideoComData = {
    'buttonShift': 500,
    'ThirdArmMonitors': [89, 92, 95, 75, 78, 81, 85, 88],
    'OUT': {
        # --- Disperchers 29 ---
        72: {
            'Name': 'Dispercher 1\nMonitor',
            'Inputs': [13,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[83],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        83: {
            'Name': 'Dispercher 1\nMonitor 2',
            'Inputs': [24,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        89: {
            'Name': 'Dispercher 1\nMonitor 3',
            'Inputs': [21,22,23,25,34,35,2,42,43,33,37,3,4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        90: {
            'Name': 'Dispercher 2\nMonitor 1',
            'Inputs': [26,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[91],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        91: {
            'Name': 'Dispercher 2\nMonitor 2',
            'Inputs': [27,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        92: {
            'Name': 'Dispercher 2\nMonitor 3',
            'Inputs': [21,22,23,25,34,35,2,42,43,33,37,3,4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        93: {
            'Name': 'Dispercher 3\nMonitor 1',
            'Inputs': [28,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[94],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        94: {
            'Name': 'Dispercher 3\nMonitor 2',
            'Inputs': [29,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        95: {
            'Name': 'Dispercher 3\nMonitor 3',
            'Inputs': [21,22,23,25,34,35,2,42,43,33,37,3,4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        73: {
            'Name': 'Dispercher 4\nMonitor 1',
            'Inputs': [30,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[74],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        74: {
            'Name': 'Dispercher 4\nMonitor 2',
            'Inputs': [31,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        75: {
            'Name': 'Dispercher 4\nMonitor 3',
            'Inputs': [21,22,23,25,34,35,2,42,43,33,37,3,4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        76: {
            'Name': 'Dispercher 5\nMonitor 1',
            'Inputs': [32,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[77],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        77: {
            'Name': 'Dispercher 5\nMonitor 2',
            'Inputs': [14,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        78: {
            'Name': 'Dispercher 5\n Monitor 3',
            'Inputs': [21,22,23,25,34,35,2,42,43,33,37,3,4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        79: {
            'Name': 'Dispercher 6\nMonitor 1',
            'Inputs': [15,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[80],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        80: {
            'Name': 'Dispercher 6\nMonitor 2',
            'Inputs': [16,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        81: {
            'Name': 'Dispercher 6\nMonitor 3',
            'Inputs': [21,22,23,25,34,35,2,42,43,33,37,3,4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        82: {
            'Name': 'Dispercher 7\nMonitor 1',
            'Inputs': [17,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[84],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        84: {
            'Name': 'Dispercher 7\nMonitor 2',
            'Inputs': [18,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        85: {
            'Name': 'Dispercher 7\nMonitor 3',
            'Inputs': [21,22,23,25,34,35,2,42,43,33,37,3,4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        86: {
            'Name': 'Dispercher 8\nMonitor 1',
            'Inputs': [19,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[87],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        87: {
            'Name': 'Dispercher 8\nMonitor 2',
            'Inputs': [20,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        88: {
            'Name': 'Dispercher 8\nMonitor 3',
            'Inputs': [21,22,23,25,34,35,2,42,43,33,37,3,4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },

        ## ------
        55: {
            'Name': '',
            'Inputs': [45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 2],
            'ConnectionType':[],
            'textFb':True,
        },
        56: {
            'Name': '',
            'Inputs': [45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 2],
            'ConnectionType':[],
            'textFb':True,
        },
        57: {
            'Name': '',
            'Inputs': [45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 2],
            'ConnectionType':[],
            'textFb':True,
        },
        58: {
            'Name': '',
            'Inputs': [45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 2],
            'ConnectionType':[],
            'textFb':True,
        },
        59: {
            'Name': '',
            'Inputs': [45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 2],
            'ConnectionType':[],
            'textFb':True,
        },
        60: {
            'Name': '',
            'Inputs': [45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 2],
            'ConnectionType':[],
            'textFb':True,
        },


        # ---- 29 Jupiter
        62: {
            'Name': '',
            'Inputs': [13, 24, 26, 27, 28, 29, 30, 31, 32, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 42, 43, 33, 37, 3, 4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_4',
            'textFb':True,
        },
        64: {
            'Name': '',
            'Inputs': [13, 24, 26, 27, 28, 29, 30, 31, 32, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 42, 43, 33, 37, 3, 4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_4',
            'textFb':True,
        },
        65: {
            'Name': '',
            'Inputs': [13, 24, 26, 27, 28, 29, 30, 31, 32, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 42, 43, 33, 37, 3, 4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_4',
            'textFb':True,
        },
        66: {
            'Name': '',
            'Inputs': [13, 24, 26, 27, 28, 29, 30, 31, 32, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 42, 43, 33, 37, 3, 4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_4',
            'textFb':True,
        },
        67: {
            'Name': '',
            'Inputs': [13, 24, 26, 27, 28, 29, 30, 31, 32, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 42, 43, 33, 37, 3, 4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_4',
            'textFb':True,
        },
        68: {
            'Name': '',
            'Inputs': [13, 24, 26, 27, 28, 29, 30, 31, 32, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 42, 43, 33, 37, 3, 4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_4',
            'textFb':True,
        },
        69: {
            'Name': '',
            'Inputs': [13, 24, 26, 27, 28, 29, 30, 31, 32, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 42, 43, 33, 37, 3, 4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_4',
            'textFb':True,
        },
        70: {
            'Name': '',
            'Inputs': [13, 24, 26, 27, 28, 29, 30, 31, 32, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 42, 43, 33, 37, 3, 4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_4',
            'textFb':True,
        },
        71: {
            'Name': '',
            'Inputs': [13, 24, 26, 27, 28, 29, 30, 31, 32, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 42, 43, 33, 37, 3, 4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_4',
            'textFb':True,
        },
        63: {
            'Name': '',
            'Inputs': [13, 24, 26, 27, 28, 29, 30, 31, 32, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 45, 47, 48, 49, 50, 51, 52, 53, 54, 46, 42, 43, 33, 37, 3, 4],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_4',
            'textFb':True,
        },

        ## ------
        122: {
            'Name': 'VCS Camera',
            'Inputs': [3, 4],
            'InputPP': 'Pp.5_GroupsInputs_1',
            'ConnectionType':[],
        },
        123: {
            # VCS Content 29
            'Name': '',
            'Inputs': [24, 27, 29, 31, 14, 16, 18, 20, 22, 25, 50, 46, 34, 35],
            'InputPP': 'Pp.3_GroupsInputsForVCS',
            'ConnectionType':[],
            'textFb':True,
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
        },


        # --- Dispercherа 31 ---
        98: {
            'Name': 'Dispercher 1\nMonitor',
            'Inputs': [13,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[109],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        109: {
            'Name': 'Dispercher 1\nMonitor 2',
            'Inputs': [24,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        115: {
            'Name': 'Dispercher 1\nMonitor 3',
            'Inputs': [21, 22, 23, 25, 34, 35, 42, 43, 38, 39, 10, 11, 12],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        116: {
            'Name': 'Dispercher 2\nMonitor 1',
            'Inputs': [26,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[117],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        117: {
            'Name': 'Dispercher 2\nMonitor 2',
            'Inputs': [27,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        118: {
            'Name': 'Dispercher 2\nMonitor 3',
            'Inputs': [21, 22, 23, 25, 34, 35, 42, 43, 38, 39, 10, 11, 12],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        119: {
            'Name': 'Dispercher 3\nMonitor 1',
            'Inputs': [28,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[120],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        120: {
            'Name': 'Dispercher 3\nMonitor 2',
            'Inputs': [29,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        121: {
            'Name': 'Dispercher 3\nMonitor 3',
            'Inputs': [21, 22, 23, 25, 34, 35, 42, 43, 38, 39, 10, 11, 12],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        99: {
            'Name': 'Dispercher 4\nMonitor 1',
            'Inputs': [30,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[100],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        100: {
            'Name': 'Dispercher 4\nMonitor 2',
            'Inputs': [31,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        101: {
            'Name': 'Dispercher 4\nMonitor 3',
            'Inputs': [21, 22, 23, 25, 34, 35, 42, 43, 38, 39, 10, 11, 12],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        102: {
            'Name': 'Dispercher 5\nMonitor 1',
            'Inputs': [32,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[103],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        103: {
            'Name': 'Dispercher 5\nMonitor 2',
            'Inputs': [14,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        104: {
            'Name': 'Dispercher 5\n Monitor 3',
            'Inputs': [21, 22, 23, 25, 34, 35, 42, 43, 38, 39, 10, 11, 12],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        105: {
            'Name': 'Dispercher 6\nMonitor 1',
            'Inputs': [15,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[106],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        106: {
            'Name': 'Dispercher 6\nMonitor 2',
            'Inputs': [16,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        107: {
            'Name': 'Dispercher 6\nMonitor 3',
            'Inputs': [21, 22, 23, 25, 34, 35, 42, 43, 38, 39, 10, 11, 12],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        108: {
            'Name': 'Dispercher 7\nMonitor 1',
            'Inputs': [17,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[110],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        110: {
            'Name': 'Dispercher 7\nMonitor 2',
            'Inputs': [18,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        111: {
            'Name': 'Dispercher 7\nMonitor 3',
            'Inputs': [21, 22, 23, 25, 34, 35, 42, 43, 38, 39, 10, 11, 12],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },
        112: {
            'Name': 'Dispercher 8\nMonitor 1',
            'Inputs': [19,21,23],
            'ConnectionType':['usb'],
            'AdditionalOut':[113],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        113: {
            'Name': 'Dispercher 8\nMonitor 2',
            'Inputs': [20,22,25],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_1',
        },
        114: {
            'Name': 'Dispercher 8\nMonitor 3',
            'Inputs': [21, 22, 23, 25, 34, 35, 42, 43, 38, 39, 10, 11, 12],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputs_2',
        },

        # --- main screens 31 - Jupiter
        131: {
            'Name': '',
            'Inputs': [
                13, 24, 26, 27, 28, 29, 30, 31, 32, 14,
                15, 16, 17, 18, 19, 20, 21, 22, 23, 25,
                45, 47, 48, 49, 50, 51, 52, 53, 54, 46,
                43, 38, 39, 10, 11, 12, 44, 8, 9
            ],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputsForRecorder_31_31',
            'textFb':True,
        },
        132	: {
            'Name': '',
            'Inputs': [
                13, 24, 26, 27, 28, 29, 30, 31, 32, 14,
                15, 16, 17, 18, 19, 20, 21, 22, 23, 25,
                45, 47, 48, 49, 50, 51, 52, 53, 54, 46,
                43, 38, 39, 10, 11, 12, 44, 8, 9
            ],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputsForRecorder_31_31',
            'textFb':True,
        },
        133	: {
            'Name': '',
            'Inputs': [
                13, 24, 26, 27, 28, 29, 30, 31, 32, 14,
                15, 16, 17, 18, 19, 20, 21, 22, 23, 25,
                45, 47, 48, 49, 50, 51, 52, 53, 54, 46,
                43, 38, 39, 10, 11, 12, 44, 8, 9
            ],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputsForRecorder_31_31',
            'textFb':True,
        },
        134	: {
            'Name': '',
            'Inputs': [
                13, 24, 26, 27, 28, 29, 30, 31, 32, 14,
                15, 16, 17, 18, 19, 20, 21, 22, 23, 25,
                45, 47, 48, 49, 50, 51, 52, 53, 54, 46,
                43, 38, 39, 10, 11, 12, 44, 8, 9
            ],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputsForRecorder_31_31',
            'textFb':True,
        },
        135	: {
            'Name': '',
            'Inputs': [
                13, 24, 26, 27, 28, 29, 30, 31, 32, 14,
                15, 16, 17, 18, 19, 20, 21, 22, 23, 25,
                45, 47, 48, 49, 50, 51, 52, 53, 54, 46,
                43, 38, 39, 10, 11, 12, 44, 8, 9
            ],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputsForRecorder_31_31',
            'textFb':True,
        },
        136	: {
            'Name': '',
            'Inputs': [
                13, 24, 26, 27, 28, 29, 30, 31, 32, 14,
                15, 16, 17, 18, 19, 20, 21, 22, 23, 25,
                45, 47, 48, 49, 50, 51, 52, 53, 54, 46,
                43, 38, 39, 10, 11, 12, 44, 8, 9
            ],
            'ConnectionType':[],
            'InputPP': 'Pp.5_GroupsInputsForRecorder_31_31',
            'textFb':True,
        },

        # --- VCS Camera + Content 31
        124	: {
            'Name': '',
            'Inputs': [10, 11],
            'InputPP': 'PPp.5_GroupsInputs_1',
            'ConnectionType':[],
            'textFb':True,
        },
        125 : {
            'Name': '',
            'Inputs': [24, 27, 29, 31, 14, 16, 18, 20, 22, 50, 46, 34, 35, 12],
            'InputPP': 'Pp.3_GroupsInputsForVCS_31_31',
            'ConnectionType':[],
            'textFb':True,
            'audio':{
                'out': [45],
                'posibleIntuts':[
                    41, 42, 43, 44, 45, 46, 47, 50,
                    31, 32, 33, 34,
                    35, 36, 37, 38,
                    61, 62
                ]
            }
        },


        97	: {
            'Name': '',
            'Inputs': [50, 46, 34, 35, 36, 42, 43, 38, 39, 10, 11, 12, 40, 41, 5, 6, 7, 44, 8, 9],
            'InputPP': 'Pp.5_GroupsInputsForJupiter_31_30',
            'ConnectionType':[],
            'textFb':True,
        },
        129	: {
            'Name': '',
            'Inputs': [50, 46, 34, 35, 36, 42, 43, 38, 39, 10, 11, 12, 40, 41, 5, 6, 7, 44, 8, 9],
            'InputPP': 'Pp.5_GroupsInputsForJupiter_31_30',
            'ConnectionType':[],
            'textFb':True,
        },
        130	: {
            'Name': '',
            'Inputs': [50, 46, 34, 35, 36, 42, 43, 38, 39, 10, 11, 12, 40, 41, 5, 6, 7, 44, 8, 9],
            'InputPP': 'Pp.5_GroupsInputsForJupiter_31_30',
            'ConnectionType':[],
            'textFb':True,
        },
        126	: {
            'Name': '',
            'Inputs': [10, 11, 5, 6, 7],
            'InputPP': 'Pp.3_GroupsInputsForVCS_31_30',
            'ConnectionType':[],
            'textFb':True,
        },
        127	: {
            'Name': '',
            'Inputs': [12, 44, 8, 9],
            'InputPP': 'Pp.3_GroupsInputsForVCS_31_30',
            'ConnectionType':[],
            'textFb':True,
            'audio':{
                'out': [47],
            }
        },

        # --- Console 1 и 2
        61	: {
            'Name': '',
            'Inputs': [],
            'ConnectionType':[],
        },
        96	: {
            'Name': '',
            'Inputs': [],
            'ConnectionType':[],
        },


        128: {
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
            'audio':{
                'out': [27],
                'outStereo': [28],
                'posibleIntuts':[
                    41, 42, 43, 44, 45, 46, 47, 50,
                    54, 55,
                    51,
                    31, 33,
                    35, 37,
                    61
                ],
                'posibleIntutsStereo':[
                    41, 42, 43, 44, 45, 46, 47, 50,
                    54, 55,
                    51,
                    32, 34,
                    36, 38,
                    62
                ]
            }
        },

    },
    'INPUTS': {
        0: {
            'Name': 'ON.',
            'ConnectionType':['usb'],
        },
        13: {
            'Name': 'ARM 1 Main',
            'ConnectionType':['usb'],
            'AdditionalInput':[24],
        },
        24: {
            'Name': 'ARM 1 Second',
            'audio':{
                'input': [41],
            }
        },
        26: {
            'Name': 'ARM 2 Main',
            'ConnectionType':['usb'],
            'AdditionalInput':[27],
        },
        27: {
            'Name': 'ARM 2 Second',
            'audio':{
                'input': [42],
            }
        },
        28: {
            'Name': 'ARM 3 Main',
            'ConnectionType':['usb'],
            'AdditionalInput':[24],
        },
        29: {
            'Name': 'ARM 3 Second',
            'audio':{
                'input': [43],
            }
        },
        30: {
            'Name': 'ARM 4 Main',
            'ConnectionType':['usb'],
            'AdditionalInput':[31],
        },
        31: {
            'Name': 'ARM 4 Second',
            'audio':{
                'input': [43],
            }
        },
        32: {
            'Name': 'ARM 5 Main',
            'ConnectionType':['usb'],
            'AdditionalInput':[14],
        },
        14: {
            'Name': 'ARM 5 Second',
            'audio':{
                'input': [45],
            }
        },
        15: {
            'Name': 'ARM 6 Main',
            'ConnectionType':['usb'],
            'AdditionalInput':[16],
        },
        16: {
            'Name': 'ARM 6 Second',
            'audio':{
                'input': [46],
            }
        },
        17: {
            'Name': 'ARM 7 Main',
            'ConnectionType':['usb'],
            'AdditionalInput':[17],
        },
        18: {
            'Name': 'ARM 7 Second',
            'audio':{
                'input': [47],
            }
        },
        19: {
            'Name': 'ARM 8 Main',
            'ConnectionType':['usb'],
            'AdditionalInput':[20],
        },
        20: {
            'Name': 'ARM 8 Second',
            'audio':{
                'input': [48],
            }
        },
        21: {
            'Name': 'ARM 9 Main',
            'ConnectionType':['usb'],
            'AdditionalInput':[22],
        },
        22: {
            'Name': 'ARM 9 Second',
            'audio':{
                'input': [49],
            }
        },
        23: {
            'Name': 'ARM 10 Main',
            'ConnectionType':['usb'],
            'AdditionalInput':[25],
        },
        25: {
            'Name': 'ARM 10 Second',
            'audio':{
                'input': [50],
            }
        },


        45: {
            'Name': 'Statistic data server 1',
        },
        47: {
            'Name': 'Statistic data server 2',
        },
        48: {
            'Name': 'Statistic data server 3',
        },
        49: {
            'Name': 'Statistic data server 4',
        },
        50: {
            'Name': 'Statistic data server 5',
            'audio':{
                'input': [31,33],
                'inputStereo': [32,34],
            }
        },
        51: {
            'Name': 'Dinamic data server 1',
        },
        52: {
            'Name': 'Dinamic data server 2',
        },
        53: {
            'Name': 'Dinamic data server 3',
        },
        54: {
            'Name': 'Dinamic data server 4',
        },
        46: {
            'Name': 'Dinamic data server 5',
            'audio':{
                'input': [35,37],
                'inputStereo': [36,38],
            }
        },
        34: {
            'Name': 'PC 11',
            'audio':{
                'input': [54],
            }
        },
        35: {
            'Name': 'PC 12',
            'audio':{
                'input': [54],
            }
        },
        36: {
            'Name': 'PC №3 (7.3)',
        },
        2: {
            'Name': 'PC Content',
        },
        42: {
            'Name': 'Mediaplayer',
            'audio':{
                'input': [51],
            }
        },
        43: {
            'Name': 'Recoder',
        },
        33: {
            'Name': 'VCS Camera',
        },
        37: {
            'Name': 'VCS Content',
        },
        3: {
            'Name': 'Camera 1',
        },
        4: {
            'Name': 'Camera 2',
        },
        38: {
            'Name': 'EK_Codec VCS_Out1',
        },
        39: {
            'Name': 'EK_Codec VCS_Out2',
        },
        10: {
            'Name': 'EK_VideoCam слева',
        },
        11: {
            'Name': 'EK_VideoCam справа',
        },
        12: {
            'Name': 'EK_Document-Camera',
        },
        40: {
            'Name': 'KS ND_Codec VCS_Out1',
        },
        41: {
            'Name': 'KS ND_Codec VCS_Out2',
        },
        5: {
            'Name': 'KS ND_Camera centre',
        },
        6: {
            'Name': 'KS ND_Camera left',
        },
        7: {
            'Name': 'KS ND_Camera right',
        },
        44: {
            'Name': 'KS ND_wirleless translation',
            'audio':{
                'input': [61],
                'inputStereo': [62],
            }
        },
        8: {
            'Name': 'KS ND_ARCH interfase №1',
            'audio':{
                'input': [61],
                'inputStereo': [62],
            }
        },
        9: {
            'Name': 'KS ND_ARCH interfase №2',
            'audio':{
                'input': [61],
                'inputStereo': [62],
            }
        },
    }
}

# ------ Cloac audio ------
MicData = {
    'Devices':{
        0: {
            'IP': '10.75.41.98',
            'Port': 50001,
            'dvName': 0,
            'DV': None,
            'micPositions': [1,2,3,0],
        },
        1: {
            'IP': '10.75.41.102',
            'Port': 50002,
            'dvName': 1,
            'DV': None,
            'micPositions': [4,5,0,0],
        },
        2: {
            'IP': '10.75.41.106',
            'Port': 50003,
            'dvName': 2,
            'DV': None,
            'micPositions': [6,7,8,0],
        },
    },
    'micNumbers': 8,
    'fb': ''
}

DocCamData = {
    'IP': '10.75.41.158',
    'Login': 'Admin',
    'Password': 'Admin',

    'buttonShift': 3300,

    'powerFb': 0,
    'freezFb': 0,
    'zoomFb': 0,
}

ProjData = {}

LedsData = {}

DtpData = {}

WatchoutData = {}

DDServData = {}

JupiterData = {}

VcsData = {}

PicUpdaterData = {}

Smp352Data = {}

ScreenData = {}

SensorsData = {}

ArturHolmData = {}

# ------ ShureCeiling ------
ShureData = {
    'ip': '10.75.41.13',
    'port': 2202,
}

# ---- file operations ----
def Read(FileName):
    if File.Exists(FileName):
        with File(FileName, mode = 'r', newline = '',  encoding='utf8') as logFile:
            logFile = logFile.read()
        return logFile
    else:
        return None

def Write(FileName, data):
    # write to file
    string = str.encode(json.dumps(data))
    with File(FileName, 'wb', newline = None) as logFile:
        logFile.write(string)