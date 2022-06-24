#!/usr/bin/env python3
# -*- encoding: UTF-8 -*-
#

import os, sys
import random as rand
import shutil, zipfile
import xml.etree.ElementTree as ET


__author__ = "Zich Robert (cichy)"
__version__ = "1.7.0"


def printHelp():
    if guiIsShown:
        return
    
    print("""
Execution: python script.py [OPTIONS] mapFile.h5m [anotherMapFile.h5m ...]

This script can change creatures, artifacts and other on homm5/mmh55 maps.
Script expects path to "data" folder of Tribes of the East is "../data".

Artifacts:
    - one to another (in same price group)
    - one to random (by ones type)
    - random to one (in type)

Creatures:
    - specific <-> random (by power)
    - single <-> group (by power)
    
    - random, really dynamic tier range and regardless context
    - not for fair games (against computer shouldn't be problem)
    - should be roughly same power, but sometimes, there is big difference

Options:
    --artChange=true                To change artifacts(art).
    --creaChange=true               To change creatures(crea).
    
    --artChangeOnlyRandom=false     To change only random art.
    --artRandom=false               To randomize art.
    --creaChangeOnlyRandom=false    To change only random crea.
    --creaRandom=false              To randomize crea.
    --creaPowerRatio=1.0            Will modify crea power.
    --creaGroupRatio=0.55           Will modify chance to crea be group (1.0 == highest, but not 100%).
    --creaMoodChange=true           To change creas mood
    --creaMoodRatio=0,3,2,1         Will modify crea mood (probably does not affect groups).
                                        - mood order: FRIENDLY,AGGRESSIVE,HOSTILE,WILD
                                        - value "1,1,0,0" would give us 50% FRIENDLY and 50% AGGRESSIVE
    --creaNeutralRatio=-2           To change chance of neutrals to be placed on map.
                                        - creaNeutralRatio == 0: chanceToPlaceOnMap = 1 / (townsCount + 1)
                                        - creaNeutralRatio < 0: chanceToPlaceOnMap = 1 / (townsCount * (creaNeutralRatio * -1 + 1) + 1)
                                        - creaNeutralRatio > 0: chanceToPlaceOnMap = (2 ** creaNeutralRatio) / (townsCount + 2 ** creaNeutralRatio)
    --creaNCF=false                 To load and work with NCF creatures.
                                        - will look for files in data folder, which names starts with "NCF"
                                        - if NFC is used, then --creaNeutralRatio=0, or higher should be set (probably)
    
    --enableScripts=true            To enable scripts.
                                        - will enable scripts only if not already enabled
                                        - will not disable scripts
                                        - needed by mmh55 (to work in multiplayer)
    --waterChange=true              To change some water objects
    --dwellChange=true              To change high tier (random) dwellings(dwell)
    --dwellRatio=4,3,1,0            To choose possible tiers(and theirs weight) of dwell
                                        - tier order: 4,5,6,7
                                        - value "1,1,0,0" would give us 50% T4 and 50% T5
    --townBuild=""                  To build, or limit some town buildings
                                        - value example "TB_MAGIC_GUILD,1,3,ALL"
                                        - value description "BUILDING_TYPE,INITIAL_UPGRADE,MAX_UPGRADE,PLAYER_NUMBER":
                                            - BUILDING_TYPE: building type (TB_TAWN_HALL, TB_FORT, TB_MARKETPLACE, TB_TAVERN, TB_BLACKSMITH, 
                                                             TB_DWELLING_1, TB_MAGIC_GUILD, TB_SHIPYARD, TB_GRAIL, TB_WONDER, TB_SPECIAL_0)
                                            - INITIAL_UPGRADE: number of initial upgrade (0-5)
                                            - MAX_UPGRADE: number of max. enabled upgrade (0-5)
                                            - PLAYER_NUMBER: build/limit only for this player (ALL, PLAYER, NONE, 1 - 8) (optional)
                                            - #: can be used to separate more buildings
    --gamePowerLimit=false          To limit some game possibilities
                                        - town: no Capiton and T5 to T7 dwellings
    
    --nogui                         To run console version (in gui version)
    --pathToGameFolder=../          Path to game folder.
    --loadMapFromBck=true           To load map from backup file (backup file is generated with first change).
                                        - better to leave true
    --createMapBck=true             To create backup of original map (only if not exist)
    
    --logArtInit=false              To log art init info.
    --logArtChange=false            To log art change info.
    --logCreaInit=false             To log crea init info.
    --logCreaChange=false           To log crea change info.
    --logWaterChange=false          To log water objects change info.
    --logMapInfo=false              To log some map(old/new) info.
    --logWarnings=false             To log warnings/errors.

Author: {}
Version: {}
    """.format(__author__, __version__))

"""
NOTES:
    --creaPowerRatio=1.0 is not 100% group, because if all units in group are of one creature, then it will lead to group of one unit
"""

# reset args func
def resetArgs():
    g = globals()
    g["mapFiles"] = []
    g["pathToGameFolder"] = "../"
    g["loadMapFromBck"] = "true"
    g["createMapBck"] = "true"

    g["artChange"] = "true"
    g["creaChange"] = "true"

    g["artChangeOnlyRandom"] = "false"
    g["artRandom"] = "false"
    g["creaChangeOnlyRandom"] = "false"
    g["creaRandom"] = "false"
    g["creaMoodChange"] = "true"
    g["creaMoodRatio"] = "0,3,2,1"
    g["creaPowerRatio"] = "1.0"
    g["creaGroupRatio"] = "0.55"
    g["creaNeutralRatio"] = "-2"
    g["creaNCF"] = "false"
    
    g["enableScripts"] = "true"
    g["waterChange"] = "true"
    g["dwellChange"] = "true"
    g["dwellRatio"] = "4,3,1,0"
    g["townBuild"] = ""
    g["gamePowerLimit"] = "false"
    
    g["logArtInit"] = "false"
    g["logArtChange"] = "false"
    g["logCreaInit"] = "false"
    g["logCreaChange"] = "false"
    g["logWaterChange"] = "false"
    g["logMapInfo"] = "false"
    g["logWarnings"] = "false"
    
    # no args
    g["guiIsShown"] = False
    g["creaMoodList"] = None
    g["dwellList"] = None
    g["dataFolder"] = None
    g["mainArchFile"] = None


# custom exception
class MyException(Exception):
    pass

# log class
class Log:
    @staticmethod
    def error(pMsg):
        raise MyException(pMsg)
    
    @staticmethod
    def warning(pMsg):
        if logWarnings:
            print(pMsg)


