#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dicip.py
#  
# Just a fun scrit I made, after talking with some friends. 
# It "encrypts" a message by looking up the words in a dictionary, and then
# finds the word on the "oposite side" of the dictionary. it does this for every word, giving 
# a nonsensicall sentence. It can both encrypt and decrypt.
# Also uses fuzzy matching to find closest match if word is not found in dictionary
#  



import string
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def normalize(s):
	for p in string.punctuation:
		s = s.replace(p, '')
	return s.lower().strip()

def slicedict(d, s):
    return {k:v for k,v in d.iteritems() if k.startswith(s)}


def encrypt(encryptString,bywords,byindex,justwords,b):
	encrypted = ""
	for word in encryptString.split():
		word = normalize(word)
		if word in bywords:
			num = bywords[word]
			num = (num+(b/2))%b
		else:
			listWithSameStart = [x for x in justwords if x.startswith(word[0])]
			top = 0
			for l in listWithSameStart:
				fuzzRatio =  fuzz.ratio(word, l)
				if fuzzRatio > top:
					top=fuzzRatio
					ok = l
					num = bywords[ok]
			num = (num+(b/2))%b
		encrypted = encrypted + byindex[num] + " "
	return encrypted

def decrypt(encryptString,bywords,byindex,justwords,b):
	decrypted = ""
	for word in encryptString.split():
		word = normalize(word)
		num = bywords[word]
		num = (num+(b/2))%b
		decrypted =decrypted + byindex[num] + " "
	return decrypted
			
def main():
	bywords = {}
	byindex = {}
	justwords = []
	with open("web2.txt","r") as dic:
		for i,word in enumerate(dic):
			if len(word) >= 2:
				word = normalize(word)
				word = word.strip()
				byindex[i] = word
				bywords[word] = i
				justwords.append(word)
		
	b = len(byindex)
	
	p = "I am a dog with three legs"
	a = encrypt(p,bywords,byindex,justwords,b)
	print a
	print decrypt(a,bywords,byindex,justwords,b)
	return 0

if __name__ == '__main__':
	main()

