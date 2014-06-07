import helpers
import sys
from os import walk
import operator
import os
import decimal
# testur = ["blend_itemtrain1.txt", "blend_itemtrain3.txt", "blend_systemtrain2.txt". "blend_usertrain1.txt"  blend_usertrain3.txt
# blend_itemtrain2.txt  blend_systemtrain1.txt  blend_systemtrain3.txt  blend_usertrain2.txt

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)
GENERATED_LOCATION = 'generated'
SCORE_FOLDER = 'evaluationScore'

SAVE_FOLDER = 'latexLines'
folder = ROOT_FOLDER + '/' + GENERATED_LOCATION + '/' + SAVE_FOLDER + '/'
SCORE_PATH = ROOT_FOLDER + '/' + GENERATED_LOCATION + '/' + SCORE_FOLDER + '/'

if not os.path.exists(folder):
    os.makedirs(folder)

def main():
    '''
    Generate LaTeX lines
    '''

    preLatexObj,preLatexObjCold,tops = readFromScoreFolder(SCORE_PATH)
    makeLaTeXTableColdstart(preLatexObjCold)
    makeLaTeXTable(preLatexObj,tops)

def makeLaTeXTable(preLatexObj,tops):
    '''
    input:
        01auc:0.692771753958
        02map:0.00010296994672
        03T_c:14
        04T_w:23
        05T_p:4
        06P_c:1300
        07P_w:1221
        08P_p:107
        09R_c:0.0107692307692
        10R_w:0.018837018837
        11R_p:0.0373831775701
        12MAP_c:0.000101585715343
        13MAP_w:0.00340725806452
        14MAP_p:0.00490196078431
    '''
    for rec in preLatexObj:
        for r in preLatexObj[rec]:
            print ('\\begin{table}\\centering\\resizebox{\columnwidth}{!}{\\begin{tabular}{*{19}l}\\toprule')
            print (tops + " \\\\")
            print ('\\midrule')
            for ra in preLatexObj[rec][r]:
                line = ra + "\t&\t"
                # line = ra + ","
                s_sorted = sorted(preLatexObj[rec][r][ra].items(), key=operator.itemgetter(0))
                for s in s_sorted[:(len(s_sorted)-3)]:
                    tmp = str(('%.6f' % (float(s[1]))))
                    tmp = tmp.rstrip('0').rstrip('.') if '.' in tmp else tmp
                    line += tmp + " &\t"
                    # line += tmp + ","
                line += ' \\\\'
                print (line)
            print ('\\bottomrule\\end{tabular}}\\caption{%s %s}\\end{table}'  % (r, rec))

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
    ignoreList = {'beta', 'k', 'l','16is_coverage','15us_coverage'}
    dict_sorted = sorted(dictL.items(), key=operator.itemgetter(0))
    for k in dict_sorted:
        for s in k[1]:
            if k[0] not in ignoreList:
                tmp = str(('%.6f' % (float(s))))
                tmp = tmp.rstrip('0').rstrip('.') if '.' in tmp else tmp
                line += "\t&\t" + tmp
    return line




def getRecommenderSystem(filename):
    '''
    '''
    recSysNames = getRecommenderidNames()

    for name in recSysNames:
        if name in filename:
            return recSysNames[name]

def getRecommenderidNames():
    return {
        'item_recommendation':'item recommender',
        'rating_prediction':'rank prediction',
        'mahout':'mahout',
    }

# def getRecommender(filename):
#     '''
#     Super dependent on the predictionfile name structure, not perfect
#     '''
#     recNames = {'item_recommendation', 'rating_prediction', 'mahout'}

#     tmp = filename.split('.')
#     testur = tmp[2].split('-')[-1]

#     return testur

def getColdstartNameFromFileName(filename):
    '''
    Get the coldstart name from the file name
    '''
    coldstartNames = {'blend_item', 'blend_user', 'blend_system'}
    # print (filename)
    for csn in coldstartNames:
        if csn in filename:
            return coldNameMapper(csn)
    return "normal"

def coldNameMapper(name):
    return {
        'blend_item':'item',
        'blend_user':'user',
        'blend_system':'system',
    }.get(name,name)

