#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 22:33:46 2020

@author: stasianik
"""
#import gpt_2_simple as gpt2
from big_phoney import BigPhoney
import lyricsgenius as genius
import random
import nlpaug.augmenter.word as naw
#from nlpaug.util import Action
import re
#import keras.backend.tensorflow_backend as tb
#tb._SYMBOLIC_SCOPE.value = True
#----------------For future live text generation-----------------
# model_name = "124M"
# model is saved into current directory under /models/124M/
# gpt2.download_gpt2(model_name=model_name) #need to run only once. comment out once done.

# Load models
#sess = gpt2.start_tf_sess()
#gpt2.load_gpt2(sess, run_name='run1')

#Load text augmentation model
#aug = naw.ContextualWordEmbsAug(
#    model_path='bert-base-uncased', action="insert")
#----------------------------------------------------------------

def get_target_lyrics(artist, title):
    
    api_key = 'Nc3VjqRNlEZiD9mqOQATDQ5PuZ4IjdgV13n7c39OIyNwsjuazZThQlQkdr_Hts4c'
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
    #create list of lines
    target_lyrics = target.split("\n")
    #print("Target lyrics:")
    #print(target_lyrics)
    return target_lyrics

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

def lyrics_to_list(file_name):
    with open(file_name, 'r') as file:
        data = file.read().split("====================")
        random_song = random.choice(data)
        gen_lyrics = random_song.split("\n")
        gen_lyrics = gen_lyrics[1:-1]
#    print(gen_lyrics)
    return gen_lyrics

#This function uses the count_syls function above to keep track of num of syllables in each line
def fit_lyrics(gen_lyrics, target_lyrics):
    print(gen_lyrics)
    aug = naw.ContextualWordEmbsAug(model_path='bert-base-uncased', action="insert")
    print('aug')
    phoney = BigPhoney()
    print('initialized phoney')
    def count_syls(text):
    
        schema = []
    
        for line in text:
            syls = phoney.count_syllables(line)
            schema.append(syls)
            #print(syls,line)
        
        return schema
    
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
        return phrase
    
    gen_schema = count_syls(gen_lyrics)
    target_schema = count_syls(target_lyrics)
#    print(target_schema)
    #make generated lyrics same length as target lyrics
    target_len = len(target_schema)
    del gen_schema[target_len:]
    del gen_lyrics[target_len:]
    new_lyrics = []
#    loop = 1
    for num, line in enumerate(gen_lyrics):
        
        if (gen_schema[num] == target_schema[num]): 
            new_lyrics.append(line)
        elif (gen_schema[num] != target_schema[num]):
            syls = gen_schema[num]
            track = 0
            while syls != target_schema[num]:
                #while syls don't match the target
                #make syls the next syls 
                #if we're at the end then stop 
                if track == len(gen_schema)-1:
                    end = True
                    break
                else:
                    track = track + 1
                    syls = gen_schema[track]
                    line = gen_lyrics[track]
                    end = False
            if end == False:
                new_lyrics.append(line)
            #If we can't find a line that's the right size
            if end:
                line = decontracted(line)
#                print("No matching line")
                #print(line)
                while syls < target_schema[num]:
#                    print("not enough syls")
                    original_line = line
                    line = aug.augment(line)
#                    print(line)
                    syls = phoney.count_syllables(line)
                #In case we overshoot (add too many syllables)
                    if syls > target_schema[num]:
                        #print("Oops we overshot")
                        line = original_line
                        syls = phoney.count_syllables(line)
                new_line = line
#                print("the same line:")
#                print(line)
                syls = gen_schema[num]
                words = line.split(" ")
                while syls > target_schema[num]:
#                    print("too many syls")
                    del words[-1]
                    new_line = ' '.join(words)
                    syls = phoney.count_syllables(new_line)
                    #In case too many syllables are deleted
                    if syls < target_schema[num]:
                        #print("Oops, deleted too many")
                        new_line = aug.augment(new_line)
                        syls = phoney.count_syllables(new_line)
                new_lyrics.append(new_line)
    return new_lyrics