# parse args func
def parseArgs(pArgs):
    resetArgs()
    g = globals()
    
    # parse args
    ignoreArgs = ["--nogui"]
    validArgs = [
        "pathToGameFolder", "loadMapFromBck", "createMapBck", "artChange", 
        "creaChange", "artChangeOnlyRandom", "artRandom", "creaChangeOnlyRandom", 
        "creaMoodChange", "creaMoodRatio", "creaPowerRatio", "creaGroupRatio", 
        "creaNeutralRatio", "creaRandom", "creaNCF", "enableScripts", 
        "waterChange", "dwellChange", "dwellRatio", "townBuild", "gamePowerLimit", "logArtInit", "logArtChange", 
        "logCreaInit", "logCreaChange", "logWaterChange", "logMapInfo", "logWarnings", 
        "guiIsShown"
    ]
    for arg in pArgs:
        if arg not in ignoreArgs:
            if arg == "-h" or arg == "--help":
                printHelp()
                sys.exit()
            knownArg = False
            valueSepPos = arg.find("=")
            if len(arg) > 1 and valueSepPos != -1:
                argName = arg[2:valueSepPos]
                argValue = arg[valueSepPos + 1:]
                if argName in validArgs:
                    g[argName] = argValue
                    knownArg = True
            if not knownArg:
                if arg.endswith(".h5m"):
                    g["mapFiles"].append(arg)
                else:
                    printHelp()
                    Log.error("Unknown argument: \"{}\"".format(arg))

    # convert args
    trueStrList = ["true"]

    g["loadMapFromBck"] = g["loadMapFromBck"] in trueStrList
    g["createMapBck"] = g["createMapBck"] in trueStrList

    g["artChange"] = g["artChange"] in trueStrList
    g["artChangeOnlyRandom"] = g["artChangeOnlyRandom"] in trueStrList
    g["creaChange"] = g["creaChange"] in trueStrList
    g["creaChangeOnlyRandom"] = g["creaChangeOnlyRandom"] in trueStrList
    g["artRandom"] = g["artRandom"] in trueStrList
    g["creaRandom"] = g["creaRandom"] in trueStrList
    g["creaMoodChange"] = g["creaMoodChange"] in trueStrList
    g["creaNCF"] = g["creaNCF"] in trueStrList

    g["enableScripts"] = g["enableScripts"] in trueStrList
    g["waterChange"] = g["waterChange"] in trueStrList
    g["dwellChange"] = g["dwellChange"] in trueStrList
    g["gamePowerLimit"] = g["gamePowerLimit"] in trueStrList
    
    g["logArtInit"] = g["logArtInit"] in trueStrList
    g["logArtChange"] = g["logArtChange"] in trueStrList
    g["logCreaInit"] = g["logCreaInit"] in trueStrList
    g["logCreaChange"] = g["logCreaChange"] in trueStrList
    g["logWaterChange"] = g["logWaterChange"] in trueStrList
    g["logMapInfo"] = g["logMapInfo"] in trueStrList
    g["logWarnings"] = g["logWarnings"] in trueStrList
    g["guiIsShown"] = g["guiIsShown"] in trueStrList
    try:
        g["creaPowerRatio"] = float(g["creaPowerRatio"])
        g["creaGroupRatio"] = float(g["creaGroupRatio"])
        g["creaNeutralRatio"] = int(g["creaNeutralRatio"])
        
        if g["creaNeutralRatio"] > 8:
            g["creaNeutralRatio"] = 8
        elif g["creaNeutralRatio"] < -8:
            g["creaNeutralRatio"] = -8
    except ValueError:
        printHelp()
        Log.error("Value error!")
    
    if g["creaChange"]:
        if g["creaPowerRatio"] <= 0.0:
            g["creaPowerRatio"] = 1.0

        # fill creaMoodList
        g["creaMoodList"] = []
        if creaMoodChange:
            basicMoodList = ["MONSTER_MOOD_FRIENDLY", "MONSTER_MOOD_AGGRESSIVE", "MONSTER_MOOD_HOSTILE", "MONSTER_MOOD_WILD"]
            basicCourageList = ["MONSTER_COURAGE_ALWAYS_JOIN", "MONSTER_COURAGE_ALWAYS_FIGHT", "MONSTER_COURAGE_CAN_FLEE_JOIN"]

            moodRatioParts = creaMoodRatio.split(",")
            if len(moodRatioParts) != 4:
                printHelp()
                Log.error("Value error!")
            for moodIndex, moodRationPart in enumerate(moodRatioParts):
                try:
                    moodRationPart = int(moodRationPart)
                    if moodRationPart > 0:
                        for i in range(moodRationPart):
                            g["creaMoodList"].append(basicMoodList[moodIndex])
                except ValueError:
                    pass
            if len(g["creaMoodList"]) == 0:
                printHelp()
                Log.error("Value error!")
    
    # fill dwellList
    g["dwellList"] = []
    if dwellChange:
        basicDwellList = [
            "/MapObjects/Random/RandomDwelling4.xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Random/RandomDwelling5.xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Random/RandomDwelling6.xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Random/RandomDwelling7.xdb#xpointer(/AdvMapDwellingShared)"
        ]
        
        dwellRatioParts = dwellRatio.split(",")
        if len(dwellRatioParts) != 4:
            printHelp()
            Log.error("Value error!")
        for dwellIndex, dwellRatioPart in enumerate(dwellRatioParts):
            try:
                dwellRatioPart = int(dwellRatioPart)
                if dwellRatioPart > 0:
                    for i in range(dwellRatioPart):
                        g["dwellList"].append(basicDwellList[dwellIndex])
            except ValueError:
                pass
        if len(g["dwellList"]) == 0:
            printHelp()
            Log.error("Value error!")
    
    
    # check map file
    if len(g["mapFiles"]) == 0:
        printHelp()
        Log.error("Map file does not exist: \"{}\"".format(None))
    else:
        for mapFile in g["mapFiles"]:
            if not os.path.exists(mapFile):
                printHelp()
                Log.error("Map file does not exist: \"{}\"".format(mapFile))
    
    # find data folder
    g["dataFolder"] = os.path.join(g["pathToGameFolder"], "data")
    if not os.path.exists(g["dataFolder"]):
        Log.error("Data folder not found: \"{}\"".format(g["dataFolder"]))
    
    # find main data file
    g["mainArchFile"] = os.path.join(g["dataFolder"], "data.pak") 
    if not os.path.exists(g["mainArchFile"]):
        Log.error("Archive does not exist: \"{}\"".format(g["mainArchFile"]))


# main prog

class Artifact:
    sAll = []
    sMapId = {}
    sMapShared = {}
    sGroups = {}
    sTypeGroups = {}
    
    def __init__(self):
        self.mId = ""
        self.mType = ""
        self.mSlot = ""
        self.mPrice = 0
        self.mCanBuy = False
        self.mShared = ""
        self.mGroup = None
    
    @staticmethod
    def fromXml(pXml):
        obj = None
        if pXml is not None:
            obj = Artifact()
            obj.mId = pXml.findtext("ID", "")
            desc = pXml.find("obj")
            if desc is not None:
                obj.mType = desc.findtext("Type", "")
                obj.mSlot = desc.findtext("Slot", "")
                obj.mPrice = int(desc.findtext("CostOfGold", "0"))
                obj.mCanBuy = desc.findtext("CanBeGeneratedToSell", "") == "true"
                obj.mShared = desc.find("ArtifactShared").get("href", "")
                
        return obj
    
    @classmethod
    def init(pClass):
        archFile = os.path.join(dataFolder, "MMH55-Index.pak") 
        if not os.path.exists(archFile):
            archFile = mainArchFile
        
        # load from file
        with zipfile.ZipFile(archFile, "r") as arch:
            with arch.open("GameMechanics/RefTables/Artifacts.xdb", "r") as dataFile:
                tree = ET.parse(dataFile)
                root = tree.getroot()
                items = root.find("objects")
        
                # fill list
                pClass.sAll = []
                pClass.sMapId = {}
                pClass.sMapShared = {}
                pClass.sGroups = {}
                pClass.sTypeGroups = {}
                pClass.sTypeGroups["ARTF_CLASS_ANY"] = []
                for item in items:
                    art = Artifact.fromXml(item)
                    if art is not None:
                        pClass.sAll.append(art)
                        pClass.sMapId[art.mId] = art
                        pClass.sMapShared[art.mShared] = art
                        
                        if art.mCanBuy:
                            if art.mPrice not in pClass.sGroups:
                                pClass.sGroups[art.mPrice] = []
                            pClass.sGroups[art.mPrice].append(art)
                            
                            if art.mType not in pClass.sTypeGroups:
                                pClass.sTypeGroups[art.mType] = []
                            pClass.sTypeGroups[art.mType].append(art)
                            pClass.sTypeGroups["ARTF_CLASS_ANY"].append(art)
        
        # add rand artifacts
        randArtList = [
            {"id": "ARTF_CLASS_ANY", "shared": "/MapObjects/Random/Random-Any.(AdvMapArtifactShared).xdb#xpointer(/AdvMapArtifactShared)"},
            {"id": "ARTF_CLASS_MINOR", "shared": "/MapObjects/Random/Random-Minor.(AdvMapArtifactShared).xdb#xpointer(/AdvMapArtifactShared)"},
            {"id": "ARTF_CLASS_MAJOR", "shared": "/MapObjects/Random/Random-Major.(AdvMapArtifactShared).xdb#xpointer(/AdvMapArtifactShared)"},
            {"id": "ARTF_CLASS_RELIC", "shared": "/MapObjects/Random/Random-Relic.(AdvMapArtifactShared).xdb#xpointer(/AdvMapArtifactShared)"}
        ]
        for i, randArt in enumerate(randArtList):
            art = Artifact()
            art.mId = randArt["id"]
            art.mType = randArt["id"]
            art.mShared = randArt["shared"]
            
            pClass.sMapId[art.mId] = art
            pClass.sMapShared[art.mShared] = art
        
        print("artifacts loaded")

        if logArtInit:
            # print groups
            for price in pClass.sGroups:
                group = pClass.sGroups[price]
                print("price - {} ({})".format(price, len(group)))
                for art in group:
                    print(art.mId)
                print("")

            for art in pClass.sAll:
                if not art.mCanBuy:
                    print("cannot buy: {}".format(art.mId))
    
    def isRand(self):
        return self.mId in self.sTypeGroups
    
    @classmethod
    def getAlt(pClass, pArt):
        altArt = pArt
        
        if artRandom:
            altArt = pClass.sMapId[pArt.mType]
        else:
            if pArt.mPrice > 0:
                if pArt.mPrice in pClass.sGroups:
                    altArt = rand.choice(pClass.sGroups[pArt.mPrice])
            else:
                if pArt.mType in pClass.sTypeGroups:
                    altArt = rand.choice(pClass.sTypeGroups[pArt.mType])
        
        return altArt
    
    @classmethod
    def getByShared(pClass, pArtShared):
        if pArtShared in pClass.sMapShared:
            return pClass.sMapShared[pArtShared]
        return None


