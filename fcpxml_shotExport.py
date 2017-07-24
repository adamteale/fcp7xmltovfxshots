#!/usr/bin/env python
# encoding: utf-8
"""
Created by ateale on 2012-05-08-1210.
Copyright (c) 2012 adamteale. All rights reserved.

run in terminal:
python fcpNuke.py xmlfile.xml jobname destinationDir

# what xml file to parse
xmlfile = str(sys.argv[1])

# name of job/project
jobname = sys.argv[2]

# where to save nuke scripts
destinationDir = sys.argv[3]


"""

import sys
import os
import re
import string
from xml.etree.ElementTree import ElementTree
import shutil



def gatherClipsFromXML(xml):
    # parse file with ElmentTree
    lDocument = ElementTree()
    lDocument.parse(xml)
    lRoot = lDocument.getroot()
    
    allClipsArray = []

    # go through xml doc and gather clipitems and write out nuke scripts for each clip
    for sequence in lRoot.getchildren():
        if sequence.tag == 'sequence':
        
            # # sequence name
            # nkscriptidname = sequence.get('id')
            # print "nkscriptidname: " + nkscriptidname
        
            # 
            for child in sequence.getchildren():
                # print all child nodes of sequence
                # print child.tag
            
                if child.tag == 'media':
                    for a in child.getchildren():
                        if a.tag == 'video':
                            aChildNodes = a.getchildren()
                            for b in aChildNodes:                
                                if b.tag == 'track':
                                
                                    trackNumber = aChildNodes.index(b)
                                
                                    # get all clip items and find their info
                                    for c in b.getchildren():
                                    
                                        # create a dictionary for each clip item to store info for later use
                                        clipDictionary = {}
                                    
                                        # clip's track number in fcp
                                        clipDictionary['track_num'] = trackNumber
                                        if c.tag == 'clipitem':
                                            for d in c.getchildren():
                                                if d.tag == 'start':
                                                    fcp_start = d.text
                                                    clipDictionary['fcp_start'] = d.text
                                                    # print "fcp in: " + fcp_start
                                                if d.tag == 'end':
                                                    fcp_end = d.text
                                                    clipDictionary['fcp_end'] = d.text
                                                    # print "fcp out: " + fcp_end
                                            # file info
                                            # clipDictionary['node_fileinfo'] = c.find("file")
                                        
                                            # shot number - add 1 so numbers start from 1
                                            clipDictionary['nkscriptid'] = str('%02d' % (b.getchildren().index(c)+1))
                                            clipDictionary['nkscript_shotname'] = "name"
                                            clipDictionary['nukeScriptPath'] = 'path'                                        
                                            clipDictionary['nukeRoot_first_frame'] = 0
                                            clipDictionary['nukeRoot_last_frame'] = 0                                        
                                            clipDictionary['nukeRoot_fps'] = 0        
                                            clipDictionary['nukeReadOrigFile'] = "filepath"                                        
                                            clipDictionary['in'] = 0                                
                                            clipDictionary['out'] = 0
                                            clipDictionary['duration'] = 0
                                                                                    
                                            rtval = 0
                                            variablespeed = 0
                                        
                                            for d in c.getchildren():
                                                # get start & end to define what section of the file is used
                                                if d.tag == "name":
                                                    clipDictionary['nkscript_shotname'] = d.text

                                                if d.tag == "in":
                                                    clipDictionary['in'] = d.text
                                                if d.tag == "out":
                                                    clipDictionary['out'] = d.text
                                                if d.tag == "start":
                                                    clipDictionary['start'] = d.text
                                                if d.tag == "end":
                                                    clipDictionary['end'] = d.text                                                
                        
                                                # get clipitem details
                                                if d.tag == 'file':
                                                    for v in d.getchildren():
                                                        if v.tag == "pathurl":
                                                            fileurl = v.text.replace("file://localhost","")
                                                            fileurl = fileurl.replace("%20","\ ")
                                                            # print "fileurl:::: " + fileurl
                                                        
                                                            clipDictionary['nukeReadOrigFile'] = fileurl
                                                        
                                                        if v.tag == "rate":
                                                            for q in v.getchildren():
                                                                if q.tag == 'timebase':
                                                                    clipDictionary['nukeRoot_fps'] = q.text

                                                        if v.tag == "duration":
                                                            clipDictionary['duration'] = v.text
                                                            print "duration: " + str(clipDictionary['duration'])
                                                            
                                        
                                            # array to store timeremap info for use in timewarp node in nuke
                                            timeRemapInfo = []
                                            reverseString = "FALSE"
                                            # filter info
                                            node_filters = c.findall("filter")
                                            # for filt in node_filters:
                                            #
                                            #     for elem in filt.iterfind('effect'):
                                            #                                                     # if elem.find("name").text == "Time Remap":
                                            #             for w in elem.iterfind("parameter"):
                                            #                 if w.find("name").text:
                                            #                     # print w.find("name").text
                                            #                     if w.find("name").text == "variablespeed":
                                            #                         # print "variable speed bool: " + w.find("value").text
                                            #                         variablespeed = bool(w.find("value").text)
                                            #                         clipDictionary['variablespeed'] = w.text
                                            #                     if w.find("name").text == "reverse":
                                            #                         # print "reverse bool: " + w.find("value").text
                                            #                         reverseString = w.find("value").text
                                            #                         clipDictionary['reverse'] = w.text
                                            #                     if w.find("name").text == "graphdict":
                                            #                         # print w.find("valuemin").text
                                            #                         # print w.find("valuemax").text
                                            #                         # print "rtval: " + w.find("value").text
                                            #                         rtval = w.find("value").text
                                            #
                                            #                     keyframes = w.findall("keyframe")
                                            #                     for keyframe in keyframes:
                                            #                         entry = []
                                            #                         when = "x" + keyframe.find("when").text
                                            #                         value = keyframe.find("value").text
                                            #                         entry.append(when)
                                            #                         entry.append(value)
                                            #                         timeRemapInfo.append(entry)
                                            #                         # print "when: " + when
                                            #                         # print "value: " + value
                                            #                     if len(timeRemapInfo) > 0:
                                            #                         if variablespeed == 1:
                                            #                             keyframeFirst = timeRemapInfo[1]
                                            #                             keyframeLast = timeRemapInfo[-2]
                                            #                             # print "keyframeFirst: " + keyframeFirst[0].replace("x","")
                                            #                             # print "keyframeLast: " + keyframeLast[0].replace("x","")
                                            #
                                            #                             clipDictionary['in'] = float(keyframeFirst[0].replace("x",""))
                                            #                             clipDictionary['out'] = float(keyframeLast[0].replace("x",""))
                                            #
                                            #                     # for y in w.iterfind("name"):
                                            #                     #     if y.find("value").text == "Time Remap":
                                            #                     #     rtval = w.iterfind("name").text
                                            #                     #     print "rtval: " + rtval
                                            #
                                            # #string to build remap for nuke timewarp node
                                            # remapString = ""
                                            # for keyframeEntry in timeRemapInfo:
                                            #     x = str(keyframeEntry[0])
                                            #     y = str(keyframeEntry[1])
                                            #     remapString = remapString + x + " " + y + " "
                                            # clipDictionary['remapString'] = remapString
                                            
                                            # add to allClipsArray
                                            allClipsArray.append(clipDictionary)
    return allClipsArray



