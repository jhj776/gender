# casts.py
#	version 0.1.1
#	1. reads a series of text files of cast lists from wikipedia movie .html files, and parse into 3 parts
#		- actor
#		- character
#		- other description
#	2. assigns genders to actor and character names 
#		(female, mostly_female, andy, mostly_male, male, unknown)
#	eventually will:
#		3. count how often the character's name (first, last, both) appear in plot summary
#			eventually even attribute "he","she","her", etc to that character
#		4. associate each character with one or more "occupations"
#			first, based on details in cast list (details are usually not included in cast lists)
#			then based on associating character name with a jobtitle in plot summary
#			codes these ~30,000 "jobtitles" into 2010 3-digit U.S. Census codes 
#			several added codes for "jobtitles" that are not employment Census occupations
#				(e.g., wife, criminal, miiitary, France)
#				these text titles are coded into new (non-Census) codes
#				also, some Census codes are subdivided: e.g., (CEOs: govt & pvt; 
#
#	arg= prefix is a filename prefix to output (& input) files
#		e.g. python3 casts.py NYT
#
#	input:
#		prefix+files.txt (e.g., NYTfiles.txt)= a file of filenames of text files to be read and coded.
#		gendernames.json	revisions of gender_guesser, "name": "gender",
#			problem: chick-> female; Check-> male.
#
#	to compile casts.py:
#		uses python standard packages: sys json
#		uses python packages that must be downloaded and installed: gender_guesser BeautifulSoup
#			e.g. pip install BeautifulSoup4
#			e.g. pip install gender-guesser  (see:  https://pypi.org/project/gender-guesser/)
#

import json
import sys
import gender_guesser.detector as gender
g = gender.Detector(case_sensitive=False)

# argument is prefix (e.g., US, Fr, SK, etc.)
# 	there should be one and only one argument in calling Python
Nargs= len(sys.argv)
if Nargs<2:
	print("You need to call casts.py with an argument giving the filename prefix")
	print("	e.g., python3 casts.py movies")
	print("	exiting...")
	sys.exit()
else:
	prefix= sys.argv[1]
	print("prefix: ", prefix)

# to strip html code from text:
from bs4 import BeautifulSoup

#
# Korean surnames that would be coded as English first names:
notgivenname= ['Gil', 'Kim', 'Lee']	# ?: Ma
#
# first words in some nonstandard lines that will be dropped:
nonstandard= ['Cast', 'cast', 'The cast', '(Cast', '(cast', 'Additional', 'Additionally', 'Categories', 'Categories:', 'Other', 'other', 'Retrieved', 'Uncredited']
#
xtab= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
####################################
# 3 output files:
#
# name-level summary: after proccessing all casts, list each name found & its counts
namesfile= prefix + "names.xls"	
namesf= open(namesfile, "w")
namesf.write ("iname	name	gender	Nfound	Nactor	Nchar	Nfemale	Nmfemale	Nandy	Nmmale	Nmale	Nunknown	PairScore	PctFemale	PctMale\n")
#
# detailed output: XXcharacters.xls= after processing each text file, writes one record for each character
#	writes as tab delimited file for input into spreadsheet/ stats program
charfile= prefix + "characters.xls"	
charf= open(charfile, "w")
charf.write ("filename" + "	AName" + "	Actor" + "	AGender" + "	CName" + "	Character" + "	ChGender" + "	additional" + "\n" )
#
# nonstandard lines have no actor as character... OR actor - character...
#	print to separate file to figure out what is wrong
nonstandardfile= prefix + "nonstandard.txt"	
nonstandardf= open(nonstandardfile, "w")
nonstandardf.write ("filename" + "	" + "nonstandard line:\n")
#
# text-level summary: after processing each text, writes a count of #words, #sentences, etc., one line per text
textsfile= prefix + "texts.xls"	
textsf= open(textsfile, "w")
textsf.write ("Nlines	Nread	Nwords	Nactors	Nchars	Nextra	Nnonstandard	movie\n")