def readFromScoreFolder(path):
    '''
    Read from the score folder
    '''
    files = []
    for (dirpath, dirnames, filenames) in walk(path):
        files.extend(filenames)

    preColdLatexObj = {}
    preLatexObj = {}

    if len(files) == 0:
        return {},{},[]

    for f in files:
        # if isColdSplit(f):
        #     ids = getIDFromFileName(f)
        #     # scoreId,scoreName,recommender,recSys
        #     if ids[2] not in preColdLatexObj:
        #         preColdLatexObj[ids[2]] = {}
        #     if ids[1] not in preColdLatexObj[ids[2]]:
        #         preColdLatexObj[ids[2]][ids[1]] = {}
        #     preColdLatexObj[ids[2]][ids[1]][ids[0]] = readFromScoreFile(path,f)
        # else:
        ids = getIdsFromFileName(f)
        if (ids[0] != 'old format'):
            if ids[0] not in preLatexObj:
                preLatexObj[ids[0]] = {}
            if ids[2] not in preLatexObj[ids[0]]:
                preLatexObj[ids[0]][ids[2]] = {}
            if ids[1] not in preLatexObj[ids[0]][ids[2]]:
                preLatexObj[ids[0]][ids[2]][ids[1]] = {}
            preLatexObj[ids[0]][ids[2]][ids[1]] = helpers.readFromScoreFile(path,f)

    # print (preColdLatexObj)
    # sys.exit()
    tops = makeTops(helpers.readFromScoreFile(path,files[0]))
    return preLatexObj,preColdLatexObj,tops

def makeTops(s):
    ss = sorted(s.items(), key=operator.itemgetter(0))
    tops = ' & '
    for s in ss[:(len(s)-3)]:
        tops += getPretty(s[0]) + ' &\t'
    return tops

def getPretty(s):
    return {
        '01auc':'AUC',
        '02map':'MAP@20',
        '03T_c':'T\\_c',
        '04T_w':'T\\_w',
        '05T_p':'T\\_p',
        '06P_c':'P\\_c',
        '07P_w':'P\\_w',
        '08P_p':'P\\_p',
        '09R_c':'R\\_c',
        '10R_w':'R\\_w',
        '11R_p':'R\\_p',
        '12MAP_c':'MAP@20-click',
        '13MAP_w':'MAP@20-want',
        '14MAP_p':'MAP@20-purchase',
    }.get(s,s)

def getIdsFromFileName(f):
    '''
    '''
    ids = []
    fs = f.split('-')
    # check if on the freshest form
    if len(fs) == 7:
        ids.append(getRecommender(fs) + '-' + getRecommenderAlg(f))
        ids.append(getRatingFile(fs))
        ids.append(getSplit(fs))
    elif len(fs) == 6:
        ids = getIDFromFileName(f)
    else:
        ids.append("old format")
        ids.append("old format")
        ids.append("old format")
        ids.append("old format")

    # print (ids)
    return ids

def getIDFromFileName(filename):
    '''
    Get the id of the score from the filename
    '''
    ids = []
    fs = filename.split('-')
    if len(fs) == 6:
        recommender = getRecommenderAlg(filename)
        recSys = getRecommenderSystem(fs[4])
        ids.append(recSys + '-' + recommender)

        headNumber = helpers.determineLatexHeaderNumber(filename)
        coldName = getColdstartNameFromFileName(filename)
        ids.append(coldName  + '-' + str(headNumber))

        ids.append('cold')
        # ids.append(recSys)
    else:
        ids.append('old format')
        ids.append('old format')
        ids.append('old format')
    return ids

def getRecommender(fs):
    recommender = getRecommenderSystem(fs[5])
    if fs[3] != '':
        recommender += '-' + fs[3]
    return recommender

def getSplit(fs):
    return fs[4]

def getRecommenderAlg(filename):
    '''
    Super dependent on the predictionfile name structure, not perfect
    '''
    recNames = {'item_recommendation', 'rating_prediction', 'mahout'}

    tmp = filename.split('.')
    testur = tmp[-3].split('-')[-1]

    return testur

def getRatingFile(fs):
    '''
    '''
    # rfn = ratingFileNames()
    # for r in rfn:
    #     if r in f:
    #         return rfn[r]
    return ratingFileNames(fs[1])

def ratingFileNames(rf):
    return {
        'count_linear':'Count linear',
        'count_sigmoid':'Count sigmoid',
        'recentness_linear':'Recentness linear',
        'recentness_sigmoid':'Recentness sigmoid',
        'count_sigmoid':'Count sigmoid',
        'price_linear':'Price linear',
        'blend': 'Blend',
        'popularity_linear': 'Popularity Linear'
    }.get(rf,rf)

def isColdSplit(f):
    '''
    '''
    coldStarts = {'blend_systemtrain', 'blend_itemtrain', 'blend_usertrain'}
    for t in f.split('-'):
        for cs in coldStarts:
            if cs in t:
                return True
    return False




if __name__ == "__main__":
    main()