def spitOutShots(clipsArray, shotNumberInt):
    
    def makeShotDir(sourceFile, destinationDir, shotNumberInt):
        print "-----------------------makeShotDir"
        sourceFile = sourceFile.replace("file://", "")
        sourceFile = sourceFile.replace("\ ", " ")
        destinationDir = destinationDir.replace("\ ", " ")

        shotdir = os.path.join(destinationDir, str(shotNumberInt ))
        filename = os.path.basename(sourceFile)
        if os.path.isdir(shotdir):
            pass
        else:
            print "making dir: " + shotdir
            os.makedirs(shotdir)
        
        try:
            shutil.move(sourceFile, os.path.join(shotdir, filename))
        except:
            print "file not there {}".format(sourceFile)

        print destinationDir
        print shotNumberInt
    
    def makeReadNodeText(clip):
        return """
Read {
inputs 0
file """+clip['nukeReadOrigFile']+"""
format "1280 720 0 0 1280 720 1 "
last """+str(clip['duration'])+"""
origlast """+str(clip['duration'])+"""
origset true
label "from Track """ + str(clip['track_num']) + """ in FCP"
}
TimeOffset {
 time_offset """ + str(int(clip['start']) - int(clip['in'])) + """
}"""

    shotNumberInt = str('%02d' % shotNumberInt)
    readNodeString = ""


    for clip in clipsArray:
        # print "-------------------------------------------"
        # print str(shotNumberInt) + " " +  clip["nkscript_shotname"]
        # print clip["in"]
        # print clip["out"]
        print clip['duration']
        readNodeString = readNodeString + makeReadNodeText(clip)

        makeShotDir(clip['nukeReadOrigFile'], destinationDir, shotNumberInt)
        