class Creature:
    sAll = []
    sMap = {}
    sMapId = {}
    sMapShared = {}
    sMapTierPower = {}
    sTownList = []
    sTownWeightList = []
    sRandList = []
    sHighestCommonTier = 1
    
    def __init__(self):
        self.mId = ""
        self.mTown = ""
        self.mTier = 1
        self.mIsUpgrade = False
        self.mPower = 0
        self.mWeekGrow = 0
        self.mCanGen = False
        self.mShared = ""
    
    @classmethod
    def fromXml(pClass, pXml):
        obj = None
        if pXml is not None:
            obj = Creature()
            obj.mTown = pXml.findtext("CreatureTown", "")
            obj.mTier = int(pXml.findtext("CreatureTier", "1"))
            obj.mIsUpgrade = pXml.findtext("Upgrade", "") == "true"
            obj.mPower = int(pXml.findtext("Power", "0"))
            obj.mWeekGrow = int(pXml.findtext("WeeklyGrowth", "0"))
            obj.mCanGen = pXml.findtext("SubjectOfRandomGeneration", "") == "true"
            obj.mShared = pXml.find("MonsterShared").get("href", "")
        
        return obj
    
    def setIdFromXml(self, pXml):
        self.mId = ""
        if pXml is not None:
            self.mId = pXml.findtext("Creature", "")
    
    @classmethod
    def init(pClass):
        archFile = os.path.join(dataFolder, "MMH55-Index.pak") 
        if not os.path.exists(archFile):
            archFile = mainArchFile
        
        # clear list
        pClass.sAll = []
        pClass.sMap = {}
        pClass.sMapId = {}
        pClass.sMapShared = {}
        pClass.sMapTierPower = {}
        pClass.sTownList = []
        pClass.sTownWeightList = []
        pClass.sRandList = []
        pClass.sHighestCommonTier = 1
        
        # files with creatures
        archFiles = [{
            "mainFile": archFile,
            "idFile": mainArchFile
        }]
        
        if creaNCF:
            # if NCF is used, then load creas from files which names starts with "NCF"
            for (dirPath, dirNames, fileNames) in os.walk(dataFolder):
                for fileName in fileNames:
                    if fileName.startswith("NCF") and fileName.endswith(".pak"):
                        fileName = os.path.join(dirPath, fileName)
                        archFiles.append({
                            "mainFile": fileName,
                            "idFile": fileName
                        })
        
        # load from file
        for archFile in archFiles:
            loadedCreas = []
            
            def loadIdsFromArch(pArchFile):
                archFilePaths = arch.namelist()
                for crea in loadedCreas:
                    creaFileEndPos = crea.mShared.find(".xdb")
                    if creaFileEndPos != -1:
                        creaFile = crea.mShared[:creaFileEndPos + 4]
                        if creaFile.startswith("/"):
                            creaFile = creaFile[1:]
                        if creaFile in archFilePaths:
                            with arch.open(creaFile, "r") as dataFile:
                                tree = ET.parse(dataFile)
                                root = tree.getroot()
                                if root.tag == "AdvMapMonsterShared":
                                    crea.setIdFromXml(root)
            
            # load desc from arch
            with zipfile.ZipFile(archFile["mainFile"], "r") as arch:
                for archFilePath in arch.namelist():
                    if archFilePath.startswith("GameMechanics/Creature/Creatures/") and archFilePath.endswith(".xdb"):
                        with arch.open(archFilePath, "r") as dataFile:
                            tree = None
                            try:
                                tree = ET.parse(dataFile)
                            except:
                                continue
                            
                            root = tree.getroot()
                            if root.tag == "Creature":
                                # add to list
                                crea = Creature.fromXml(root)
                                if crea is None or len(crea.mShared) == 0:
                                    Log.warning("Creature error! ({})".format(archFilePath))
                                else:
                                    loadedCreas.append(crea)
                
                if archFile["mainFile"] == archFile["idFile"]:
                    # load ids from this arch
                    loadIdsFromArch(arch)
            
            if archFile["mainFile"] != archFile["idFile"]:
                # load ids from other arch
                with zipfile.ZipFile(archFile["idFile"], "r") as arch:
                    loadIdsFromArch(arch)
            
            # register loaded creas
            for crea in loadedCreas:
                if len(crea.mId) == 0:
                    otherCrea = Creature.getByShared(crea.mShared)
                    if otherCrea is None:
                        Log.warning("Creature id not found! ({})".format(crea.mShared))
                    else:
                        # creature with this shared is already registered
                        # id is empty because shared point out to other file
                        Log.warning("Creature alredy exist! ({})".format(crea.mShared))
                    continue
                
                pClass.sAll.append(crea)
                pClass.sMapId[crea.mId] = crea
                pClass.sMapShared[crea.mShared] = crea
                
                if crea.mCanGen:
                    if crea.mTown not in pClass.sMap:
                        pClass.sMap[crea.mTown] = {}
                    if crea.mTier not in pClass.sMap[crea.mTown]:
                        pClass.sMap[crea.mTown][crea.mTier] = []
                    pClass.sMap[crea.mTown][crea.mTier].append(crea)
        
        # fill sTownList and sTownWeightList
        for townId in pClass.sMap:
            pClass.sTownList.append(townId)
            
            if creaNeutralRatio != 0:
                if creaNeutralRatio < 0:
                    # decreasing chance of neutral creas
                    pClass.sTownWeightList.append(townId)
                    if townId != "TOWN_NO_TYPE":
                        for i in range(creaNeutralRatio * -1):
                            pClass.sTownWeightList.append(townId)
                else:
                    # increasing chance of neutral creas
                    if townId != "TOWN_NO_TYPE":
                        pClass.sTownWeightList.append(townId)
                    else:
                        for i in range(2 ** creaNeutralRatio):
                            pClass.sTownWeightList.append(townId)
            else:
                pClass.sTownWeightList.append(townId)
        
        # find sHighestCommonTier
        pClass.sHighestCommonTier = 100
        for townId in pClass.sTownList:
            if pClass.sHighestCommonTier not in pClass.sMap[townId] and townId != "TOWN_NO_TYPE":
                pClass.sHighestCommonTier = len(pClass.sMap[townId])
                while pClass.sHighestCommonTier not in pClass.sMap[townId]:
                    pClass.sHighestCommonTier -= 1
        
        # fill sMapTierPower
        tierCreasCount = {}
        for townId in pClass.sMap:
            townCreas = pClass.sMap[townId]
            for tierId in townCreas:
                if tierId not in pClass.sMapTierPower:
                    pClass.sMapTierPower[tierId] = 0
                    tierCreasCount[tierId] = 0
                
                tierCreas = townCreas[tierId]
                for crea in tierCreas:
                    pClass.sMapTierPower[tierId] += crea.mPower
                    tierCreasCount[tierId] += 1
        
        for tierId in pClass.sMapTierPower:
            if tierCreasCount[tierId] > 0:
                pClass.sMapTierPower[tierId] = int(pClass.sMapTierPower[tierId] / tierCreasCount[tierId])
        
        # fill sRandList
        randTierList = [
            {"id": "CREATURE_RANDOM_MONSTER_ANY", "shared": "/MapObjects/Random/Random-Monster-Any.(AdvMapMonsterShared).xdb#xpointer(/AdvMapMonsterShared)"},
            {"id": "CREATURE_RANDOM_MONSTER_L1", "shared": "/MapObjects/Random/Random-Monster-L1.(AdvMapMonsterShared).xdb#xpointer(/AdvMapMonsterShared)"},
            {"id": "CREATURE_RANDOM_MONSTER_L2", "shared": "/MapObjects/Random/Random-Monster-L2.(AdvMapMonsterShared).xdb#xpointer(/AdvMapMonsterShared)"},
            {"id": "CREATURE_RANDOM_MONSTER_L3", "shared": "/MapObjects/Random/Random-Monster-L3.(AdvMapMonsterShared).xdb#xpointer(/AdvMapMonsterShared)"},
            {"id": "CREATURE_RANDOM_MONSTER_L4", "shared": "/MapObjects/Random/Random-Monster-L4.(AdvMapMonsterShared).xdb#xpointer(/AdvMapMonsterShared)"},
            {"id": "CREATURE_RANDOM_MONSTER_L5", "shared": "/MapObjects/Random/Random-Monster-L5.(AdvMapMonsterShared).xdb#xpointer(/AdvMapMonsterShared)"},
            {"id": "CREATURE_RANDOM_MONSTER_L6", "shared": "/MapObjects/Random/Random-Monster-L6.(AdvMapMonsterShared).xdb#xpointer(/AdvMapMonsterShared)"},
            {"id": "CREATURE_RANDOM_MONSTER_L7", "shared": "/MapObjects/Random/Random-Monster-L7.(AdvMapMonsterShared).xdb#xpointer(/AdvMapMonsterShared)"}
        ]
        for i, randTier in enumerate(randTierList):
            crea = Creature()
            crea.mId = randTier["id"]
            crea.mTown = "TOWN_RANDOM"
            crea.mTier = i if i != 0 else rand.randint(1, 7)
            crea.mPower = pClass.sMapTierPower[crea.mTier]
            crea.mShared = randTier["shared"]
            
            pClass.sMapId[crea.mId] = crea
            pClass.sMapShared[crea.mShared] = crea
            pClass.sRandList.append(crea)
        
        print("creatures loaded")
        
        if logCreaInit:
            for townId in pClass.sMap:
                print("town - {}:".format(townId))
                townCreas = pClass.sMap[townId]
                for tierId in townCreas:
                    print("tier - {}:".format(tierId))
                    tierCreas = townCreas[tierId]
                    for crea in tierCreas:
                        print("crea - ({} - {}) {}".format(crea.mPower, crea.mWeekGrow, crea.mId))
                print("")
        
            print("tier power:")
            for tierId in pClass.sMapTierPower:
                print("tier {} - {}".format(tierId, pClass.sMapTierPower[tierId]))
            print("")
    
    def isRand(self):
        return self.mTown == "TOWN_RANDOM"
    
    @classmethod
    def getById(pClass, pId):
        crea = None
        if pId in pClass.sMapId:
            crea = pClass.sMapId[pId]
        return crea
        
    @classmethod
    def getByShared(pClass, pShared):
        crea = None
        if pShared in pClass.sMapShared:
            crea = pClass.sMapShared[pShared]
        return crea
    
    @classmethod
    def getTierByPower(pClass, pPower):
        actTier = "1"
        actTierPower = 0
        # select tier with equal or little lower power
        for tierId in pClass.sMapTierPower:
            tierPower = pClass.sMapTierPower[tierId]
            if tierPower <= pPower and actTierPower < tierPower:
                actTier = tierId
                actTierPower = tierPower
        return int(actTier)
    
    @classmethod
    def getPowerByTier(pClass, pTier):
        power = 1
        if pTier in pClass.sMapTierPower:
            power = pClass.sMapTierPower[pTier]
        return power
    
    @classmethod
    def getBasicStackPowerByTier(pClass, pTier):
        count = [20, 30, 26, 20, 14, 11, 5.5, 3, 2, 1][pTier - 1]
        power = 1
        if pTier in pClass.sMapTierPower:
            power = pClass.sMapTierPower[pTier]
        return power * count
    
    @classmethod
    def getRandomTownId(pClass):
        return rand.choice(pClass.sTownWeightList)
    
    @classmethod
    def getTownCreatures(pClass, pTownId):
        return pClass.sMap[pTownId]
    
    @classmethod
    def getRandomCreature(pClass, pTierId):
        return pClass.sRandList[pTierId]
    
    @classmethod
    def townHasTier(pClass, pTownId, pTier):
        return pTier in pClass.sMap[pTownId] and len(pClass.sMap[pTownId][pTier]) > 0


