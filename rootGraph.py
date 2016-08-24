def parseQuranMetadata(resourceFile):
    global metadata
    import json
    with open(resourceFile) as f:
        metadata = json.loads(f.read())
    return metadata

def loadQuranText(textfile):
    text = {}
    with open(textfile) as file:
        for line in file:
            ts = line.split("|")
            if ts[0] not in text:
                text[ts[0]] = {}
            text[ts[0]][ts[1]] = ts[2]
    return text

def isHamSiaqInList(metadata,a1,al):
    x1,y1 = int(int(a1)/1000), int(a1)%1000
    for a2 in al:
        x2,y2 = int(int(a2)/1000), int(a2)%1000
        if x1 is not x2: continue
        if y1 is y2: return True
        y1,y2 = min(y1,y2), max(y1,y2)
        check = False
        for k  in metadata["Ruku"]:
            if len(k) is not 2:
                continue
            x,y = k
            if check:
                if y is y2:
                    return True
                break
            if x1 is x and y is y1:
                check = True
    return False



def parseQuranTokens(corpusFile):
    global metadata
    tokens = {}
    rnumber = 0
    with open(corpusFile) as file:
        for line in file:
            address, form, pos, feature = line.split("\t")
            features = dict([(a+":").split(":")[:2] for a in feature.strip().split("|")])
            # if "ROOT" in features and features["ROOT"] in ["kwn","qwl","Alh"]:
            #     del features["ROOT"]
            features["form"] = form
            features["pos"] = pos
            sure,aye,kalame,token = [int(x) for x in address.strip()[1:-1].split(":")]
            #if len(metadata["Ruku"])>rnumber and sure == int(metadata["Ruku"][rnumber +1][0]) and aye == int(metadata["Ruku"][rnumber+1][1]):
            #    rnumber = rnumber + 1
            features["ruku"] = rnumber
            if sure not in tokens: tokens[sure] = {}
            if aye not in tokens[sure]: tokens[sure][aye] = {}
            if kalame not in tokens[sure][aye]: tokens[sure][aye][kalame] = {}
            if token not in tokens[sure][aye][kalame]: tokens[sure][aye][kalame][token] = features
    return tokens

def getLemAyat(tokens):
    lems = {}
    roots = {}
    for sure in tokens.keys():
        for aye in tokens[sure].keys():
            for kalame in tokens[sure][aye].keys():
                for token in tokens[sure][aye][kalame].keys():
                    if "LEM" in tokens[sure][aye][kalame][token]:
                        lem = tokens[sure][aye][kalame][token]["LEM"]
                        if lem not in lems:
                            lems[lem] = []
                        lems[lem].append(int(aye)+ int(sure)*1000)
                        if "ROOT" in tokens[sure][aye][kalame][token]:
                            root = tokens[sure][aye][kalame][token]["ROOT"]
                            if lem not in roots:
                                roots[lem] = root

    return {"lems":lems,"roots":roots}

def getLemGraph(lems):
    import math
    graph = {}
    for a in lems["lems"]:
        graph[a] = {}
        for b in lems["lems"]:
            if a is b:
                graph[a][b] = 1
            elif a in lems["roots"] and b in lems["roots"] and lems["roots"][a] == lems["roots"][b]:
                graph[a][b] = 1
            elif b in graph:
                if a in graph[b]:
                    graph[a][b] = graph[b][a]
            else:
                tm = [x for x in lems["lems"][a] if x in lems["lems"][b]]
                if len(tm)>0:
                    graph[a][b] = len(tm) / (len(lems["lems"][a])*len(lems["lems"][b]))#math.sqrt(len(lems["lems"][a])*len(lems["lems"][b]))
    return graph

def getLemSiaqGraph(lems,metadata):
    import math
    graph = {}
    for a in lems["lems"]:
        graph[a] = {}
        for b in lems["lems"]:
            if a is b:
                graph[a][b] = 1
            elif a in lems["roots"] and b in lems["roots"] and lems["roots"][a] == lems["roots"][b]:
                graph[a][b] = 1
            elif b in graph:
                if a in graph[b]:
                    graph[a][b] = graph[b][a]
            else:
                tm = [x for x in lems["lems"][a] if isHamSiaqInList(metadata,x,lems["lems"][b])]
                if len(tm)>0:
                    graph[a][b] = len(tm) / (len(lems["lems"][a])*len(lems["lems"][b]))#math.sqrt(len(lems["lems"][a])*len(lems["lems"][b]))
    return graph



def getRootAyat(tokens):
    global roots
    roots = {}
    for sure in tokens.keys():
        for aye in tokens[sure].keys():
            for kalame in tokens[sure][aye].keys():
                for token in tokens[sure][aye][kalame].keys():
                    if "ROOT" in tokens[sure][aye][kalame][token]:
                        root = tokens[sure][aye][kalame][token]["ROOT"]
                        if root not in roots:
                            roots[root] = []
                        roots[root].append(int(aye) + int(sure)*1000)#token + (kalame + (aye + sure*1000)*1000)*10)
    return roots

