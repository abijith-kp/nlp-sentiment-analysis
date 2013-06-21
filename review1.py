#please do not remove this comment
# Bird, Steven, Edward Loper and Ewan Klein (2009). Natural Language Processing 
# with Python. O’Reilly Media Inc

#!/usr/bin/python

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.chunk import RegexpParser
from sentiwordnet import SentiWordNetCorpusReader, SentiSynset
import re, string

####################### CONSTANTS #############################################
NP = 0
VP = 1
NN = 2
VB = 3
ADV = 4
ADJ = 5
PRD = 6
CLS = 7

####################### FUNCTIONS #############################################

def addNounPhrase(tree):          #returns tuple with <[ADJ] [NN]>
    adj = []
    nn = []
    
    #if len(tree) < 2:
	#try:
	#    if tree[0][1] == "JJ":
	#	adj.append(t[0])
	#    elif t[0][1] == "NN" or t[0][1] == "NNP" or t[0][1] == "NNS": 
	#	nn.append(t[0])
	#    elif t[0][1]=="NNPS":
	#	nn.append(t[0])
	#    elif t[0][1]=="PRP" or t[0][1] == "PRP$":
	#	nn.append(t[0])
	#except:
	#    pass
	#return (adj, nn)
   
    for t in tree:
	try:
	    if t[1] == "JJ":
		adj.append(t[0])
	    elif t[1] == "NN" or t[1] == "NNP" or t[1] == "NNS" or t[1]=="NNPS":
		nn.append(t[0])
	    elif t[1]=="PRP" or t[1] == "PRP$":
		nn.append(t[0])
	except:
	    continue

    #print (adj , nn)
    return (adj , nn)
	    
def addVerbPhrase(tree):
    adv = []
    vb = []
    
    for t in tree:
	#print t[1]
	try:
	    if t[1] == "RB" or t[1] == "RBR" or t[1] == "RBS":
		adv.append(t[0])
	except:
	    if t.node == "V":
		vb.append(t[0][0])
    #print (adv , vb)
    return (adv , vb)

def addPredicate(tree):
    tmp = (addNounPhrase(tree[0]), addVerbPhrase(tree[1]))
    return tmp

def addClause1(tree):
    tmp = (addNounPhrase(tree[0]), addPredicate(tree[1]))
    return tmp

def addClause2(tree):
    #print tree
    tmp = (addNounPhrase(tree[1]), addPredicate(tree[0]))
    #print tmp, ">>"
    return tmp

################################################################################
##### Evaluation of values #####################################################

def findScoreWord(word, dType):
    swn_filename = 'SentiWordNet_3.0.0_20130122.txt'
    swn = SentiWordNetCorpusReader(swn_filename)
    word = re.sub('[%s]' % re.escape(string.punctuation), ' ', word)
    word = word.lower()
    #print word
    wS = 0
    
    for w in word.split():
	#print w
	if dType == NN:
	    test = swn.senti_synsets(w, 'n')
	elif dType == ADJ:
	    test = swn.senti_synsets(w, 'a')
	elif dType == VB:
	    test = swn.senti_synsets(w, 'v')
	elif dType == ADV:
	    test = swn.senti_synsets(w, 'r')
	try:
	    wS += test[0].obj_score
	except:
	    continue
    #print word, wS
    if len(word.split()) == 0:
	return 0
    return wS/len(word.split())

