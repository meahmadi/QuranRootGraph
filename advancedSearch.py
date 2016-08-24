from rootGraph import *

def findInArea(feature,value,sure,aye,word,token,surespace,ayespace,wordspace,tokenspace):
    global tokens
    #set spaces
    result = []
    for i_s in range(max(1,sure-surespace),min(len(tokens),sure+surespace)+1):
        for i_a in range(max(1,aye-ayespace),min(len(tokens[str(sure)]),aye+ayespace)+1):
            for i_w in range(max(1,word-wordspace),min(len(tokens[str(sure)][str(aye)]),word+wordspace)+1):
                for i_t in range(max(1,token-tokenspace),min(len(tokens[str(sure)][str(aye)][str(word)]),token+tokenspace)+1):
                    features = tokens[str(i_s)][str(i_a)][str(i_w)][str(i_t)]
                    if feature in features and features[feature] == value:
                        result.append((i_s,i_a,i_w,i_t))
    return result
def findAdvance2(feature1,value1,feature2,value2,surespace,ayespace,wordspace,tokenspace):
    global tokens
    result = []
    for sure in tokens:
        for aye in tokens[sure]:
            for word in tokens[sure][aye]:
                for token in tokens[sure][aye][word]:
                    features = tokens[sure][aye][word][token]
                    if feature1 in features and features[feature1] == value1:
                        r = findInArea(feature2,value2,int(sure),int(aye),int(word),int(token),surespace,ayespace,wordspace,tokenspace)
                        if len(r)>0:
                            result.append((sure,aye,word,token,r))
    return result

def anotherFindAdvance2(feature1,value1,feature2,value2,surespace,ayespace,wordspace,tokenspace):
    global tokens
    result1 = []
    result2 = []
    for sure in tokens:
        for aye in tokens[sure]:
            for word in tokens[sure][aye]:
                for token in tokens[sure][aye][word]:
                    features = tokens[sure][aye][word][token]
                    if feature1 in features and features[feature1] == value1:
                        result1.append(10*1000*1000*int(sure)+10*1000*int(aye)+10*int(word)+int(token))
                    if feature2 in features and features[feature2] == value2:
                        result2.append(10*1000*1000*int(sure)+10*1000*int(aye)+10*int(word)+int(token))
    result = []
    for t1 in result1:
        for t2 in result2:
            if abs(t2-t1) < surespace*10*1000*1000+ayespace*10*1000+wordspace*10+tokenspace:
                result.append((t1,getFeatures(t1)["form"],t2,getFeatures(t2)["form"]))
    return result

def anotherFindAdvanceN(featureValues,spaces):
    global tokens
    results = [[] for x in featureValues]
    for sure in tokens:
        for aye in tokens[sure]:
            for word in tokens[sure][aye]:
                for token in tokens[sure][aye][word]:
                    features = tokens[sure][aye][word][token]
                    i = 0
                    for f,v in featureValues:
                        if f in features and features[f] = v:
                            results[i].append()
                        i = i + 1
                    if feature1 in features and features[feature1] == value1:
                        result1.append(fromAddress(sure,aye,word,token))
    preresult = [[] for x in len(featureValues)]
    for i in range(len(featureValues)):
        for j in range(i+1,len(featureValues)):
            for t1 in results[i]:
                for t2 in results[j]:
                    if abs(t2-t1) < surespace*10*1000*1000+ayespace*10*1000+wordspace*10+tokenspace:
                        preresult[i].append((t1,getFeatures(t1)["form"],t2,getFeatures(t2)["form"]))
    return preresult

if __name__ == '__main__':
    import os.path


    metadata = parseQuranMetadata("quran-data.js")

    corpusfile = "corpus.json"
    if os.path.exists(corpusfile):
        tokens = loadFrom(corpusfile)
    else:
        tokens = parseQuranTokens("quranic-corpus-morphology-0.4.txt")
        saveTo(tokens,corpusfile)

    rootfile = "roots.json"
    if os.path.exists(rootfile):
        roots = loadFrom(rootfile)
    else:
        roots = getRootAyat(tokens)
        saveTo(roots,rootfile)

    quran_text = loadQuranText("quran-simple.txt")

    r = anotherFindAdvance2("LEM","Hakiym","ROOT","byn",0,2,1000,1000)
    r1 = ["%s \n %s\n-------"%(getAyeText(x[0]),getAyeText(x[2])) for x in r if x[3] not in ["bayona","bayoni"] ]
    print(len(r1))
    print(u"\n\n".join(r1))
