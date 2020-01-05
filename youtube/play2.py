from youtube.playlist import urls
from pytube import YouTube

youtubes = []
for url in urls:
    yt = YouTube(url)
    youtubes.append(yt)

print(yt.description)