def evalScore(one , two, three):
    t = 0
    if three == NP:
	if one >= 0 and two >= 0:
	    t = +(abs(two) + (1-abs(two)) * abs(one))
	elif one >= 0 and two < 0:
	    t = -(abs(two) + (1-abs(two)) * abs(one))
	elif one < 0 and two >= 0:
	    t = one
	elif one < 0 and two < 0:
	    t = -(abs(two) + (1-abs(two)) * abs(one))
    
    elif three == VP:
	if one >= 0 and two >= 0:
	    t = +(abs(one) * (1-abs(two)))
	elif one >= 0 and two < 0:
	    t = -(abs(one) * (1-abs(two)))
	elif one < 0 and two >= 0:
	    t = -(abs(one) * (1-abs(two)))
	elif one < 0 and two < 0:
	    t = +(abs(one) * (1-abs(two)))
	#print t, " ", one ," ",  two
    elif three == PRD:
	if one >= 0 and two >= 0:
	    t = +(abs(two) * (1-abs(one)))
	elif one < 0 and two >= 0:
	    t = -(abs(two) * (1-abs(one)))
	elif one >= 0 and two < 0:
	    t = -(abs(two) * (1-abs(one)))
	elif one < 0 and two < 0:
	    t = +(abs(two) * (1-abs(one)))
    
    elif three == CLS:
	#print one, ">>>>>", two
	if abs(one) > abs(two):
	    t = one;
	else:
	    t = two
	    
    return t

################################################################################


def findScoreSO(tmpNP):		#tmpNP = [(<[ADJ] [NN]>) , ...]
    scoreAdj = 0
    scoreNn = 0
    totalScore = 0	

    for temp in tmpNP:
	
	scoreAdj = 0
	scoreNn = 0
	
	for t1 in temp[0]:
	    scoreAdj +=  findScoreWord(t1, ADJ)
	
	for t1 in temp[1]:
	    scoreNn +=  findScoreWord(t1, NN)
	
	if len(temp[0]) != 0 and len(temp[1]) != 0:
	    totalScore += evalScore((scoreAdj/len(temp[0])), 
(scoreNn/len(temp[1])), NP)
	
	elif len(temp[0]) == 0 and len(temp[1]) != 0:
	    totalScore += (scoreNn/len(temp[1]))
	
	elif len(temp[0]) != 0 and len(temp[1]) == 0:
	    totalScore += (scoreAdj/len(temp[0]))
	
	else:
	    totalScore += 0
	
    if len(tmpNP) != 0:
	return totalScore/len(tmpNP)
    else:
	return 0


def findScoreVP(tmpVP):
    scoreAdv = 0
    scoreVb = 0
    totalScore = 0
   
    for temp in tmpVP:
	scoreAdv = 0
	scoreVb = 0
	for t1 in temp[0]:
	    scoreAdv +=  findScoreWord(t1, ADV)
	for t1 in temp[1]:
	    scoreVb +=  findScoreWord(t1, VB)
	
	if len(temp[0]) != 0 and len(temp[1]) != 0:
	    totalScore += evalScore((scoreAdv/len(temp[0])), 
(scoreVb/len(temp[1])), VP)
	
	elif len(temp[0]) == 0 and len(temp[1]) != 0:
	    totalScore += (scoreVb/len(temp[1]))
	
	elif len(temp[0]) != 0 and len(temp[1]) == 0:
	    totalScore += (scoreAdv/len(temp[0]))
	else:
	    totalScore += 0
	#print totalScore, temp
    #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>"
    if len(tmpVP) != 0:
	return totalScore/len(tmpVP)
    else:
	return 0

def findScorePredicate(tmpPrd):
    totalScore = 0
    tmpNP = []
    tmpVP = []
    #print tmpPrd
    for temp in tmpPrd:
	tmpNP.append(temp[0])
	tmpVP.append(temp[1])
	#print type(tmpPrd), " ", type(temp[1])
	totalScore += evalScore(findScoreSO(tmpNP), findScoreVP(tmpVP), PRD)
	#print findScoreSO(tmpNP), "..", findScoreVP(tmpVP), "..", totalScore
    if len(tmpPrd) != 0:
	return totalScore/len(tmpPrd)
    else:
	return 0