####################################
# 2 input files:
#
# read list of filenames of input texts such as files with movie plots, newspaper articles, other texts.
infilelist= prefix + "files.txt"
files=open(infilelist).read()
# files is a long string with all file names:
# number of files:
textfiles=files.split('\n')
Ntextfiles=len(textfiles)
Sumtextlines=0
# strip off end of file line:
textfiles=textfiles[0:Ntextfiles-1]
print ('\nList of text files to be analyzed: ' + infilelist + " " + str(type(textfiles)) + ", #files= " + str(len(textfiles)) + '\n')
print       ('\ntext list: ' + infilelist + " " + str(type(textfiles)) + ", #files= " + str(len(textfiles)) + '\n')
#textsf.write ('	text list: ' + infilelist + " " + str(type(textfiles)) + ", #files= " + str(len(textfiles)) + '\n')
#
# read json file of supplemental (corrected) names and gender:
# 	Queen, Princess, King, Prince, -- already in gender_guesser
genderwords= open("genderwords.json").read()
# genderwords is a long string, make genderwords into a dict, namegender:
namegender= json.loads(genderwords)
print  ('\nnamegender (names with fixed gender)= ' + str(type(namegender)) + ' Nlines=' + str(len(namegender)) )
#outlog.write  ('\njoblabels (jobtitles mostly from Census+)= ' + str(type(joblabels)) + ' Nlines=' + str(len(joblabels)) )

foundnames= ["given_name"]
gendernames= ["unknown"]
countnames= [0]
countanames= [0]
countcnames= [0]
countmales= [0]
countmmales= [0]
countmfemales= [0]
countfemales= [0]
countandy= [0]
countunknown= [0]

