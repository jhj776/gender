# casts.py: A Python Program to check gender matches of names in wikipedia movie casts lists: actors / characters

## version
This is beta version 0.1.1  

## suggested citation:
Vanneman, Reeve. 2020.  "casts.py: A Python Program to Code Check Gender in Movie Cast Lists.
url: https://github.com/ReeveVanneman/gender Version 0.1.1.

## names
casts.py uses two sources to determine gender of a name (or some words)
	gendernames.json
	gender_guesser
It categorizes each name into:
	female
	mostly_female
	andy (androgynous)
	mostly_male
	male
	unknown (i.e., not found in either list)

## arguments  
casts.py is called with one argument, a prefix for input and output files.  e.g., US, Fr, SK,
	 python3 casts.py US
would look for a file USfiles.txt that lists all the files of cast lists from US movies
It would also produce output files with the prefix US (USnames.xls, UScharacters.xls, etc.)
  
## compiling jobs.py:  
jobs.py uses python standard packages: json sys  
jobs.py also uses python packages that must be downloaded and installed: gender_guesser BeautifulSoup

## input files:  
- prefix+files.txt (e.g., USfiles.txt)  = a file of filenames of cast lists to be read 
These are local file names (which can include absolute or relative addresses) that casts.py loops through searching for names.

- gendernames.json  = a json file of names and words with assigned genders
This file can always be improved and updated.
  
The casts.py program is in 2 main sections:
- it divides each line in a cast list into 3 parts: actor name / character name / & optional additional material
- it assigns each actor's name and character's name a gender using (first) gendernames.json and if not there, gender_guesser
	- the first word in a name that gets an assigned gender other than "unknown" determines the assigned gender
	-	for Chinese and Korean names, the program works backwards from the end
	- if none of the names are found in either list, the name is assigned "unknown"
	- for each cast line, casts.py compiles joint counts of the gender of the actor and gender of the character

## output files:  
( "XX" below is the prefix arg, e.g., US )

- main output: XXnames.xls  
For each unique name (either actor's or character's) it lists the counts by the 6 gender categories.

- detailed output: XXcharacter.xls  
For each line in the cast for each file in XXfiles.txt, casts.py writes one record of movie file name, the actor's and character's names and the assigned genders

- text file descriptions: XXtexts.xls  
after processing each movie, writes a count of #lines, #words, #actors, #characters, #line with additional text, #lines that are not actor/character lines.