def findScoreClause(tmpCls):
    totalScore = 0
    tmpNP = []
    tmpPrd = []
    #print tmpPrd
    for temp in tmpCls:
	tmpNP.append(temp[0])
	tmpPrd.append(temp[1])
	#print tmpCls, " ", tmpCls
	totalScore +=evalScore(findScoreSO(tmpNP),findScorePredicate(tmpPrd) , 
CLS)
	#print findScoreSO(tmpNP), "..", findScorePredicate(tmpPrd), ".."
    if len(tmpCls) != 0:
	return totalScore/len(tmpPrd)
    else:
	return 0
    

################################################################################
################################################################################

review = " "
punctuation = [",",";",".",":",","]


grammer = '''
    NP: {<DT>? <JJ>* <NN.*|PR.*>*}
    P: {<IN>}          
    V: {<V.*>}
    PP: {<P> <NP>}    
    '''
vp = "VP: {<RB|RBR|RBS>* <V> <RB|RBR|RBS>* <NP|PP>*}\n"
prd = "PRD: {<NP> <VP>}\n"
cls1 = "CLS1: {<NP> <PRD>}\n"
cls2 = "CLS2: {<PRD> <NP>}\n"

print "Loading input file..."
fileReview = open("input", "r")	#open 
#file to retrive movie 
#reviews
arr = fileReview.read()

while arr:				#removes all trilling white spaces and
    review += arr.strip()		#adds it to var review
    arr = fileReview.read()

fileReview.close()

print "Sentence tokenization..."
review_dict = sent_tokenize(review)	#tokenizes sentences
arr_pos = []
removed = []

print "POS tagging for words..."
#arr_sent = pos_tag(review_dict)		#tagging words for semantic 
#annotation

for sent in review_dict:	#adding individual sentences after tagging
    arr_pos.extend([pos_tag(sent.split())].__iter__())
    

################################################################################
################################################################################


print "Loading Parser..."
#t = npc.parse(tmp_arr_pos[0])
print "Finished loading..."

#print len(t)
#t.draw()
#help(t)
sentCount = 1
sentScore = []          #tuple with (Subj-Obj , Verb-P , )
totalS = []

print "Processing input..."
print "Number of sentences to process: ", len(arr_pos)

for q in ["", vp, prd, cls1, cls2]:
   grammer += q
   npc = RegexpParser(grammer)
   print "\n\n"
   for i in arr_pos:
	print "Reading sentence ", sentCount
	sentCount += 1
	t = npc.parse(i)
	print t
	tmpVP = []
	tmpNP = []
	tmpPrd = []
	tmpCls = []
	x1 = ""
   
	for x in t:
	    try:
		if x.node == "VP":
	       #print x
		    x1 = addVerbPhrase(x)
		    tmpVP.append(x1)
	       
		if x.node == "NP":
		    x1 = addNounPhrase(x)
		    tmpNP.append(x1)
	       
		elif x.node == "PRD":
		    x1 = addPredicate(x)
		    tmpPrd.append(x1)
	      
		elif x.node == "CLS1":
		    x1 = addClause1(x)
		    tmpCls.append(x1)
	       #print x1

		elif x.node == "CLS2":
		    x1 = addClause2(x)
		    tmpCls.append(x1)
	       #print x1
	    except:
		continue
   #print findScorePredicate(tmpPrd), "\n"
   #sentScore.append((findScoreSO(tmpNP), findScoreVP(tmpVP), 
#findScorePredicate(tmpPrd), findScoreClause(tmpCls)))
    
	totalS.append(1)
   
	tNp = findScoreSO(tmpNP)
	tVp = findScoreVP(tmpVP)
	tPrd = findScorePredicate(tmpPrd)
	tCls = findScoreClause(tmpCls)

	if tNp != 0:
	    totalS.append(totalS.pop() * tNp)
   
	#print totalS
	if tVp != 0:
	    totalS.append(totalS.pop() * tVp)
   
	#print totalS
	if tPrd != 0:
	    totalS.append(totalS.pop() * tPrd)
   
	#print totalS
	if tCls != 0:
	    totalS.append(totalS.pop() * tCls)
   
	#print totalS
   
for i in totalS:
    print i