def getRootGraph(roots):
    import math
    graph = {}
    for a in roots:
        graph[a] = {}
        for b in roots:
            if a is b:
                graph[a][b] = 1
            elif b in graph:
                if a in graph[b]:
                    graph[a][b] = graph[b][a]
            else:
                tm = [x for x in roots[a] if x in roots[b]]
                if len(tm)>0:
                    graph[a][b] = len(tm) / math.sqrt(len(roots[a])*len(roots[b]))
    return graph

def rootWeightInSure(root, sure):
    global rootWeights,roots
    import math

    # print(sure,root,len(rootWeights),end=" :")
    if root in rootWeights:
        # print("+",end="")
        # print(rootWeights[root],"-",end="")
        if sure in rootWeights[root]:
            # print(rootWeights[root][sure])
            return rootWeights[root][sure]
        # else:
            # print("#",end="")
    else:
        # print("!",end="")
        rootWeights[root] = {}
    d = 0.0

    # print("?",end="")

    for aye in roots[root]:
        # print(aye,int(sure),math.floor(int(aye)/1000),end=";")
        if math.floor(int(aye)/1000) == int(sure):
            d = d + 1
    # print(".",d,end="")
    rootWeights[root][sure] = math.pow(d / len(roots[root]),1)
    # print(rootWeights[root][sure])
    return rootWeights[root][sure]


def ayeSimilarity(feature,graph,a,b,sure=None):
    global rootWeights,roots
    import math

    d = 0
    for wordA in a.keys():
        for tokenA in a[wordA].keys():
            for wordB in b.keys():
                for tokenB in b[wordB].keys():
                    if feature in a[wordA][tokenA] and feature in b[wordB][tokenB]:
                        try:
                            #d += 1 if a[wordA][tokenA][feature] == b[wordB][tokenB][feature] else 0
                            z = 1
                            if sure is not None:
                                # print(a[wordA][tokenA][feature],b[wordB][tokenB][feature])
                                x1 = rootWeightInSure(a[wordA][tokenA][feature],sure)
                                # print (x1)
                                x2 = rootWeightInSure(b[wordB][tokenB][feature],sure)
                                # print (x2)
                                z = x1 * x2
                            d = d + graph[ a[wordA][tokenA][feature] ][ b[wordB][tokenB][feature] ] #* z
                        except:
                            pass
    d = d / math.sqrt(len(a)*len(b))

    return d

def siaqSimilarity(feature,graph,s1,s11,s12,s2,s21,s22):
     d = 0
     c = 0
     for ayeA in s1:
         if int(ayeA) < s11 or int(ayeA) >  s12:
             continue
         for ayeB in s2:
             if int(ayeB) <s21 or int(ayeB) > s22:
                 continue
             #d = d + ayeSimilarity(feature,graph,s1[ayeA],s2[ayeB])
             for wordA in s1[ayeA].keys():
                 for tokenA in s1[ayeA][wordA].keys():
                     for wordB in s2[ayeB].keys():
                         for tokenB in s2[ayeB][wordB].keys():
                             c = 0
                             if feature in s1[ayeA][wordA][tokenA] and feature in s2[ayeB][wordB][tokenB]:
                                 try:
                                     d = d + graph[ s1[ayeA][wordA][tokenA][feature] ][ s2[ayeB][wordB][tokenB][feature] ]
                                 except:
                                     pass
     d = d / math.sqrt(c)

     return d

def center(graph):
    INF = 100000000

    d = {}
    for n1 in graph:
        d[n1] = {}
        for n2 in graph:
            if n1 == n2:
                d[n1][n2] = 0
            else:
                d[n1][n2] = graph[n1][n2]
                #if graph[n1][n2] == 0:
                #    d[n1][n2] = INF
    #print ("D", d)
    for k in graph:
        for v in graph:
            for u in graph:
                d[v][u] = min(d[v][u], d[v][k] + d[k][u])
    #
    #print("D", d)
    dsum_list = []
    dmax_list = []
    dsum = {}
    dmax = {}
    for n in graph:
        dsum[n] = 0
        dmax[n] = 0
        for v in graph:
            dsum[n] += d[n][v]
            dmax[n] = max(dmax[n], d[n][v])

        dsum_list.append((n, dsum[n]))
        dmax_list.append((n, dmax[n]))
    dsum_list = sorted(dsum_list, key=lambda x: x[1])
    dmax_list = sorted(dmax_list, key=lambda x: x[1])
    return dsum_list, dmax_list

def cmp_root(cmp, v):
    if (cmp[v] == v):
        return v
    u = cmp_root(cmp, cmp[v])
    return cmp[v] == u

