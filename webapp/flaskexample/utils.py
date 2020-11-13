#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 22:33:46 2020

@author: stasianik
"""

from big_phoney import BigPhoney
import lyricsgenius as genius
import random
import nlpaug.augmenter.word as naw
import re

#----------------For future live text generation-----------------
#import gpt_2_simple as gpt2

# model_name = "124M"
# model is saved into current directory under /models/124M/
# gpt2.download_gpt2(model_name=model_name) #need to run only once. comment out once done.

# Load models
#sess = gpt2.start_tf_sess()
#gpt2.load_gpt2(sess, run_name='run1')

#----------------------------------------------------------------

def get_target_lyrics(artist, title, api_key):
    
    #api_key = 'YOUR_API_KEY_HERE'
    api = genius.Genius(api_key)
    api.remove_section_headers = True # Removes section headers like "Verse" and "Intro"
    
    #get song lyrics
    song = api.search_song(artist, title)
    
    #clean up the target lyrics
    target = song.lyrics
    target = target.replace("\u2005"," ")
    target = target.replace("\\"," ")
    target = target.replace("\\n"," ")
    target = target.replace("("," ")
    target = target.replace(")"," ")
    target = target.replace("\n\n","\n")
    target = target.replace("\n\n\n","\n")
    target = target.replace("2x","")
    
    target_lyrics = target.split("\n")
    return target_lyrics

#----------------For future live text generation-----------------
#def generate_lyrics(): 
#    
#    gen_lyrics = gpt2.generate(sess, 
#                     length=250,
#                     temperature=0.9,
#                     include_prefix=False,
#                     #prefix="Deep in the night",
#                     nsamples=1,
#                     batch_size=1,
#                     return_as_list=True)[0]
#    
#    gen_lyrics = gen_lyrics.split("\n")
#    
#    return gen_lyrics
#----------------------------------------------------------------

def lyrics_to_list(file_name):
    with open(file_name, 'r') as file:
        data = file.read().split("====================")
        random_song = random.choice(data)
        target = random_song
        
        # clean generatedd lyrics
        target = target.replace("\u2005"," ")
        target = target.replace("\\"," ")
        target = target.replace("\\n"," ")
        target = target.replace("("," ")
        target = target.replace(")"," ")
        target = target.replace("\n\n","\n")
        target = target.replace("\n\n\n","\n")
        target = target.replace("2x","")
        gen_lyrics = target.split("\n")
        gen_lyrics = gen_lyrics[1:-1]

    return gen_lyrics

def fit_lyrics(gen_lyrics, target_lyrics):
    
    print(gen_lyrics)
    
    aug = naw.ContextualWordEmbsAug(model_path='bert-base-uncased', action="insert")
    print('aug')
    
    phoney = BigPhoney()
    print('initialized phoney')
    
    # Counts the number of syllables in each line
    def count_syls(text):
    
        schema = []
    
        for line in text:
            syls = phoney.count_syllables(line)
            schema.append(syls)
            #print(syls,line)
        
        return schema
    
    # Remove special characters and contractions from the line. This will make it easier to
    # augment lines that need augmentation. 
    def decontracted(phrase):
        # specific
        phrase = re.sub(r"won\'t", "will not", phrase)
        phrase = re.sub(r"can\'t", "can not", phrase)

        # general
        phrase = re.sub(r"n\'t", " not", phrase)
        phrase = re.sub(r"\'re", " are", phrase)
        phrase = re.sub(r"\'s", " is", phrase)
        phrase = re.sub(r"\'d", " would", phrase)
        phrase = re.sub(r"\'ll", " will", phrase)
        phrase = re.sub(r"\'t", " not", phrase)
        phrase = re.sub(r"\'ve", " have", phrase)
        phrase = re.sub(r"\'m", " am", phrase)
        phrase = re.sub('[!@#$?]', '', phrase)
        return phrase
    
    # Count the number of syllables in the generated and target texts.
    gen_schema = count_syls(gen_lyrics)
    target_schema = count_syls(target_lyrics)
#    print(target_schema)

    # make generated lyrics same length as target lyrics
    #target_len = len(target_schema)
    #del gen_schema[target_len:]
    #del gen_lyrics[target_len:]
    
    # initialize array for the new fitted lyrics
    new_lyrics = []
    
    # loop through each line and either find existing line to place into the current position, 
    # or augment the current line. 

    for num, line in enumerate(gen_lyrics):
        print("line in gen_lyrics:")
        print(line)

        # if the line is already the right length, add it to the new lyrics. 
        if (gen_schema[num] == target_schema[num]): 
            new_lyrics.append(line)
            print("this line is good:")
            print(line)
        # if the line is not the right length, augment or delete
        elif (gen_schema[num] != target_schema[num]):
            line = decontracted(line)
            print("target syls:")
            print(target_schema[num])
            print("same line decontracted:")
            print(line)
            syls = gen_schema[num]
            # If we start with fewer syllables than we want, we augment. 
            while syls < target_schema[num]:
                print("not enough syls")
                original_line = line
                line = aug.augment(line)
                line = re.sub(r'[^\w\s]','',line)
                print(line)
                syls = phoney.count_syllables(line)
            #In case we overshoot (add too many syllables)
                if syls > target_schema[num]:
                    print("Oops we overshot")
                    print(line)
                    line = original_line
                    syls = phoney.count_syllables(line)
            new_line = line
#                print("the same line:")
            syls = gen_schema[num]
            words = line.split(" ")
            while syls > target_schema[num]:
                print("too many syls")
                original_words = words
                #instead of deleting the last word, try deleting a word randomly
                #del words[-1]
                words.pop(random.randrange(len(words))) 
                new_line = ' '.join(words)
                syls = phoney.count_syllables(new_line)
                print("after removing one:")
                print(new_line)
                #In case too many syllables are deleted
                if syls < target_schema[num]:
                    print("Oops, deleted too many")
                    print(line)
                    words = original_words
                    new_line = ' '.join(words)
                    syls = phoney.count_syllables(new_line)
                    print(syls)
                    print("the target was:")
                    print(target_schema[num])
                        
            new_lyrics.append(new_line)
                
    return new_lyrics