class Army:
    def __init__(self):
        self.mMood = "MONSTER_MOOD_AGGRESSIVE"
        self.mCourage = "MONSTER_COURAGE_CAN_FLEE_JOIN"
        self.mUnits = []
    
    def __repr__(self):
        resStr = "army {} - {} - {}\n".format(self.getPower(), len(self.mUnits), self.mMood)
        for unit in self.mUnits:
            resStr += "\tunit {} - {} - {}\n".format(self.getPower(unit), unit["count"], unit["crea"].mId)
        return resStr
    
    def getPower(self, pUnit=None):
        power = 0
        if pUnit is not None:
            power = pUnit["crea"].mPower * pUnit["count"]
        else:
            for unit in self.mUnits:
                power += unit["crea"].mPower * unit["count"]
        return power
    
    def addUnit(self, pCrea, pCount):
        wasAdded = False
        if pCount == 0:
            pCount = 1 # can be problem? place only where needed?
        for unit in self.mUnits:
            if unit["crea"].mId == pCrea.mId:
                unit["count"] += pCount
                wasAdded = True
        if not wasAdded:
            self.mUnits.append({"crea": pCrea, "count": pCount})
    
    @staticmethod
    def fromXml(pXml):
        if pXml is not None:
            obj = Army()
            obj.mMood = pXml.findtext("Mood", "")
            obj.mCourage = pXml.findtext("Courage", "")
            
            crea = Creature.getByShared(pXml.find("Shared").get("href", ""))
            if crea is not None:
                creaCount = int(pXml.findtext("Amount", "0"))
                creaCount2 = int(pXml.findtext("Amount2", "0"))
                if creaCount2 > creaCount:
                    # range
                    creaCount = round((creaCount + creaCount2) / 2)
                
                creaIsCustom = pXml.findtext("Custom", "true") == "true"
                if not creaIsCustom:
                    # random size
                    creaCount = round(Creature.getBasicStackPowerByTier(crea.mTier) / crea.mPower)
                
                if crea is not None and creaCount > 0:
                    obj.mUnits.append({"crea": crea, "count": creaCount})
            
            otherUnits = pXml.find("AdditionalStacks")
            if otherUnits is not None:
                for unit in otherUnits:
                    crea = Creature.getById(unit.findtext("Creature", ""))
                    if crea is not None:
                        creaCount = int(unit.findtext("Amount", "0"))
                        creaCount2 = int(unit.findtext("Amount2", "0"))
                        if creaCount2 > creaCount:
                            # range
                            creaCount = round((creaCount + creaCount2) / 2)
                        
                        creaIsCustom = unit.findtext("CustomAmount", "true") == "true"
                        if not creaIsCustom:
                            # random size
                            creaCount = round(Creature.getBasicStackPowerByTier(crea.mTier) / crea.mPower)
                        
                        if crea is not None and creaCount > 0:
                            obj.mUnits.append({"crea": crea, "count": creaCount})
            
            if len(obj.mUnits) > 0:
                return obj
        
        return None
    
    def toXml(self, pXml):
        if pXml is not None and len(self.mUnits) > 0:
            highestUnitIndex = 0
            highestUnitPower = 0
            for i, unit in enumerate(self.mUnits):
                unitPower = self.getPower(unit)
                if highestUnitPower < unitPower:
                    highestUnitPower = unitPower
                    highestUnitIndex = i
            
            pXml.find("Mood").text = self.mMood
            pXml.find("Courage").text = self.mCourage
            pXml.find("Shared").set("href", self.mUnits[highestUnitIndex]["crea"].mShared)
            pXml.find("Amount").text = str(self.mUnits[highestUnitIndex]["count"])
            pXml.find("Amount2").text = "0"
            pXml.find("Custom").text = "true"
            
            otherUnits = pXml.find("AdditionalStacks")
            if otherUnits is not None:
                pXml.remove(otherUnits)
            
            otherUnits = ET.SubElement(pXml, "AdditionalStacks")
            for i, unit in enumerate(self.mUnits):
                if i != highestUnitIndex:
                    unitDesc = ET.SubElement(otherUnits, "Item")
                    ET.SubElement(unitDesc, "Creature").text = unit["crea"].mId
                    ET.SubElement(unitDesc, "Amount").text = str(unit["count"])
                    ET.SubElement(unitDesc, "Amount2").text = "0"
                    ET.SubElement(unitDesc, "CustomAmount").text = "true"
    
    def isRand(self):
        for unit in self.mUnits:
            if not unit["crea"].isRand():
                return False
        return True
    
    @classmethod
    def getAlt(pClass, pArmy):
        # create alt army
        altArmy = Army()
        altArmy.mMood = pArmy.mMood
        altArmy.mCourage = pArmy.mCourage
        
        if creaMoodChange:
            altArmy.mMood = rand.choice(creaMoodList) # sel mood
        
        armyPower = pArmy.getPower() * creaPowerRatio # sel new power
        isGroup = not creaRandom and rand.random() < creaGroupRatio and armyPower  > 100
        
        if not isGroup:
            # single unit
            randCount = 2 + int(20 * rand.random() * 2) # basic count is 2 + (0 - 39)
            if randCount == 0:
                randCount = 1
            tier = Creature.getTierByPower(armyPower / randCount) # sel basic tier
            
            if creaRandom:
                # random unit
                if tier > 7:
                    tier = 7
                tierPower = Creature.getPowerByTier(tier)
                count = int(armyPower / tierPower) # real count
                addOneRatio = (armyPower - (tierPower * count)) / tierPower # how big part of one unit is missing
                if rand.random() < addOneRatio:
                    count += 1 # add one to real count
                
                # set tier and count
                crea = Creature.getRandomCreature(tier)
                altArmy.addUnit(crea, count)
            else:
                # specific unit
                # select town
                townId = None
                while townId is None:
                    townId = Creature.getRandomTownId()
                    if not Creature.townHasTier(townId, tier):
                        townId = None
                        if tier > Creature.sHighestCommonTier:
                            tier = Creature.sHighestCommonTier
                
                # may change tier
                tierChangeRatio = 0.10
                canTierDown = Creature.townHasTier(townId, tier - 1)
                canTierUp = randCount >= 5 and Creature.townHasTier(townId, tier + 1)
                randNum = rand.random()
                if canTierDown and randNum < tierChangeRatio:
                    tier -= 1
                elif canTierUp and randNum >= (1 - tierChangeRatio):
                    tier += 1
                
                # sel creature and count
                tierCreas = Creature.getTownCreatures(townId)[tier]
                crea = rand.choice(tierCreas)
                count = int(armyPower / crea.mPower) # real count
                addOneRatio = (armyPower - (crea.mPower * count)) / crea.mPower # how big part of one unit is missing
                if rand.random() < addOneRatio:
                    count += 1 # add one to real count
                
                altArmy.addUnit(crea, count) # set unit
        else:
            # group
            # select highest tier
            highUnitPower = armyPower / 3 / 2
            highUnitTier = Creature.getTierByPower(highUnitPower)
            
            # select town
            townId = None
            while townId is None:
                townId = Creature.getRandomTownId()
                if not Creature.townHasTier(townId, highUnitTier):
                    townId = None
                    if highUnitTier > Creature.sHighestCommonTier:
                        highUnitTier = Creature.sHighestCommonTier
            
            # find available tiers
            canSelTierList = []
            for i in range(highUnitTier, highUnitTier - 4, -1):
                if Creature.townHasTier(townId, i):
                    canSelTierList.append(i)
            
            # sel group size
            minGroupSize = 2 if len(canSelTierList) > 1 else 1
            groupSize = rand.randint(minGroupSize, len(canSelTierList))
            
            # sel tiers in group
            tierList = []
            if groupSize == len(canSelTierList):
                tierList = canSelTierList
            else:
                while len(tierList) < groupSize:
                    i = rand.choice(canSelTierList)
                    tierList.append(i)
            
            ratioBasedChoose = False
            ratioList = []
            if ratioBasedChoose:
                # sel tiers ratio (is needed? random add may would be better?)
                fullRatio = 0
                for i in range(0, groupSize):
                    ratio = rand.random()
                    fullRatio += ratio
                    ratioList.append(ratio)
                minRatio = fullRatio * (1 / (groupSize + 2))
                maxRatio = fullRatio - (minRatio * groupSize)
                usedRatio = 0
                for i, ratio in enumerate(ratioList):
                    if ratio < minRatio:
                        ratioList[i] = minRatio
                    elif ratio > maxRatio:
                        ratioList[i] = maxRatio
                    usedRatio += ratioList[i]
                    ratioList[i] = (1 / fullRatio) * ratioList[i] * 100 # ratio to percentage
                # sum is not 100% so we multiply it (may not needed - would be more dinamic - would boost stronger creatures)
                usedRatioMult = fullRatio / usedRatio
                for i, ratio in enumerate(ratioList):
                    ratioList[i] *= usedRatioMult
                
                powerBit = armyPower / 100 # 1 percent of power
            
            # sel creatures and their counts
            armyPowerLeft = armyPower
            townCreas = Creature.getTownCreatures(townId)
            creas = []
            for i, tier in enumerate(tierList):
                crea = rand.choice(townCreas[tier])
                count = 0
                if ratioBasedChoose:
                    count = int((powerBit * ratioList[i]) / crea.mPower)
                armyPowerLeft -= count * crea.mPower
                creas.append({"crea": crea, "count": count})
            
            # add missing power to army
            # 10% of missing army has 160% chance of adding (1% has 16%)
            while armyPowerLeft > 0 and rand.random() < ((armyPowerLeft / armyPower) * 16):
                crea = rand.choice(creas)
                addOneRatio = armyPowerLeft / crea["crea"].mPower # how big part of this creature is missing
                if rand.random() < addOneRatio:
                    crea["count"] += 1
                    armyPowerLeft -= crea["crea"].mPower
            
            # move creatures and their counts to army
            for crea in creas:
                if crea["count"] > 0:
                    altArmy.addUnit(crea["crea"], crea["count"])
            
            if len(altArmy.mUnits) == 0:
                # army is empty - add one creature
                altArmy.addUnit(creas[0]["crea"], 1)
        
        return altArmy


