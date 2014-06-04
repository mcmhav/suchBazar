import helpers
import sys
from os import walk
import operator
import os
# testur = ["blend_itemtrain1.txt", "blend_itemtrain3.txt", "blend_systemtrain2.txt". "blend_usertrain1.txt"  blend_usertrain3.txt
# blend_itemtrain2.txt  blend_systemtrain1.txt  blend_systemtrain3.txt  blend_usertrain2.txt

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)
GENERATED_LOCATION = 'generated'
SAVE_FOLDER = 'latexLines'
SCORE_FOLDER = 'evaluationScore'
folder = ROOT_FOLDER + '/' + GENERATED_LOCATION + '/' + SAVE_FOLDER + '/'
SCORE_PATH = ROOT_FOLDER + '/' + GENERATED_LOCATION + '/' + SCORE_FOLDER + '/'

if not os.path.exists(folder):
    os.makedirs(folder)

def main():
    '''
    Generate LaTeX lines
    '''

    preLatexObj = readFromScoreFolder(SCORE_PATH)
    makeLaTeXTableColdstart(preLatexObj)
    # makeLaTeXTable(preLatexObj)

def makeLaTeXTable(preLatexObj):
    '''
    '''

    for rec in preLatexObj:
        for mode in preLatexObj[rec]:
            for split in preLatexObj[rec][mode]:
                tmp = {}
                tmp[split] = [preLatexObj[rec][mode][split]]
                # print (preLatexObj[rec][mode][split])
                print (tmp)
                sys.exit()

def makeLaTeXTableColdstart(preLatexObj):
    '''
    Write the table to file in latex format
    '''

    systemScore = ""
    itemScore = ""
    userScore = ""
    for nameID in preLatexObj:
        keySorted = sorted(preLatexObj[nameID].items(), key=operator.itemgetter(0))
        for key in keySorted:
            mode = key[0]
            e = open(folder + 'latextable' + nameID + '.tmptex','w')
            tmp = {}
            split_sorted = sorted(key[1].items(), key=operator.itemgetter(0))
            for split in split_sorted:
                for score in split[1]:
                    if score not in tmp:
                        tmp[score] = []
                    tmp[score].append(split[1][score])
            idString = ("NameID: %s\t mode: %s" % (nameID,mode))
            line = makeLineFromDict(tmp)
            # print (idString)
            print (idString + line + " \\\\")
            e.write(line)
            e.close()

    print ("Done generating latex lines")

def makeLineFromDict(dictL):
    line = ''
    ignoreList = {'beta', 'k', 'l'}
    dict_sorted = sorted(dictL.items(), key=operator.itemgetter(0))
    for k in dict_sorted:
        for s in k[1]:
            if k[0] not in ignoreList:
                line += "\t&\t" + ('%.4f' % (float(s.rstrip())))
    return line

def readFromScoreFolder(path):
    '''
    Read from the score folder
    '''
    files = []
    for (dirpath, dirnames, filenames) in walk(path):
        files.extend(filenames)

    preLatexObj = {}
    for f in files:
        scoreId,scoreName,recommender,recSys = getIDFromFileName(f)

        if recommender not in preLatexObj:
            preLatexObj[recommender] = {}
        if scoreName not in preLatexObj[recommender]:
            preLatexObj[recommender][scoreName] = {}
        preLatexObj[recommender][scoreName][scoreId] = readFromScoreFile(path,f)
    return preLatexObj


def getIDFromFileName(filename):
    '''
    Get the id of the score from the filename
    '''
    headNumber = helpers.determineLatexHeaderNumber(filename)
    coldName = getColdstartNameFromFileName(filename)
    recommender = getRecommender(filename)
    recSys = getRecommenderSystem(filename)

    return headNumber,coldName,recommender,recSys

def getRecommenderSystem(filename):
    '''
    '''
    recSysNames = {'item', 'rank', 'mahout'}

    for name in recSysNames:
        if name in recSysNames:
            return name



def getRecommender(filename):
    '''
    Super dependent on the predictionfile name structure, not perfect
    '''
    recNames = {'item', 'rank', 'mahout'}

    tmp = filename.split('.')
    testur = tmp[2].split('-')[-1]

    return testur

def getColdstartNameFromFileName(filename):
    '''
    Get the coldstart name from the file name
    '''

    coldstartNames = {'item', 'user', 'system'}
    for csn in coldstartNames:
        if csn in filename:
            return csn
    return "normal"

def readFromScoreFile(path,filename):
    '''
    Reads from the scorefile to get the scores based on the predictions
    '''
    scores = {}
    f = open(path + filename, 'r+')
    lines = f.readlines()
    f.close()
    for line in lines:
        tmp = line.split(':')
        scores[tmp[0]] = tmp[1]
    return scores

if __name__ == "__main__":
    main()