for file in textfiles:
	Nactors=0
	Ncharacters=0
	Nnochar=0
	Nadditional=0
	Nnonstandard=0
	Nblanklines=0
	# write blank line to character.xls file to separate each movie:
	charf.write ("\n")
	# todo: work with different codings
	#text0=open(file, encoding = "ISO-8859-1").read()
	text0=open(file).read()
	# drop html:
	text1= BeautifulSoup(text0, features="html.parser")
	textstring= text1.get_text()
	Nbytes=len(textstring)
	Nwords=textstring.count(" ")
	Nlines=textstring.count("\n")
	textstring= textstring.replace('/',' / ')
	textstring= textstring.replace('[',' [')	# wikipedia footnotes: separate word
	textstring= textstring.replace('	', ' ')
	textstring= textstring.replace('  ',' ')
	#print ("\nafter BeautifulSoup: " + file + ":\n" + str(textstring) + "\nNlines= " + str(Nlines) + "\nNwords= " + str(Nwords))
	#
	# make each sentence a new string
	textlines0= textstring.splitlines()
	Ntextlines0= len(textlines0)
	Sumtextlines= Sumtextlines + Ntextlines0
	# process each line in the file:
	#
	# first drop some nonstandard lines beginning with the above list of nonstandard beginning words:
	textlines= [""]
	Ntextlines= len(textlines)
	iline0=0
	for line in textlines0:
		iline0= iline0+1
		line= line.strip()
		line= line.replace('	', ' ')
		line= line.replace('  ',' ')
		lenline= len(line)
		if lenline>0 :
			words= line.split(" ")
			if words[0] in nonstandard:
				Nnonstandard= Nnonstandard+1
				nonstandardf.write (file + "	common nonstandard line:	" + str(line) + "\n" )
			else:
				textlines.append(line)
	iline=0
	for line in textlines:
		lenline= len(line)
		Nwordline= line.count(" ") + 1
		actor=""
		char=""
		aname=""
		tempname=""
		additional=""
		iline= iline+1
		#
		# find the separation marker between actor name and character name
		# 	endactor#= the position in the line where it is found
		# 	if more than one separation marker, use the first one
		# 	if more than one separation marker, use the first one
		#
		# most cast lists separate actor and character with " as "
		endactor1= line.find(" as ")
		if endactor1==-1:
			endactor1=lenline
		# a few cast lists separate actor and character with " - "
		endactor2= line.find(" - ")	# dash with spaces around (not a hyphen)
		if endactor2==-1:
			endactor2=lenline
		# a few cast lists separate actor and character with " ... " or more periods
		endactor3= line.find("...")
		if endactor3==-1:
			endactor3=lenline
		endactor4= line.find(":")
		if endactor4==-1:
			endactor4=lenline
		endactor5= line.find("â")
		if endactor5==-1:
			endactor5=lenline
		endactor6= line.find("–")
		if endactor6==-1:
			endactor6=lenline
		# if there are more than one of these breaks, use the first one on the line
		endactor= min(endactor1, endactor2, endactor3, endactor4, endactor5, endactor6)
		# test if no marker found or if very long line:
		if endactor==lenline or endactor>80:
			#print ('no "as" or " - " or "..." or ":" in:	' + str(line) + "\n")
			startchar=0
			if Nwordline>0 & Nwordline<5:	# the line has words but 4 or less
				#	probably only an actor listed with no character
				Nnochar=Nnochar+1
				actor=line[:endactor].strip()
				Nactors= Nactors+1
			elif lenline>0:  # not a blank line (often a blank entry in a 2-column cast list)
				# save this probably only an actor name line to nonstandard line file
				#	won't be analyzed because no actor -> character match
				# can't figure out what this line is; save in file of nonstandard lines
				nonstandardf.write (file + "	longact:	" + str(line) + "\n" )
				Nnonstandard= Nnonstandard+1
		else:
			# a standard line with " as ", " - ", or "..." or one of the 6 standard separator markers:
			#	the separators are of different lengths so must start character names at different positions:
			if endactor==endactor1:		# " as "
				startchar=4
			elif endactor==endactor2:	# " - "
				startchar=3
			elif endactor==endactor3:	# "... "
				startchar=4
			elif endactor==endactor4:	# ":"
				startchar=1
			elif endactor==endactor5:	# "â" non-ascii
				startchar=6
			elif endactor==endactor6:	# "–" n-dash
				startchar=1
			else:
				startchar=0
				nonstandardf.write (file + "	no as; endactor=", str(endactor), "	", line, "\n")
			startchar=endactor+startchar
			actor=line[:endactor].strip()
			Nactors= Nactors+1
			#
			# find end of character name:
			#	character name ends with a , : , end of line, or some distinctive character
			#	begin find only after actor's name since a few actors have a comma ( , Jr. )
			Nwordchar= line[startchar:].count(" ")
			endcomma= line[startchar:].find(",")
			if endcomma== -1:
				endcomma=lenline
			endcolon= line[startchar:].find(":")
			if endcolon== -1:
				endcolon=lenline
			endsemicolon= line[startchar:].find(";")
			if endsemicolon== -1:
				endsemicolon=lenline
			endcarata= line.find("â")
			if endcarata== -1:
				endcarata=lenline
			endendash= line[startchar:].find("–")
			if endendash== -1:
				endendash=lenline
			endhyphen= line[startchar:].find(" - ")
			if endhyphen== -1:
				endhyphen=lenline
			endparen= line[startchar:].find("(")
			if endparen== -1:
				endparen=lenline
			endchar= min(endcomma, endcolon, endsemicolon, endcarata, endendash, endhyphen, endparen)
			if endchar==lenline:
				# no comma, colon, etc.
				if Nwordchar>=8 :
					# more than 8 words describing character (even if no , or :)
					nonstandardf.write (file + "	8words+:	" + str(line) + "\n" )
					Nnonstandard= Nnonstandard+1
				#else:
				char= line[startchar:].strip()
				lenchar= len(char)
				if lenchar>0:
					if char[-1]==".":
						char= char[0:-1]
					Ncharacters= Ncharacters+1
			else:
				# line has a comma, colon, semicolon, etc.:
				char= line[startchar:endchar+startchar].strip()
				lenchar= len(char)
				if lenchar>0:
					if char[-1]==".":
						char= char[0:-2]
					Ncharacters= Ncharacters+1
				additional= line[1+endchar+startchar:]
				lenadditional= len(additional)
				Nadditional= Nadditional+1
			#
			# line is now separated into 3 parts: full actor name, full character name, additional words
			#
			# loop through the words in anames[] to find first gendered name or title (e.g. Mrs.)
			actor= actor.replace('	',' ')	# rarely a tab separates words in names
			actor= actor.replace("'","")	# delete quotes around nicknames, e.g., 'Doc'
			anames= actor.split(" ")	# this will separate some compound names
			if prefix=="SK":
				anames= anames.reverse()
			agender= "unknown"
			for aname in anames:
				# some common surnames in Korean are given names in English;
				if prefix=="SK" and aname in notgivenname:
					agender= "unknown"
				elif len(aname)>0 and aname[0]=="[":	# wiki footnote usually at end of char section
					agender= "unknown"
				elif len(aname)>=2 and aname[-2]=="'" and aname[-1]=="s":	# possessive
					agender= "unknown"
				elif len(aname)>=2 and aname[-2]=="s" and aname[-1]=="'":	# plural possessive
					agender= "unknown"
				else:
					# then check if aname is in revision dict, namegender{}, above:
					agender= namegender.get(aname.lower())
					if agender==None:	# aname not found in updated namegender json file
						# last place to look is in gender_guesser
						agender= g.get_gender(aname)
					if agender!= "unknown": 	#if gender is unknown, then continue for loop & go to next word; ?"andy"?
						break
			if agender=="unknown":	# if at end of for loop, all anames are unknown gender, then use the first word
				# ? but maybe the second if the first is just a title?
				aname=anames[0]
			# check whether this aname has already been found: 
			if aname in foundnames:
				# aname has been found before, so just increment count
				iname= foundnames.index(aname)
				countnames[iname]=  countnames[iname]+1
				countanames[iname]= countanames[iname]+1
			else:
				# aname has not been found before, so add to list of names found
				foundnames.append(aname)
				iname= len(foundnames)-1
				countnames.append(1)
				countanames.append(1)
				countcnames.append(0)
				gendernames.append(agender)
				countmales.append(0)
				countmmales.append(0)
				countandy.append(0)
				countmfemales.append(0)
				countfemales.append(0)
				countunknown.append(0)
			ianame= iname
			# 
			# loop through the words in cnames[] to find first gendered name | title
			char= char.replace('	',' ')	# rarely a tab separates words in names
			char= char.replace("'","")	# delete quotes around nicknames, e.g., 'Doc'
			cnames= char.split(" ")		# this will separate some compound names
			cgender= "unknown"
			if prefix=="SK":
				cnames= cnames.reverse()
			for cname in cnames:
				if prefix=="SK" and cname in notgivenname:
					cgender= "unknown"
				else:
					# then check if cname is in revision dict, namegender{}, above:
					cgender= namegender.get(cname.lower())
					if cgender==None:	# cname not found in updated namegender json file
						# last place to look is in gender_guesser
						cgender= g.get_gender(cname)
					if cgender!= "unknown": 	#if gender of cname is unknown, then continue for loop & go to next word
						break
			if cgender=="unknown":	# if all cnames are unknown gender, then use the first word
				# ? but maybe the second if the first is just a title?
				cname=cnames[0]
			# check whether this cname has already been found: 
			if cname in foundnames:
				# cname has been found before, so just increment count
				iname= foundnames.index(cname)
				countnames[iname]=  countnames[iname]+1
				countcnames[iname]= countcnames[iname]+1
			else:
				# cname has not been found before, so add to list of names found
				foundnames.append(cname)
				iname= len(foundnames)-1
				countnames.append(1)
				countcnames.append(1)
				countanames.append(0)
				gendernames.append(cgender)
				countmales.append(0)
				countmmales.append(0)
				countandy.append(0)
				countmfemales.append(0)
				countfemales.append(0)
				countunknown.append(0)
			icname= iname
			# increment counts of actor genders for this character name
			if agender=="female":
				countfemales[icname]= countfemales[icname]+1
				xtabcell=0
			elif agender=="mostly_female":
				countmfemales[icname]= countmfemales[icname]+1
				xtabcell=7
			elif agender=="andy":
				countandy[icname]= countandy[icname]+1
				xtabcell=14
			elif agender=="mostly_male":
				countmmales[icname]= countmmales[icname]+1
				xtabcell=21
			elif agender=="male":
				countmales[icname]= countmales[icname]+1
				xtabcell=28
			elif agender=="unknown":
				countunknown[icname]= countunknown[icname]+1
				xtabcell=35
			else:
				xtabcell=42	# no actor
			# increment counts of character genders for this actor name
			if cgender=="female":
				countfemales[ianame]= countfemales[ianame]+1
				#xtabcell= xtabcell+0
			elif cgender=="mostly_female":
				countmfemales[ianame]= countmfemales[ianame]+1
				xtabcell= xtabcell+1
			elif cgender=="andy":
				countandy[ianame]= countandy[ianame]+1
				xtabcell= xtabcell+2
			elif cgender=="mostly_male":
				countmmales[ianame]= countmmales[ianame]+1
				xtabcell= xtabcell+3
			elif cgender=="male":
				countmales[ianame]= countmales[ianame]+1
				xtabcell= xtabcell+4
			elif cgender=="unknown":
				xtabcell= xtabcell+5
				countunknown[ianame]= countunknown[ianame]+1
			else:
				xtabcell= xtabcell+6
			xtab[xtabcell]= xtab[xtabcell]+1
			charf.write (file + "	" + aname + "	" + actor + "	"  + agender + "	" + cname + "	" + char + "	" +cgender + "	" + additional + "\n")
	textsf.write (str(Nlines) + "	" + str(iline) + "	" + str(Nwords) + "	" + str(Nactors) + "	" + str(Ncharacters) + "	" + str(Nadditional)+ "	" + str(Nnonstandard) + "	" + file + "\n")
	print ("Nlines=" + str(Nlines) + "	iline=" + str(iline) + " 	#words=" + str(Nwords) + "	#actors=" + str(Nactors) + "	#characters=" + str(Ncharacters) + "	#w/extra=" + str(Nadditional)+ "	#nonstandard lines=" + str(Nnonstandard) + "	"+ file )