#     # create shot directory if it doesn't already exist
#     if os.path.isdir(destinationDir + "/" + str( shotNumberInt ) ):
#         pass
#     else:
#         print "making dir: " + destinationDir + "/" + str(shotNumberInt)
#         os.makedirs(destinationDir + "/" + str(shotNumberInt ))
#
#     # create scripts directory if it doesn't already exist
#     if os.path.isdir(destinationDir + "/" + str(shotNumberInt) + "/scripts" ):
#         pass
#     else:
#         print "making dir: " + destinationDir + "/" + str(shotNumberInt ) + "/scripts"
#         os.makedirs(destinationDir + "/" + str(shotNumberInt) + "/scripts")
#         os.makedirs(destinationDir + "/" + str(shotNumberInt ) + "/renders")
#
#     num = 1
#     version = str('%03d' % num)
#     nukeScriptPath = destinationDir + "/" + str(shotNumberInt ) + "/scripts" + "/" + jobname + "_" + str(shotNumberInt)  + "_" + clipsArray[0]['nkscript_shotname']  + "_v" + str(version) + ".nk"
#     # while(os.path.isfile(nukeScriptPath)==1):
#     #     print "exists..."
#     #     num = num + 1
#     #     version = str('%03d' % num)
#     #     nukeScriptPath = destinationDir + "/" + str(nkscriptid) + "/scripts" + "/" + jobname + "_" + str(nkscriptid)  + "_comp_" + nkscript_shotname + "_v" + str(version) + ".nk"
#     if(os.path.isfile(nukeScriptPath)==1):
#         print "exists..."
#     else:
#         version = str('%03d' % 1)
#         nukeScriptPath = destinationDir + "/" + str(shotNumberInt ) + "/scripts" + "/" + jobname + "_" + str(shotNumberInt)  + "_" + clipsArray[0]['nkscript_shotname']  + "_v" + str(version) + ".nk"
#         print "nukeScriptPath: " + nukeScriptPath
#
#
#     # barebones nuke script to fill-in
#     nukeScript = """Root {
# inputs 0
# name """ + clipsArray[0]['nukeScriptPath'].replace(" ","\ ") + """
# first_frame """ + str(clipsArray[0]['start']) + """
# last_frame """ + str(clipsArray[0]['end']) + """
# lock_range true
# fps """ + str(clipsArray[0]['nukeRoot_fps']) + """
# format "2048 1556 0 0 2048 1556 1 2K_Super_35(full-ap)"
# proxy_type scale
# proxy_format "1024 778 0 0 1024 778 1 1K_Super_35(full-ap)"
# }
# """ + readNodeString
#
#     # Write out nuke script
#     fo = open(nukeScriptPath, "wb")
#     fo.write(nukeScript)
#     fo.close()

    


###############################
#START HERE

# what xml file to parse
xmlfile = str(sys.argv[1])

# name of job/project
jobname = sys.argv[2]

