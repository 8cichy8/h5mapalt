#!/usr/bin/env python3
# -*- encoding: UTF-8 -*-
#
# AUTHOR:      Zich Robert (cichy)
# VERSION:     1.2.0
# DESCRIPTION: See help.
#

import os, sys
import random as rand
import shutil, zipfile
import xml.etree.ElementTree as ET


def printHelp():
    if guiIsShown:
        return
    
    print("""
Execution: python script.py [OPTIONS] mapFile.h5m

This script can change creatures/artifacts on homm5/mmh55 maps.
Script expects it is in Maps folder of Tribes of the East.

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
    --artChange=true            To change artifacts(art).
    --creaChange=true           To change creature(crea).
    
    --artRandom=false           To randomize art.
    --creaRandom=false          To randomize crea.
    --creaPowerRatio=1.0        Will modify crea power.
    --creaGroupRatio=0.55       Will modify chance to crea be group (1.0 == highest, but not 100%).
    --creaMoodRatio=0,3,2,1     Will modify crea mood (probably does not affect groups).
                                    - mood order: FRIENDLY,AGGRESSIVE,HOSTILE,WILD
                                    - value "1,1,0,0" would give us 50% FRIENDLY and 50% AGGRESSIVE
    --creaNeutralReduction=2    To reduce chance of neutrals to be placed on map.
                                    - chanceToPlaceOnMap = 1 / townsCount / (creaNeutralReduction + 1)
    --creaNCF=false             To load and work with NCF creatures.
                                    - will look for files in data folder, which names starts with "NCF"
                                    - if NFC is used, then --creaNeutralReduction=0 should be set (probably)

    --nogui                     To run console version (in gui version)
    --pathToGameFolder=../      Path to game folder.
    --loadMapFromBck=true       To load map from backup file (backup file is generated with first change).
                                    - better to leave true
    
    --logArtInit=false          To log art init info.
    --logArtChange=false        To log art change info.
    --logCreaInit=false         To log crea init info.
    --logCreaChange=false       To log crea change info.
    --logMapInfo=false          To log some map(old/new) info.
    --logWarnings=false         To log warnings/errors.
    """)

"""
NOTES:
    --creaPowerRatio=1.0 is not 100% group, because if all units in group are of one creature, then it will lead to group of one unit
"""

# reset args func
def resetArgs():
    g = globals()
    g["mapFile"] = None
    g["pathToGameFolder"] = "../"
    g["loadMapFromBck"] = "true"

    g["artChange"] = "true"
    g["creaChange"] = "true"

    g["artRandom"] = "false"
    g["creaRandom"] = "false"
    g["creaMoodRatio"] = "0,3,2,1"
    g["creaPowerRatio"] = "1.0"
    g["creaGroupRatio"] = "0.55"
    g["creaNeutralReduction"] = "2"
    g["creaNCF"] = "false"

    g["logArtInit"] = "false"
    g["logArtChange"] = "false"
    g["logCreaInit"] = "false"
    g["logCreaChange"] = "false"
    g["logMapInfo"] = "false"
    g["logWarnings"] = "false"
    
    # no args
    g["guiIsShown"] = False
    g["creaNeutralChanceList"] = None
    g["creaMoodList"] = None
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
        "pathToGameFolder", "loadMapFromBck", "artChange", "creaChange", 
        "artRandom", "creaMoodRatio", "creaPowerRatio", "creaGroupRatio", 
        "creaNeutralReduction", "creaRandom", "creaNCF", "logArtInit", 
        "logArtChange", "logCreaInit", "logCreaChange", "logMapInfo", 
        "logWarnings", "guiIsShown"
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
                if g["mapFile"] is None:
                    g["mapFile"] = arg
                else:
                    printHelp()
                    Log.error("Unknown argument: \"{}\"".format(arg))

    # convert args
    trueStrList = ["true"]

    g["loadMapFromBck"] = g["loadMapFromBck"] in trueStrList

    g["artChange"] = g["artChange"] in trueStrList
    g["creaChange"] = g["creaChange"] in trueStrList
    g["artRandom"] = g["artRandom"] in trueStrList
    g["creaRandom"] = g["creaRandom"] in trueStrList
    g["creaNCF"] = g["creaNCF"] in trueStrList

    g["logArtInit"] = g["logArtInit"] in trueStrList
    g["logArtChange"] = g["logArtChange"] in trueStrList
    g["logCreaInit"] = g["logCreaInit"] in trueStrList
    g["logCreaChange"] = g["logCreaChange"] in trueStrList
    g["logMapInfo"] = g["logMapInfo"] in trueStrList
    g["logWarnings"] = g["logWarnings"] in trueStrList
    g["guiIsShown"] = g["guiIsShown"] in trueStrList
    try:
        g["creaPowerRatio"] = float(g["creaPowerRatio"])
        g["creaGroupRatio"] = float(g["creaGroupRatio"])
        g["creaNeutralReduction"] = int(g["creaNeutralReduction"])
    except ValueError:
        printHelp()
        Log.error("Value error!")
    
    if g["creaChange"]:
        if g["creaPowerRatio"] <= 0.0:
            g["creaPowerRatio"] = 1.0

        # fill creaNeutralChanceList
        g["creaNeutralChanceList"] = [True]
        for i in range(g["creaNeutralReduction"]):
            g["creaNeutralChanceList"].append(False)

        # fill creaMoodList
        basicMoodList = ["MONSTER_MOOD_FRIENDLY", "MONSTER_MOOD_AGGRESSIVE", "MONSTER_MOOD_HOSTILE", "MONSTER_MOOD_WILD"]
        basicCourageList = ["MONSTER_COURAGE_ALWAYS_JOIN", "MONSTER_COURAGE_ALWAYS_FIGHT", "MONSTER_COURAGE_CAN_FLEE_JOIN"]
        g["creaMoodList"] = []

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
    
    
    # check map file
    if g["mapFile"] is None or not os.path.exists(g["mapFile"]):
        printHelp()
        Log.error("Map file does not exist: \"{}\"".format(g["mapFile"]))
    
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
    
    @classmethod
    def getAlt(pClass, pArtShared):
        altShared = pArtShared
        if pArtShared in pClass.sMapShared:
            art = pClass.sMapShared[pArtShared]
            altArt = None
            if artRandom:
                altArt = pClass.sMapId[art.mType]
            else:
                if art.mPrice > 0:
                    if art.mPrice in pClass.sGroups:
                        altArt = rand.choice(pClass.sGroups[art.mPrice])
                else:
                    if art.mType in pClass.sTypeGroups:
                        altArt = rand.choice(pClass.sTypeGroups[art.mType])
            
            if altArt is not None:
                altShared = altArt.mShared
        
        return altShared

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
    sRandList = []
    
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
        pClass.sRandList = []
        
        # files with creatures
        archFiles = [{
            "mainFile": archFile,
            "idFile": mainArchFile
        }]
        
        if creaNCF:
            # if NCF is used, then load creas from files which names starts with "NCF"
            for (dirPath, dirNames, fileNames) in os.walk(dataFolder):
                for fileName in fileNames:
                    if fileName.startswith("NCF"):
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
        
        # fill sTownList
        for townId in pClass.sMap:
            pClass.sTownList.append(townId)
        
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
    def getRandomTownId(pClass):
        townId = None
        while townId is None:
            townId = rand.choice(pClass.sTownList)
            if townId == "TOWN_NO_TYPE":
                # may reduce chance to neutrals be on map
                if rand.choice(creaNeutralChanceList) != True:
                    townId = None
        return townId
    
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
            creaCount = int(pXml.findtext("Amount", "0"))
            creaCount += int(pXml.findtext("Amount2", "0"))
            if crea is not None and creaCount > 0:
                obj.mUnits.append({"crea": crea, "count": creaCount})
            
            otherUnits = pXml.find("AdditionalStacks")
            if otherUnits is not None:
                for unit in otherUnits:
                    crea = Creature.getById(unit.findtext("Creature", ""))
                    creaCount = int(unit.findtext("Amount", "0"))
                    creaCount += int(unit.findtext("Amount2", "0"))
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
    
    @classmethod
    def getAlt(pClass, pArmy):
        # create alt army
        altArmy = Army()
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
    