#totalsf.write ("\n# titles=" + str(Sumales) + "\n# files=" + str(len(textfiles)) + "\n# sentences=" + str(Sumsentences) + "\n# words=" + str(Sumwords) + "\n" )
print ("# names=" + str(len(foundnames)))
Sumnames= len(foundnames)
for iname in range(Sumnames):
	# pairscore is summary measure of whether the paired name (e.g. the character's when found name is the actor's) is female (negative scores=male)
	pairscore=2*countfemales[iname]+countmfemales[iname]-countmmales[iname]-2*countmales[iname]
	# pctfemale is % of foundnames that are "female" or "mostly_female";
	#	can be used to identify errors in male names
	if countnames[iname]>0:
		pctfemale=100*(countfemales[iname]+countmfemales[iname])/countnames[iname]
	else:
		pctfemale=0
	# pctmale is % of foundnames that are "male" or "mostly_male";
	#	can be used to identify errors in female names
	#	pctmale + pctfemale <=100 because andy, unknown
	if countnames[iname]>0:
		pctmale=100*(countmales[iname]+countmmales[iname])/countnames[iname]
	else:
		pctfemale=0
	lineout= str(iname) +"	"+ foundnames[iname] +"	"+ gendernames[iname] +"	"+ str(countnames[iname]) +"	"+ str(countanames[iname]) +"	"+ str(countcnames[iname]) +"	"+ str(countfemales[iname]) +"	"+ str(countmfemales[iname]) +"	"+ str(countandy[iname]) +"	"+ str(countmmales[iname]) +"	"+ str(countmales[iname]) +"	"+ str(countunknown[iname]) + "	" + str(pairscore) + "\n" 
	namesf.write (lineout)