class Town:
    sAll = []
    sMapId = {}
    
    def __init__(self):
        self.mId = ""
        self.mPlayer = ""
        self.mObj = None
    
    @staticmethod
    def fromXml(pXml):
        obj = None
        if pXml is not None:
            obj = Town()
            obj.mId = pXml.get("id", "")
            obj.mObj = pXml
            desc = pXml.find("AdvMapTown")
            if desc is not None:
                obj.mPlayer = desc.findtext("PlayerID", "PLAYER_NONE")
        
        return obj
    
    @classmethod
    def init(pClass, pMapTree):
        if pMapTree is None:
            return
        
        root = pMapTree.getroot()
        allTowns = root.findall("./objects/Item[@href='#n:inline(AdvMapTown)']")
        
        # fill list
        pClass.sAll = []
        pClass.sMapId = {}
        
        for item in allTowns:
            town = Town.fromXml(item)
            if town is not None:
                pClass.sAll.append(town)
                pClass.sMapId[town.mId] = town
        
        #print("towns loaded: {}".format(len(pClass.sAll)))
    
    @classmethod
    def getById(pClass, pId):
        town = None
        if pId in pClass.sMapId:
            town = pClass.sMapId[pId]
        return town
    
    def hasPlayer(self):
        return self.mPlayer != "PLAYER_NONE"


