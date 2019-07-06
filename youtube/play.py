from pytube import YouTube
from playlist import urls

for url in urls:
    yt = YouTube(url)
    x = yt.streams.filter(progressive=True).first().download()
    pass