print ("\n# unique names=", str(len(foundnames)), "\n")
print ("See XXnames.xls; sort on gender, pairscore to revise unknown and andy")
print ("See XXnames.xls; sort on gender, pctmale or gender, pctfemale to check male&female errors")
#
#	crosstabs of actor gender X character gender
coltotal= [0,0,0,0,0,0,0]
print ("\n 	character gender:")
print ("actor:	female	mfemale	andy	male	mmale	unknown	miss	rowtotal")
rowlabel= ["female", "mfemale", "andy", "mmale", "male", "unknown", "miss", "rowtotal"]
for row in range(0,49,7):
	rowtotal= xtab[row+0] + xtab[row+1] + xtab[row+2] + xtab[row+3] + xtab[row+4] + xtab[row+5] + xtab[row+6]
	coltotal[0]= coltotal[0] + xtab[row+0]
	coltotal[1]= coltotal[1] + xtab[row+1]
	coltotal[2]= coltotal[2] + xtab[row+2]
	coltotal[3]= coltotal[3] + xtab[row+3]
	coltotal[4]= coltotal[4] + xtab[row+4]
	coltotal[5]= coltotal[5] + xtab[row+5]
	coltotal[6]= coltotal[6] + xtab[row+6]
	rowint=int(row/7)
	print (rowlabel[rowint], str(xtab[row+0]), str(xtab[row+1]), str(xtab[row+2]), str(xtab[row+3]), str(xtab[row+4]), str(xtab[row+5]), str(xtab[row+6]), str(rowtotal), sep="	")
total= coltotal[0] + coltotal[1] + coltotal[2] + coltotal[3] + coltotal[4] + coltotal[5] + coltotal[6]
print ("\ntotals", str(coltotal[0]), str(coltotal[1]), str(coltotal[2]), str(coltotal[3]), str(coltotal[4]), str(coltotal[5]), str(coltotal[6]), str(total), sep="	")
print ("\n", str(total), " movie actor/character pairs out of ", str(Sumtextlines), " lines in the ", str(Ntextfiles)," cast files.")
print ("\nSee XXcharacters.xls for each movie character.")
print ("	Sort by Cname Chgender Agender Aname (or by Aname Agender Cgender Cname) to identify misclassified names.")
print ("\n	exiting...")
sys.exit()

