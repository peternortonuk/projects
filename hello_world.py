import os
import sys
from pprint import pprint as pp

print(os.getcwd())
pp(sys.path)
paths = ['C:\\dev\\code\\projects\\pytube\\pytube', 'C:\\dev\\code\\projects\\pytube\\pytube\\contrib']
sys.path.extend(paths)
pp(sys.path)

os.chdir(r'C:\dev\code\projects\pytube')
from pytube import YouTube

url = r'https://www.youtube.com/watch?v=xZAfdgYnsZc&list=PLYf3-nc0C5ly-2-7WU6S2nCW7MMT0VM87&index=2'
yt = YouTube(url)
print(yt.description)