# where to save nuke scripts
destinationDir = sys.argv[3]

allClipsArray = gatherClipsFromXML(xmlfile)

# find missing file pathurls and replace (usually caused from same clip used multiple times in a fcp sequence)
# eventually replace this and use the fcp xml's "link" property
for b in allClipsArray:
    if b['nukeReadOrigFile'] == "filepath":
        for a in allClipsArray:
            if a['nkscript_shotname'] == b['nkscript_shotname'] and a['nkscript_shotname']!="filepath" :
                b["nukeReadOrigFile"] = a["nukeReadOrigFile"]
                b['duration'] = a['duration']
                break


# sort array based on each clip's fcp_start key - will help with sorting of shotNumbers further down the script
allClipsArray = sorted(allClipsArray, key=lambda k: int(k['fcp_start'])) 
# for a in allClipsArray:
#     print a['fcp_start']

usedClips = []

# Match up layers to "shots" in order
# -
# For each clipItem in the allClipsArray compare it against each usedClip in the usedClipsArray.
# if the inPoint of the clipItem is greater than or equal to the inPoint of the usedItem, and the inPoint of the clipItem 
# is less than the outpoint of the usedItem then it must be in teh same "shot" time range.
# -
# if the clipItem doesn't exist in the usedItems array, set it's "shotNumber" to be it's index in the allClipsArray (but i think this is wrong - could be out based on the gaps in the timeline and clips in above tracks)


for clip in allClipsArray:
    # must have at least 1 item for this to work - so add first one

    # print "looking for match ************************************************************************************"
    # print clip['nkscript_shotname'] + " track:" +  str(clip['track_num']) + " frameIn:" + clip['fcp_start'] + " frameOut:" + clip['fcp_end']
    # print
    
    # for each "used clip" in usedClips, compare the "clip" against a used clip.
    # if it matches the timing requires, set it's shotNumber to the shot number of the used Clips
    count = 0
    print "*************************************************"
    for uc in usedClips:

        # print  uc['nkscript_shotname'] + " track:" +  str(uc['track_num']) + " frameIn:" + uc['fcp_start'] + " frameOut:" + uc['fcp_end']
        if int(clip['fcp_start']) >= int(uc['fcp_start']) and int(clip['fcp_start']) < int(uc['fcp_end']) :
            # possible match
            # assign clip
            print "Possible Match!"
            if uc.has_key("shotNumber"):
                print "a" + str(uc["shotNumber"])
                clip["shotNumber"] = uc["shotNumber"]
            else:
                print "b"
                clip["shotNumber"] = usedClips.index(uc)
            
            print "shot number: " + str(clip["shotNumber"])
            print allClipsArray.index(clip)
            print clip['fcp_start'] + " " + str(clip['fcp_end'])
            print uc['fcp_start'] + " " + str(uc['fcp_end'])
            print "object " + clip['nkscript_shotname'] + " in track: " + str(clip['track_num']) + " matched to clip " + uc['nkscript_shotname']  + " in track " + str(uc['track_num']) 
            break
        count = count + 1    
    
    if count == len(usedClips):
        if clip not in usedClips:
            usedClips.append(clip)
        clip["shotNumber"] =  usedClips.index(clip)
        # print "SHOT NUMBER: "  + str(clip["shotNumber"])
        # print "framestart: "  + str(clip["fcp_start"])

counter = 1
for shot in usedClips:
    print shot['shotNumber']
    clipsForShotArray = []
    for clip in allClipsArray:
        if clip['shotNumber'] == shot['shotNumber']:
            # print "shotNumber " + str(usedClips.index(shot) + 1) + " " + str(clip["shotNumber"]) + ' ' + clip['fcp_start']
            clipsForShotArray.append(clip)
    print "###############"
    print "SHOT NUMBER " + str(usedClips.index(shot)+1)
    for a in clipsForShotArray:
        print a['shotNumber']
    # make nuke scripts
    spitOutShots(clipsForShotArray, usedClips.index(shot) + 1)
    
