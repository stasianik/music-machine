from flask import render_template, request, Markup
from flaskexample import app
from flaskexample.utils import lyrics_to_list, get_target_lyrics, fit_lyrics
from collections import deque

################### For future live GPT2 integration #########################
#import gpt_2_simple as gpt2
# Load in model checkpoint and start a tensorflow session
#sess = gpt2.start_tf_sess()
#gpt2.load_gpt2(sess, run_name='run1')
##############################################################################

@app.route('/')
@app.route('/index')
def index():
   return render_template("input2.html",
      title = 'Home'
      )

@app.route('/output')
def lyrics_output():
    artist = request.args.get('artist')
    title = request.args.get('title')
    
    #get api key
    lines = open('API.txt').readlines()
    api_key = lines[0].strip()
    
    target_lyrics = get_target_lyrics(artist, title, api_key)
    
    band = request.args.get('radioValue')
    #connect to button 
    if band == 'option1':
        file_name = 'gpt2_gentext_Bjork.txt'
    elif band == 'option2':
        file_name = 'gpt2_gentext_META.txt'
    elif band == 'option3':
        file_name = 'gpt2_gentext_IM.txt'
    
    gen_lyrics = lyrics_to_list(file_name)
    print('lyrics retrieved')
    
    new_lyrics = fit_lyrics(gen_lyrics, target_lyrics) 
    
    new_lyrics = deque(new_lyrics)
    new_lyrics.appendleft('New Lyrics:')
    lyrics1 = '<br>\n'.join(new_lyrics)
    
    target_lyrics = deque(target_lyrics)
    target_lyrics.appendleft('Target Lyrics:')
    lyrics2 = '<br>\n'.join(target_lyrics)
    
    combined = "<table><tr><td style='vertical-align:top; padding-right:20px'>" + lyrics1 + "</td><td style='vertical-align:top'>" + lyrics2 + '</td></tr></table>' 

################## For future live GPT2 integration ###########################
#    prefix = request.args.get('lyrics_topic')
#    sess = gpt2.start_tf_sess()
#    gpt2.load_gpt2(sess, run_name='run1')
#    
#    generated_text = gpt2.generate(sess, 
#                     length=250,
#                     temperature=0.9,
#                     prefix=prefix,
#                     nsamples=1,
#                     batch_size=1,
#                     return_as_list=True)[0]
###############################################################################
    
    return Markup(combined)