def MST2(graph):
    E = []
    cmp = {}
    for n in graph:
        cmp[n] = n
        for m in graph:
            if n != m:
                E.append((n, m, graph[n, m]))
    E = sorted(E, key=lambda x: x[2])
    addedE = 0
    firstE = 0
    G = []
    while addedE < len(graph):
        if cmp_root(E[firstE][0]) != cmp_root(E[firstE][1]):
            G.append(E[first])
            addedE += 1
            cmp[cmp_root(E[firstE][0])] = cmp_root(E[firstE][1])
    return G


def MST(graph):
    # print(graph)
    INF = -10000000000
    d = {}
    mark = {}
    p = {}
    for n in graph:
        d[n] = INF
        mark[n] = False
        p[n] = None

    first = '12'#list(graph.keys())[0]
    d[ first ] = 0

    while True:
        min_d = INF
        min_v = None
        for n in graph:
            if mark[n] == False and min_d < d[n]:
                min_d = d[n]
                min_v = n
        if min_v == None:
            break
        mark[min_v] = True
        for n in graph:
            # print (min_v , n)
            # print (graph[min_v])
            # print (graph[min_v][n])
            # print (d[n])
            if mark[n] == False and graph[min_v][n] > d[n]:
                p[n] = min_v
                d[n] = graph[min_v][n]

    return p
    #for n in graph:
    #    if p[n] != -1:

def betweenness(graph):
    INF = 100000000

    d = {}
    for n1 in graph:
        d[n1] = {}
        for n2 in graph:
            if n1 == n2:
                d[n1][n2] = 0
            else:
                d[n1][n2] = graph[n1][n2]
                #if graph[n1][n2] == 0:
                #    d[n1][n2] = INF
    #print ("D", d)
    for k in graph:
        for v in graph:
            for u in graph:
                d[v][u] = min(d[v][u], d[v][k] + d[k][u])

    b = {}
    for k in graph:
        b[k] = 0
        for v in graph:
            for u in graph:
                if d[v][u] == d[v][k] + d[k][u]:
                    b[k] += 1

    return b




def sureSelfSimilarity(feature, graph, metadata, tokens, sure):
    r = {}
    s = tokens[sure]
    ayat = list(s.keys())
    ayat.sort()
    sureGraph = {}
    for ayeA in ayat:
        r[ayeA] = 0
        sureGraph[ayeA] = {}
        for ayeB in ayat:
            if ayeA is not ayeB:
                ts = ayeSimilarity(feature,graph,s[ayeA],s[ayeB],sure)
                sureGraph[ayeA][ayeB] = ts
                if ts > 0:
                    r[ayeA] = r[ayeA] + ts
    sortedAyat = sorted(r, key=r.get)[::-1]
    print("ayat %s:"%sure,sortedAyat)
    saveGraphToGDF(sureGraph,"%s-ayat.gdf"%sure)

    mst = MST(sureGraph)
    nei = {}
    INF = 1000000000
    treeGraph = {}
    for n in sureGraph:
        treeGraph[n] = {}
        for m in sureGraph:
            treeGraph[n][m] = INF

    for n in sureGraph:
        nei[n] = [n]
    for a, b in mst.items():
        if b == None: continue
        nei[a].append(b)
        nei[b].append(a)
        treeGraph[a][b] = treeGraph[b][a] = 1


    nei = sorted(nei.values(), key=lambda x: len(x))

    print("NEI:")
    for n in nei:
        print(n)
    #for a, b in nei:
    #    print (a,b)


    print("CENTER:")
    #c, c2 = center(treeGraph)
    # print("C1", c)
    # print("C2", c2)

    #b = betweenness(treeGraph)
    # print ("B", b)

    for a in sureGraph:
        for b in sureGraph:
            if treeGraph[a][b] != INF:
                treeGraph[a][b] = sureGraph[a][b]
            else:
                del treeGraph[a][b]
    saveGraphToGDF(treeGraph,"%s-ayeTree.gdf"%sure)



    # siaqs = sorted([s[1] for s in metadata["Ruku"] if len(s)>0 and s[0] is int(sure)])
    # siaqs.append(len(s))
    #
    # sq = {}
    # for i1 in range(len(siaqs)-1):
    #     s11 = siaqs[i1]
    #     s12 = siaqs[i1+1]-1
    #     sq[(s11,s12)] = 0
    #     for i2 in range(len(siaqs)-1):
    #         if i2 is i1:
    #             continue
    #         s21 = siaqs[i2]
    #         s22 = siaqs[i2+1]-1
    #
    #         ts = siaqSimilarity(feature,graph,s,s11,s12,s,s21,s22)
    #         sq[(s11,s12)] = sq[(s11,s12)] + ts
    #     sq[(s11,s12)] = sq[(s11,s12)]/(s12-s11+1)
    # print("siaq %s:"%sure,sq)
    # maxsq = max(sq.values())
    # siaqAyat = []
    # for k in sq:
    #     if sq[k] == maxsq:
    #         siaqAyat = [ x for x in sortedAyat if ((int(x)>=k[0]) and (int(x)<=k[1])) ]
    #     sq[k] = sq[k]/maxsq
    #
    # print("siaq:%s"%sure,sq)
    # print("best siaq %s:"%sure,siaqAyat)
    #
    # return siaqAyat[0]