class Map:
    def __init__(self, pFileName):
        self.mTree = None
        self.mFileName = pFileName
        self.mDataFileName = None
        self.mTempFolder = ".tempMapFolder6541351"
        self.mBckExt = ".bck"
    
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
                        if os.path.exists(self.mTempFolder):
                            shutil.rmtree(self.mTempFolder)
                        # extract map arch to temp folder
                        arch.extractall(self.mTempFolder)

                        # load map xml tree
                        self.mTree = ET.parse(os.path.join(self.mTempFolder, self.mDataFileName))
                        print("map loaded")
                        break
    
    def save(self):
        if (self.mTree is not None 
                and self.mFileName is not None 
                and len(self.mFileName) > 0
                and self.mDataFileName is not None 
                and os.path.exists(os.path.join(self.mTempFolder, self.mDataFileName))):
            
            # write map xml tree to temp file
            self.mTree.write(os.path.join(self.mTempFolder, self.mDataFileName), "UTF-8", True)
            
            if os.path.exists(self.mFileName) and not os.path.exists(self.mFileName + self.mBckExt):
                # backup does not exist - create it - before we change original map file
                os.rename(self.mFileName, self.mFileName + self.mBckExt)
            
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
    
    def    changeArtifacts(self):
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
                        artifactsChanged += 1
                        oldArtShared = artShared.get("href", "")
                        newArtShared = Artifact.getAlt(oldArtShared)
                        artShared.set("href", newArtShared)
                        
                        newArt = Artifact.getByShared(newArtShared)
                        if newArt.mType not in artifactsCount:
                            artifactsCount[newArt.mType] = 0
                        artifactsCount[newArt.mType] += 1
                        
                        if logArtChange:
                            print("artifact change:")
                            print("old: {}".format(oldArtShared))
                            print("new: {}\n".format(newArtShared))
        
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
                    if army is not None:
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


# main func
def run(pArgs=None):
    if pArgs is None:
        pArgs = sys.argv[1:]
    parseArgs(pArgs)
    
    if artChange or creaChange:
        Artifact.init()
        Creature.init()
        
        gameMap = Map(mapFile)
        gameMap.load()
        if artChange:
            gameMap.changeArtifacts()
        if creaChange:
            gameMap.changeCreatures()
        gameMap.save()


if __name__ == "__main__":
    # prog execution
    try:
        run()
    except MyException as ex:
        print(str(ex))
        sys.exit()

