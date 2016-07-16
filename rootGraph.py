
def parseQuranMetadata(resourceFile):
    import json
    with open(resourceFile) as f:
        metadata = json.loads(f.read())
    return metadata

def parseQuranTokens(corpusFile):
    tokens = {}
    with open(corpusFile) as file:
        for line in file:
            address, form, pos, feature = line.split("\t")
            features = dict([(a+":").split(":")[:2] for a in feature.strip().split("|")])
            features["form"] = form
            features["pos"] = pos
            sure,aye,kalame,token = [int(x) for x in address.strip()[1:-1].split(":")]
            if sure not in tokens: tokens[sure] = {}
            if aye not in tokens[sure]: tokens[sure][aye] = {}
            if kalame not in tokens[sure][aye]: tokens[sure][aye][kalame] = {}
            if token not in tokens[sure][aye][kalame]: tokens[sure][aye][kalame][token] = features
    return tokens

def getRootAyat(tokens):
    roots = {}
    for sure in tokens.keys():
        for aye in tokens[sure].keys():
            for kalame in tokens[sure][aye].keys():
                for token in tokens[sure][aye][kalame].keys():
                    if "ROOT" in tokens[sure][aye][kalame][token]:
                        root = tokens[sure][aye][kalame][token]["ROOT"]
                        if root not in roots:
                            roots[root] = []
                        roots[root].append(aye + sure*1000)#token + (kalame + (aye + sure*1000)*1000)*10)
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

def ayeSimilarity(graph,a,b):
    import math
    d = 0
    for wordA in a.keys():
        for tokenA in a[wordA].keys():
            for wordB in b.keys():
                for tokenB in b[wordB].keys():
                    if "ROOT" in a[wordA][tokenA] and "ROOT" in b[wordB][tokenB]:
                        try:
                            d = d + graph[ a[wordA][tokenA]["ROOT"] ][ b[wordB][tokenB]["ROOT"] ]
                        except:
                            pass
    d = d / math.sqrt(len(a)*len(b))
    return d

def siaqSimilarity(graph,s1,s11,s12,s2,s21,s22):
    d = 0
    for ayeA in s1:
        if int(ayeA) < s11 or int(ayeA) >  s12:
            continue
        for ayeB in s2:
            if int(ayeB) <s21 or int(ayeB) > s22:
                continue
            d = d + ayeSimilarity(graph,s1[ayeA],s2[ayeB])
    d = d / ((s12-s11+1) * (s22-s21 + 1))
    return d

def sureSelfSimilarity(graph, metadata, tokens, sure):
    r = {}
    s = tokens[sure]
    ayat = list(s.keys())
    ayat.sort()
    for ayeA in ayat:
        r[ayeA] = 0
        for ayeB in ayat:
            if ayeA is not ayeB:
                ts = ayeSimilarity(graph,s[ayeA],s[ayeB])
                r[ayeA] = r[ayeA] + ts
    sortedAyat = sorted(r, key=r.get)[::-1]
    print("ayat:",sortedAyat)

    siaqs = sorted([s[1] for s in metadata["Ruku"] if len(s)>0 and s[0] is int(sure)])
    siaqs.append(len(s))
    print("siaqs:",siaqs)

    sq = {}
    for i1 in range(len(siaqs)-1):
        s11 = siaqs[i1]
        s12 = siaqs[i1+1]-1
        sq[(s11,s12)] = 0
        for i2 in range(len(siaqs)-1):
            if i2 is i1:
                continue
            s21 = siaqs[i2]
            s22 = siaqs[i2+1]-1

            ts = siaqSimilarity(graph,s,s11,s12,s,s21,s22)
            sq[(s11,s12)] = sq[(s11,s12)] + ts
        sq[(s11,s12)] = sq[(s11,s12)]/(s12-s11+1)
    print("siaq:",sq)
    maxsq = max(sq.values())
    siaqAyat = []
    for k in sq:
        if sq[k] == maxsq:
            siaqAyat = [ x for x in sortedAyat if ((int(x)>=k[0]) and (int(x)<=k[1])) ]
        sq[k] = sq[k]/maxsq

    print("siaq:",sq)
    print("best siaq:",siaqAyat)

    return siaqAyat[0]

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

    corpusfile = "corpus.json"
    if os.path.exists(corpusfile):
        tokens = loadFrom(corpusfile)
    else:
        tokens = parseQuranTokens("quranic-corpus-morphology-0.4.txt")
        saveTo(tokens,corpusfile)
    print("tokens:", len(tokens))

    metadata = parseQuranMetadata("quran-data.js")

    rootfile = "roots.json"
    if os.path.exists(rootfile):
        roots = loadFrom(rootfile)
    else:
        roots = getRootAyat(tokens)
        saveTo(roots,rootfile)
    print("roots:",len(roots))


    graphfile = "rootgraph.json"
    if os.path.exists(graphfile):
        rootGraph = loadFrom(graphfile)
    else:
        rootGraph = getRootGraph(roots)
        saveTo(rootGraph,graphfile)
        saveGraphToGDF(rootGraph,"rootGraph.gdf")

    yasinSims = sureSelfSimilarity(rootGraph, metadata, tokens, "36")
    yasinSims = sureSelfSimilarity(rootGraph, metadata, tokens, "2")