class Map:
    def __init__(self, pFileName):
        self.mTree = None
        self.mFileName = pFileName
        self.mDataFileName = None
        self.mTempFolder = ".tempMapFolder6541351"
        self.mBckExt = ".bck"
        self.useDirectAccess = False and sys.version_info.major >= 3 and sys.version_info.minor >= 6
    
    def load(self):
        if (self.mFileName is not None 
                and os.path.exists(self.mFileName)):
            
            fileName = self.mFileName
            if loadMapFromBck and os.path.exists(self.mFileName + self.mBckExt):
                # load map from backup
                fileName = self.mFileName + self.mBckExt
            
            with zipfile.ZipFile(fileName, "r") as arch:
                filePaths = arch.namelist()
                for filePath in filePaths:
                    if filePath.endswith("map.xdb"):
                        # found map file path
                        self.mDataFileName = filePath
                        
                        if self.useDirectAccess:
                            with arch.open(self.mDataFileName, "r") as archInnerFile:
                                # load map xml tree
                                self.mTree = ET.parse(archInnerFile)
                        else:
                            if os.path.exists(self.mTempFolder):
                                shutil.rmtree(self.mTempFolder)
                            # extract map arch to temp folder
                            arch.extractall(self.mTempFolder)
                        
                            # load map xml tree
                            self.mTree = ET.parse(os.path.join(self.mTempFolder, self.mDataFileName))
                        
                        print("map loaded ({})".format(self.mFileName))
                        break
            
            Town.init(self.mTree)
    
    def save(self):
        if (self.mTree is not None 
                and self.mFileName is not None 
                and len(self.mFileName) > 0
                and self.mDataFileName is not None 
                and (self.useDirectAccess or os.path.exists(os.path.join(self.mTempFolder, self.mDataFileName)))):
            
            if createMapBck and os.path.exists(self.mFileName) and not os.path.exists(self.mFileName + self.mBckExt):
                # backup does not exist - create it - before we change original map file
                os.rename(self.mFileName, self.mFileName + self.mBckExt)
            
            if self.useDirectAccess:
                # direct save to zip file
                # TODO: copy arch from backup (if available/needed)?
                # INFO: not tested!
                with zipfile.ZipFile(self.mFileName, "a", zipfile.ZIP_DEFLATED) as arch:
                    with arch.open(self.mDataFileName, "w") as archInnerFile:
                        # write map xml tree to file
                        self.mTree.write(archInnerFile, "UTF-8", True)
            else:
                # write map xml tree to temp file
                self.mTree.write(os.path.join(self.mTempFolder, self.mDataFileName), "UTF-8", True)
                
                # compress content of temp folder to map arch and remove temp folder
                with zipfile.ZipFile(self.mFileName, "w", zipfile.ZIP_DEFLATED) as arch:
                    files = []
                    for (dirPath, dirNames, fileNames) in os.walk(self.mTempFolder):
                        for fileName in fileNames:
                            files.append(os.path.join(dirPath, fileName))

                    tempFileNamePrefixLen = len(self.mTempFolder + "/")
                    for f in files:
                        arch.write(f, f[tempFileNamePrefixLen:])
                    shutil.rmtree(self.mTempFolder)
            
            print("map saved")
    
    def changeArtifacts(self):
        if self.mTree is None:
            return
        
        root = self.mTree.getroot()
        items = root.find("objects")
        artifactsChanged = 0
        artifactsCount = {}
        
        # change artifacts on map
        for item in items:
            href = item.get("href", "")
            if href == "#n:inline(AdvMapArtifact)":
                art = item.find("AdvMapArtifact")
                if art is not None:
                    artShared = art.find("Shared")
                    if artShared is not None:
                        oldArt = Artifact.getByShared(artShared.get("href", ""))
                        if oldArt is not None and (not artChangeOnlyRandom or oldArt.isRand()):
                            artifactsChanged += 1
                            newArt = Artifact.getAlt(oldArt)
                            artShared.set("href", newArt.mShared)
                            
                            if newArt.mType not in artifactsCount:
                                artifactsCount[newArt.mType] = 0
                            artifactsCount[newArt.mType] += 1
                            
                            if logArtChange:
                                print("artifact change:")
                                print("old: {}".format(oldArt.mShared))
                                print("new: {}\n".format(newArt.mShared))
        
        # allow all artifacts
        allowedArtifactsNode = root.find("artifactIDs")
        if allowedArtifactsNode is None:
            allowedArtifactsNode = ET.SubElement(root, "artifactIDs")
        allowedArtifactsNode.clear()
        
        print("artifacts changed: {}".format(artifactsChanged))
        
        if logMapInfo:
            # new map info
            print("ARTIFACT COUNT (new map):")
            for artType in artifactsCount:
                print("{}: {}".format(artType, artifactsCount[artType]))
            print("")
    
    def changeCreatures(self):
        if self.mTree is None:
            return
        
        root = self.mTree.getroot()
        items = root.find("objects")
        creaturesChanged = 0
        
        armies = []
        powerDownDiff = 0
        powerDownCount = 0
        powerDownMaxDiff = 0
        powerUpDiff = 0
        powerUpCount = 0
        powerUpMaxDiff = 0
        
        # change creatures on map
        for item in items:
            href = item.get("href", "")
            if href == "#n:inline(AdvMapMonster)":
                armyXml = item.find("AdvMapMonster")
                if armyXml is not None:
                    army = Army.fromXml(armyXml)
                    if army is not None and (not creaChangeOnlyRandom or army.isRand()):
                        armies.append(army)
                        creaturesChanged += 1
                        altArmy = Army.getAlt(army)
                        altArmy.toXml(armyXml)
                        
                        if logCreaChange:
                            armyPower = army.getPower()
                            armyPowerDiff = (altArmy.getPower() - armyPower) / (armyPower / 100)
                            if armyPowerDiff < 0:
                                powerDownDiff += armyPowerDiff
                                powerDownCount += 1
                                if powerDownMaxDiff > armyPowerDiff:
                                    powerDownMaxDiff = armyPowerDiff
                            elif armyPowerDiff > 0:
                                powerUpDiff += armyPowerDiff
                                powerUpCount += 1
                                if powerUpMaxDiff < armyPowerDiff:
                                    powerUpMaxDiff = armyPowerDiff
                            
                            print("creature change: {:.2f}%".format(armyPowerDiff))
                            print("old:\n{}".format(army))
                            print("new:\n{}\n".format(altArmy))
        
        if logCreaChange and len(armies) > 0:
            print("power diff: {:.2f}%".format((powerDownDiff + powerUpDiff) / (powerDownCount + powerUpCount)))
            if powerDownCount > 0:
                print("power down - avr: {:.2f}% max: {:.2f}%".format(powerDownDiff / powerDownCount, powerDownMaxDiff))
            if powerUpCount > 0:
                print("power up - avr:    {:.2f}% max:  {:.2f}%\n".format(powerUpDiff / powerUpCount, powerUpMaxDiff))
        
        print("creatures changed: {}".format(creaturesChanged))
        
        if logMapInfo:
            # old map info
            print("ARMIES (old map):")
            lowArmy = {}
            highArmy = {}
            tierLowArmy = {}
            tierHighArmy = {}
            for army in armies:
                armySize = len(army.mUnits)
                armyPower = army.getPower()
                if armySize not in lowArmy or lowArmy[armySize]["power"] > armyPower:
                    lowArmy[armySize] = {"army": army, "power": armyPower}
                if armySize not in highArmy or highArmy[armySize]["power"] < armyPower:
                    highArmy[armySize] = {"army": army, "power": armyPower}
                for unit in army.mUnits:
                    crea = unit["crea"]
                    if crea.mTier not in tierLowArmy or tierLowArmy[crea.mTier]["power"] > armyPower:
                        tierLowArmy[crea.mTier] = {"army": army, "power": armyPower}
                    if crea.mTier not in tierHighArmy or tierHighArmy[crea.mTier]["power"] < armyPower:
                        tierHighArmy[crea.mTier] = {"army": army, "power": armyPower}
        
            print("LOW ARMIES:")
            for i in lowArmy:
                print(lowArmy[i]["army"])
            print("HIGH ARMIES:")
            for i in highArmy:
                print(highArmy[i]["army"])
            print("TIER LOW ARMIES:")
            for i in tierLowArmy:
                print("tier: {}".format(i))
                print(tierLowArmy[i]["army"])
            print("TIER HIGH ARMIES:")
            for i in tierHighArmy:
                print("tier: {}".format(i))
                print(tierHighArmy[i]["army"])
    
    def changeWaterObjects(self):
        if self.mTree is None:
            return
        
        root = self.mTree.getroot()
        
        # set ReflectiveWater to true
        reflectiveWaterNode = root.find("ReflectiveWater")
        if reflectiveWaterNode is None:
            reflectiveWaterNode = ET.SubElement(root, "ReflectiveWater")
        reflectiveWaterNode.text = "true"
        
        # water objects lists
        oneSquareWaterTreaList = [
            {"weight": 12, "type": "floatsam", "shared": "/MapObjects/Floatsam.(AdvMapTreasureShared).xdb#xpointer(/AdvMapTreasureShared)"},
            {"weight": 6, "type": "chest", "shared": "/MapObjects/Sea_Chest.(AdvMapTreasureShared).xdb#xpointer(/AdvMapTreasureShared)"},
            {"weight": 1, "type": "special", "shared": "/MapObjects/Water/Shipwrecks_2/PeasantWreck.xdb#xpointer(/AdvMapTreasureShared)"},
            {"weight": 1, "type": "special", "shared": "/MapObjects/Water/Shipwrecks_2/FootmanWreck.xdb#xpointer(/AdvMapTreasureShared)"}
        ]
        oneSquareWaterObjList = [
            {"weight": 1, "type": "combat", "shared": "/MapObjects/Water/Damaged_Boats_2/Unkempt_Junk.xdb#xpointer(/AdvMapBuildingShared)"},
            {"weight": 1, "type": "combat", "shared": "/MapObjects/Water/Damaged_Boats_2/Unkempt_Galley.xdb#xpointer(/AdvMapBuildingShared)"},
            {"weight": 1, "type": "combat", "shared": "/MapObjects/Water/Damaged_Boats_2/Unkempt_Galleon.xdb#xpointer(/AdvMapBuildingShared)"},
            {"weight": 1, "type": "combat", "shared": "/MapObjects/Water/Damaged_Boats_2/Demolish_Galleon.xdb#xpointer(/AdvMapBuildingShared)"},
            {"weight": 1, "type": "combat", "shared": "/MapObjects/Water/Damaged_Boats_2/Demolish_Galley.xdb#xpointer(/AdvMapBuildingShared)"},
            {"weight": 1, "type": "combat", "shared": "/MapObjects/Water/Damaged_Boats_2/Demolish_Junk.xdb#xpointer(/AdvMapBuildingShared)"},
            {"weight": 1, "type": "other", "shared": "/MapObjects/Sirens.(AdvMapBuildingShared).xdb#xpointer(/AdvMapBuildingShared)"},
            {"weight": 1, "type": "other", "shared": "/MapObjects/Mermaids.(AdvMapBuildingShared).xdb#xpointer(/AdvMapBuildingShared)"},
            {"weight": 1, "type": "other", "shared": "/MapObjects/Buoy.(AdvMapBuildingShared).xdb#xpointer(/AdvMapBuildingShared)"}
        ]
        
        def getSharedList(mList, byWeight):
            lList = []
            for obj in mList:
                if not byWeight:
                    lList.append(obj["shared"])
                else:
                    for i in range(obj["weight"]):
                        lList.append(obj["shared"])
            return lList
        
        oneSquareWaterTreasShared = getSharedList(oneSquareWaterTreaList, False)
        oneSquareWaterObjsShared = getSharedList(oneSquareWaterObjList, False)
        
        oneSquareWaterTreasSharedWeight = getSharedList(oneSquareWaterTreaList, True)
        oneSquareWaterObjsSharedWeight = getSharedList(oneSquareWaterObjList, True)
        
        # ratios
        waterObjDelRatio = 0.0
        waterTreaRatio = 0.7
        
        # counts
        oldOneSquareWaterItemsCount = {}
        newOneSquareWaterItemsCount = {}
        
        oneSquareWaterItems = []
        
        items = root.find("objects")
        
        # load water objects
        for item in items:
            itemHref = item.get("href", "")
            isTreasure = itemHref == "#n:inline(AdvMapTreasure)"
            isBuilding = itemHref == "#n:inline(AdvMapBuilding)"
            if isTreasure or isBuilding:
                innerItem = item.find("AdvMapTreasure" if isTreasure else "AdvMapBuilding")
                if innerItem is not None:
                    innerItemShared = innerItem.find("Shared")
                    if innerItemShared is not None:
                        innerItemSharedValue = innerItemShared.get("href", "")
                        if ((isTreasure and innerItemSharedValue in oneSquareWaterTreasShared) 
                            or (isBuilding and innerItemSharedValue in oneSquareWaterObjsShared)):
                            
                            if innerItemSharedValue not in oldOneSquareWaterItemsCount:
                                oldOneSquareWaterItemsCount[innerItemSharedValue] = 0
                            oldOneSquareWaterItemsCount[innerItemSharedValue] += 1
                            
                            # remove some sub elements
                            tagsToRemove = ["IsCustom", "Amount", "MessageFileRef", "PlayerID", "GroupID", "showCameras"]
                            for tagToRemove in tagsToRemove:
                                someItem = innerItem.find(tagToRemove)
                                if someItem is not None:
                                    innerItem.remove(someItem)
                            
                            oneSquareWaterItems.append({"item": item, "innerItem": innerItem})
        
        # change water objects
        for oneSquareWaterItem in oneSquareWaterItems:
            item = oneSquareWaterItem["item"]
            innerItem = oneSquareWaterItem["innerItem"]
            innerItemShared = innerItem.find("Shared")
            
            if rand.random() < waterObjDelRatio:
                # remove water object
                items.remove(item)
            else:
                isTreasure = rand.random() < waterTreaRatio
                if isTreasure:
                    # treasure
                    item.set("href", "#n:inline(AdvMapTreasure)")
                    innerItem.tag = "AdvMapTreasure"
                    innerItemShared.set("href", rand.choice(oneSquareWaterTreasSharedWeight))
                    
                    # add some sub elements
                    ET.SubElement(innerItem, "IsCustom").text = "false"
                    ET.SubElement(innerItem, "Amount").text = "0"
                    ET.SubElement(innerItem, "MessageFileRef").set("href", "")
                else:
                    # building
                    item.set("href", "#n:inline(AdvMapBuilding)")
                    innerItem.tag = "AdvMapBuilding"
                    innerItemShared.set("href", rand.choice(oneSquareWaterObjsSharedWeight))
                    
                    # add some sub elements
                    ET.SubElement(innerItem, "PlayerID").text = "PLAYER_NONE"
                    captureTriggerItem = ET.SubElement(innerItem, "CaptureTrigger")
                    captureTriggerActionItem = ET.SubElement(captureTriggerItem, "Action")
                    ET.SubElement(captureTriggerActionItem, "FunctionName")
                    ET.SubElement(innerItem, "GroupID").text = "0"
                    ET.SubElement(innerItem, "showCameras")
                
                innerItemSharedValue = innerItemShared.get("href", "")
                if innerItemSharedValue not in newOneSquareWaterItemsCount:
                    newOneSquareWaterItemsCount[innerItemSharedValue] = 0
                newOneSquareWaterItemsCount[innerItemSharedValue] += 1
        
        oldWaterObjCount = len(oneSquareWaterItems)
        
        print("water objects changed: {}".format(oldWaterObjCount))
        
        if logWaterChange and oldWaterObjCount > 0:
            def getCounts(pCountMap, pListObjs, pObjsType):
                totalValue = 0
                for obj in pListObjs:
                    if obj["type"] == pObjsType and obj["shared"] in pCountMap:
                        totalValue += pCountMap[obj["shared"]]
                return totalValue
            
            oldWaterTreaFloatsamCount = getCounts(oldOneSquareWaterItemsCount, oneSquareWaterTreaList, "floatsam")
            oldWaterTreaChestCount = getCounts(oldOneSquareWaterItemsCount, oneSquareWaterTreaList, "chest")
            oldWaterTreaSpecialCount = getCounts(oldOneSquareWaterItemsCount, oneSquareWaterTreaList, "special")
            oldWaterTreaCount = oldWaterTreaFloatsamCount + oldWaterTreaChestCount + oldWaterTreaSpecialCount
            oldWaterBuildCombatCount = getCounts(oldOneSquareWaterItemsCount, oneSquareWaterObjList, "combat")
            oldWaterBuildOtherCount = getCounts(oldOneSquareWaterItemsCount, oneSquareWaterObjList, "other")
            oldWaterBuildCount = oldWaterBuildCombatCount + oldWaterBuildOtherCount
            
            newWaterTreaFloatsamCount = getCounts(newOneSquareWaterItemsCount, oneSquareWaterTreaList, "floatsam")
            newWaterTreaChestCount = getCounts(newOneSquareWaterItemsCount, oneSquareWaterTreaList, "chest")
            newWaterTreaSpecialCount = getCounts(newOneSquareWaterItemsCount, oneSquareWaterTreaList, "special")
            newWaterTreaCount = newWaterTreaFloatsamCount + newWaterTreaChestCount + newWaterTreaSpecialCount
            newWaterBuildCombatCount = getCounts(newOneSquareWaterItemsCount, oneSquareWaterObjList, "combat")
            newWaterBuildOtherCount = getCounts(newOneSquareWaterItemsCount, oneSquareWaterObjList, "other")
            newWaterBuildCount = newWaterBuildCombatCount + newWaterBuildOtherCount
            newWaterObjCount = newWaterTreaCount + newWaterBuildCount
            newWaterDelObjCount = oldWaterObjCount - newWaterObjCount
            
            print("\nWATER OBJECTS COUNT (old map):")
            print("water objects - count: {}".format(oldWaterObjCount))
            if oldWaterObjCount > 0:
                print("water treasures - count: {} ({:.2f}%) (floatsam: {} ({:.2f}%) chest: {} ({:.2f}%) special: {} ({:.2f}%))".format(
                        oldWaterTreaCount, oldWaterTreaCount / oldWaterObjCount * 100, 
                        oldWaterTreaFloatsamCount, (oldWaterTreaFloatsamCount / oldWaterTreaCount * 100) if oldWaterTreaCount > 0 else 0, 
                        oldWaterTreaChestCount, (oldWaterTreaChestCount / oldWaterTreaCount * 100) if oldWaterTreaCount > 0 else 0, 
                        oldWaterTreaSpecialCount, (oldWaterTreaSpecialCount / oldWaterTreaCount * 100) if oldWaterTreaCount > 0 else 0))
                print("water buildings - count: {} ({:.2f}%) (combat: {} ({:.2f}%) other: {} ({:.2f}%))".format(
                        oldWaterBuildCount, oldWaterBuildCount / oldWaterObjCount * 100, 
                        oldWaterBuildCombatCount, (oldWaterBuildCombatCount / oldWaterBuildCount * 100) if oldWaterBuildCount > 0 else 0, 
                        oldWaterBuildOtherCount, (oldWaterBuildOtherCount / oldWaterBuildCount * 100) if oldWaterBuildCount > 0 else 0))
            print("")
            
            print("\nWATER OBJECTS COUNT (new map):")
            print("water objects - count: {} changed: {} ({:.2f}%) removed: {} ({:.2f}%)".format(
                    oldWaterObjCount, 
                    newWaterObjCount, newWaterObjCount / oldWaterObjCount * 100,
                    newWaterDelObjCount, newWaterDelObjCount / oldWaterObjCount * 100))
            if newWaterObjCount > 0:
                print("water treasures - count: {} ({:.2f}%) (floatsam: {} ({:.2f}%) chest: {} ({:.2f}%) special: {} ({:.2f}%))".format(
                        newWaterTreaCount, newWaterTreaCount / newWaterObjCount * 100, 
                        newWaterTreaFloatsamCount, (newWaterTreaFloatsamCount / newWaterTreaCount * 100) if newWaterTreaCount > 0 else 0, 
                        newWaterTreaChestCount, (newWaterTreaChestCount / newWaterTreaCount * 100) if newWaterTreaCount > 0 else 0, 
                        newWaterTreaSpecialCount, (newWaterTreaSpecialCount / newWaterTreaCount * 100) if newWaterTreaCount > 0 else 0))
                print("water buildings - count: {} ({:.2f}%) (combat: {} ({:.2f}%) other: {} ({:.2f}%))".format(
                        newWaterBuildCount, newWaterBuildCount / newWaterObjCount * 100, 
                        newWaterBuildCombatCount, (newWaterBuildCombatCount / newWaterBuildCount * 100) if newWaterBuildCount > 0 else 0, 
                        newWaterBuildOtherCount, (newWaterBuildOtherCount / newWaterBuildCount * 100) if newWaterBuildCount > 0 else 0))
            print("")
    
    def changeDwellings(self):
        if self.mTree is None:
            return
        
        highTierDwellsShared = [
            "/MapObjects/Random/RandomDwelling4.xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Random/RandomDwelling5.xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Random/RandomDwelling6.xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Random/RandomDwelling7.xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Haven/Heaven_Military_Post.(AdvMapDwellingShared).xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Inferno/InfernoMilitaryPost.(AdvMapDwellingShared).xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Necropolis/Necropolis_Military_Post.(AdvMapDwellingShared).xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Preserve/Preserve_Military_Post.xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Dungeon/Dungeon_Military_Post.xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Academy/Academy_Military_Post.xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Dwarven/DwarvenDwelling04.(AdvMapDwellingShared).xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Dwarven/DwarvenDwelling04.(AdvMapDwellingShared) (2).xdb#xpointer(/AdvMapDwellingShared)",
            "/MapObjects/Orcs/OrcishDwelling04.(AdvMapDwellingShared).xdb#xpointer(/AdvMapDwellingShared)"
        ]
        
        playerTownDwellSharedList = {}
        townDwellSharedList = {}
        playerMap = {}
        townMap = {}
        dwellsChanged = 0
        
        townIdPrefixLen = len("#xpointer(id(")
        townIdPostfixLen = len(")/AdvMapTown)")
        
        root = self.mTree.getroot()
        allDwells = root.findall("./objects/Item[@href='#n:inline(AdvMapDwelling)']/AdvMapDwelling")
        
        for dwell in allDwells:
            sharedNode = dwell.find("Shared")
            if sharedNode is not None:
                sharedValue = sharedNode.get("href", "")
                if sharedValue in highTierDwellsShared:
                    dwellsChanged += 1
                    
                    town = None
                    player = None
                    linkTownHref = dwell.find("LinkToTown").get("href", "")
                    if len(linkTownHref) > (townIdPrefixLen + townIdPostfixLen):
                        town = Town.getById(linkTownHref[townIdPrefixLen : len(linkTownHref) - townIdPostfixLen])
                    
                    if town is not None and town.hasPlayer():
                        player = town.mPlayer
                    else:
                        dwellPlayer = dwell.find("PlayerID").text
                        if dwellPlayer != "PLAYER_NONE":
                            player = dwellPlayer
                        """
                        # looks like LinkToPlayer do nothing
                        else:
                            dwellLinkPlayer = dwell.find("LinkToPlayer").text
                            if dwellLinkPlayer != "PLAYER_NONE":
                                player = dwellLinkPlayer
                        """
                    
                    if player is not None:
                        # player town (link) or player (owner)
                        # all players will have same dwellings
                        if player not in playerMap:
                            playerMap[player] = 0
                        if playerMap[player] not in playerTownDwellSharedList:
                            playerTownDwellSharedList[playerMap[player]] = rand.choice(dwellList)
                        sharedNode.set("href", playerTownDwellSharedList[playerMap[player]])
                        
                        playerMap[player] += 1
                    elif town is not None:
                        # non player town
                        # all non players towns will have same dwellings
                        if town.mId not in townMap:
                            townMap[town.mId] = 0
                        if townMap[town.mId] not in townDwellSharedList:
                            townDwellSharedList[townMap[town.mId]] = rand.choice(dwellList)
                        sharedNode.set("href", townDwellSharedList[townMap[town.mId]])
                        
                        townMap[town.mId] += 1
                    else:
                        # other
                        sharedNode.set("href", rand.choice(dwellList))
                    
                    dwell.find("RandomCreatures").text = "false"
                    dwell.find("creaturesEnabled").clear()
        
        print("high tier dwellings changed: {}".format(dwellsChanged))
    
    def buildTowns(self, townBuild, gamePowerLimit):
        townBuildStr = townBuild
        if gamePowerLimit:
            townBuildStr += "#TB_TOWN_HALL,1,3#TB_DWELLING_5,0,0#TB_DWELLING_6,0,0#TB_DWELLING_7,0,0"

        buildsTypes = []
        buildsList = []
        buildsListStr = townBuildStr.split("#")

        for buildOptionsStr in buildsListStr:
            buildOptions = buildOptionsStr.split(",")
            buildObj = {
                "Type": buildOptions[0],
                "InitialUpgrade": "BLD_UPG_" + (buildOptions[1] if buildOptions[1] != "0" else "NONE"),
                "MaxUpgrade": "BLD_UPG_" + ((buildOptions[2] if buildOptions[2] != "0" else "NONE") if len(buildOptions) >= 3 else "5"),
                "Player": buildOptions[3] if len(buildOptions) == 4 else "ALL"
            }
            buildsTypes.append(buildObj["Type"])
            buildsList.append(buildObj)
        
        for town in Town.sAll:
            townInnerObj = town.mObj.find("AdvMapTown")
            townBuilds = townInnerObj.find("buildings")
            
            for build in buildsList:
                if build["Player"] != "ALL":
                    townPlayerID = townInnerObj.find("PlayerID").text

                    if build["Player"] == "PLAYER":
                        if townPlayerID == "PLAYER_NONE":
                            continue
                    elif build["Player"] == "NONE":
                        if townPlayerID != "PLAYER_NONE":
                            continue
                    elif townPlayerID != ("PLAYER_" + build["Player"]):
                        continue
                
                for townBuild in townBuilds:
                    if townBuild.find("Type").text == build["Type"]:
                        townBuilds.remove(townBuild)
                        break
                
                buildDesc = ET.SubElement(townBuilds, "Item")
                ET.SubElement(buildDesc, "Type").text = build["Type"]
                ET.SubElement(buildDesc, "InitialUpgrade").text = build["InitialUpgrade"]
                ET.SubElement(buildDesc, "MaxUpgrade").text = build["MaxUpgrade"]
        
        print("towns buildings changed")
    
    def enableScripts(self):
        if self.mTree is None:
            return
        
        root = self.mTree.getroot()
        mapScriptNode = root.find("MapScript")
        
        if mapScriptNode is None:
            mapScriptNode = ET.SubElement(root, "MapScript")
        
        if len(mapScriptNode.get("href", "")) == 0:
            mapScriptNode.set("href", "MapScript.xdb#xpointer(/Script)")
            print("scripts enabled")


# main func
def run(pArgs=None):
    if pArgs is None:
        pArgs = sys.argv[1:]
    parseArgs(pArgs)
    
    if artChange or creaChange or enableScripts or waterChange or dwellChange or len(townBuild) != 0 or gamePowerLimit:
        Artifact.init()
        Creature.init()
        
        for mapFile in mapFiles:
            print("")
            gameMap = Map(mapFile)
            gameMap.load()
            
            if artChange:
                gameMap.changeArtifacts()
            if creaChange:
                gameMap.changeCreatures()
            if enableScripts:
                gameMap.enableScripts()
            if waterChange:
                gameMap.changeWaterObjects()
            if dwellChange:
                gameMap.changeDwellings()
            if len(townBuild) != 0 or gamePowerLimit:
                gameMap.buildTowns(townBuild, gamePowerLimit)
            
            gameMap.save()


if __name__ == "__main__":
    # prog execution
    try:
        run()
    except MyException as ex:
        print(str(ex))
        sys.exit()

