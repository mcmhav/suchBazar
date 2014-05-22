import helpers
import sys
from os import walk
import operator
# testur = ["blend_itemtrain1.txt", "blend_itemtrain3.txt", "blend_systemtrain2.txt". "blend_usertrain1.txt"  blend_usertrain3.txt
# blend_itemtrain2.txt  blend_systemtrain1.txt  blend_systemtrain3.txt  blend_usertrain2.txt

def main():
    '''
    Generate LaTeX lines
    '''
    preLatexObj = readFromScoreFolder('../evaluation/evaluationScore/')
    makeLaTeXTable(preLatexObj)

def makeLaTeXTable(preLatexObj):
    '''
    Write the table to file in latex format
    '''


    systemScore = ""
    itemScore = ""
    userScore = ""
    for nameID in preLatexObj:
        e = open('../data/latextable' + nameID + '.tmptex','w')
        keySorted = sorted(preLatexObj[nameID].items(), key=operator.itemgetter(0))
        tmp = {}
        for key in keySorted:
            for score in key[1]:
                if score not in tmp:
                    tmp[score] = []
                tmp[score].append(preLatexObj[nameID][key[0]][score])

        line = makeLineFromDict(tmp)
        e.write(line)
        e.close()

    print ("Done, lol")

def makeLineFromDict(dictL):
    line = ''
    ignoreList = {'beta', 'k', 'l'}
    dict_sorted = sorted(dictL.items(), key=operator.itemgetter(0))
    for k in dict_sorted:
        if k[0] not in ignoreList:
            for s in k[1]:
                line += s.rstrip() + "\t&\t"
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
        scoreId,scoreName = getIDFromFileName(f)
        if scoreName not in preLatexObj:
            preLatexObj[scoreName] = {}
        preLatexObj[scoreName][scoreId] = readFromScoreFile(path,f)
    return preLatexObj

def getIDFromFileName(filename):
    '''
    Get the id of the score from the filename
    '''
    headNumber = helpers.determineLatexHeaderNumber(filename)
    coldName = getColdstartNameFromFileName(filename)
    return headNumber,coldName

def getColdstartNameFromFileName(filename):
    '''
    Get the coldstart name from the file name
    '''

    coldstartNames = {'item', 'user', 'system'}
    for csn in coldstartNames:
        if csn in filename:
            return csn

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