def getAddress(ayePos):
    import math
    s = math.floor(ayePos/(10*1000*1000))
    a = math.floor((ayePos%(10*1000*1000))/(10*1000))
    w = math.floor((ayePos%(10*1000))/(10))
    t = math.floor(ayePos%10)
    return (s,a,w,t)
def fromAddress(s,a,w,t):
    return 10*1000*1000*int(s)+10*1000*int(a)+10*int(w)+int(t)
def getFeatures(ayePos):
    global tokens
    x = getAddress(ayePos)
    return tokens[str(x[0])][str(x[1])][str(x[2])][str(x[3])]
def getAyeText(ayePos):
    global quran_text
    x = getAddress(ayePos)
    return quran_text[str(x[0])][str(x[1])] + u"(%d,%d)"%(x[0],x[1])


def saveTo(d,filename):
    import json
    with open(filename,"w") as f:
        f.write(json.dumps(d))

def loadFrom(filename):
    import json
    with open(filename) as f:
        d = json.loads(f.read())
    return d

def saveGraphToGDF(graph,gfdfile):
    with open(gfdfile,"w") as f:
        f.write("nodedef> name VARCHAR,label VARCHAR\n")
        for root in graph.keys():
            f.write("%s,\"%s\"\n"%(root,root))
        f.write("edgedef> node1,node2,weight DOUBLE,directed BOOLEAN\n")
        for a in graph.keys():
            for b in graph[a].keys():
                f.write("%s,%s,%f,true\n"%(a,b,graph[a][b]))

if __name__ == '__main__':
    import os.path

    rootWeights = {}

    metadata = parseQuranMetadata("quran-data.js")

    corpusfile = "corpus.json"
    if os.path.exists(corpusfile):
        tokens = loadFrom(corpusfile)
    else:
        tokens = parseQuranTokens("quranic-corpus-morphology-0.4.txt")
        saveTo(tokens,corpusfile)
    #print("tokens:", len(tokens))

    rootfile = "roots.json"
    if os.path.exists(rootfile):
        roots = loadFrom(rootfile)
    else:
        roots = getRootAyat(tokens)
        saveTo(roots,rootfile)
    #print("roots:",len(roots))

    quran_text = loadQuranText("quran-simple.txt")

    r = anotherFindAdvance2("LEM","Hakiym","ROOT","byn",0,2,1000,1000)
    r1 = ["%s \n %s\n-------"%(getAyeText(x[0]),getAyeText(x[2])) for x in r if x[3] not in ["bayona","bayoni"] ]
    print(len(r1))
    print(u"\n\n".join(r1))

    exit(0)

    rootsitem = sorted(list(roots.items()), key=lambda x: len(x[1]))
    print([ (x[0],len(x[1])) for x in rootsitem[-10:]])

    # lemfile = "lems.json"
    # if os.path.exists(lemfile):
    #     lems = loadFrom(lemfile)
    # else:
    #     lems = getLemAyat(tokens)
    #     saveTo(lems,lemfile)
    # print("lems:",len(lems["lems"]), "roots:", len(lems["roots"]))


    graphfile = "rootgraph.json"
    if os.path.exists(graphfile):
        rootGraph = loadFrom(graphfile)
    else:
        rootGraph = getRootGraph(roots)
        saveTo(rootGraph,graphfile)
        saveGraphToGDF(rootGraph,"rootGraph.gdf")

    # graphfile = "getLemSiaqGraph.json"
    # if os.path.exists(graphfile):
    #     lemGraph = loadFrom(graphfile)
    # else:
    #     lemGraph = getLemSiaqGraph(lems,metadata)
    #     saveTo(lemGraph,graphfile)
    #     saveGraphToGDF(lemGraph,"getLemSiaqGraph.gdf")


    # sureSelfSimilarity("LEM",lemGraph, metadata, tokens, "36")
    # sureSelfSimilarity("LEM",lemGraph, metadata, tokens, "32")
    sureSelfSimilarity("ROOT",rootGraph, metadata, tokens, "36")
    sureSelfSimilarity("ROOT",rootGraph, metadata, tokens, "2")
#    sureSelfSimilarity("ROOT",rootGraph, metadata, tokens, "32")
#    sureSelfSimilarity("ROOT",rootGraph, metadata, tokens, "2")
