'''
Created on 2013-05-21

@author: Dallas
'''
from flask import Flask

app = Flask(__name__)
app.config.from_object('config')


from sanway import views