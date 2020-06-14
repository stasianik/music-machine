from flask import render_template
from flask import request
from flaskexample import app
#from sqlalchemy import create_engine
#from sqlalchemy_utils import database_exists, create_database
#import pandas as pd
#import psycopg2
import gpt_2_simple as gpt2

# Python code to connect to Postgres
# You may need to modify this based on your OS, 
# as detailed in the postgres dev setup materials.
#user = 'stasianik' #add your Postgres username here      
#host = 'localhost'
#dbname = 'birth_db'
#db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
#con = None
#con = psycopg2.connect(database = dbname, user = user)

# Load in model checkpoint and start a tensorflow session
#sess = gpt2.start_tf_sess()
#gpt2.load_gpt2(sess, run_name='run1')

@app.route('/')
@app.route('/index')
def index():
   return render_template("index.html",
      title = 'Home'
      )
           
@app.route('/input')
def lyrics_input():
   return render_template("input.html")

@app.route('/output')
def lyrics_output():

    prefix = request.args.get('lyrics_topic')
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, run_name='run1')
    
    generated_text = gpt2.generate(sess, 
                     length=250,
                     temperature=0.9,
                     prefix=prefix,
                     nsamples=1,
                     batch_size=1,
                     return_as_list=True)[0]
    
    return generated_text
