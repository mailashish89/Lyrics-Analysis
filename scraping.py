import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

df = pd.DataFrame(columns=["Movie", "Released on", "URL", "Word", "Count"])

movie_url_list = []
alphabets = [chr(i) for i in range(ord('a'), ord('z') + 1)] + [""]
for alphabet in alphabets:
    alphabetical_page = requests.get("https://www.lyricsbogie.com/category/movies/%s" % (alphabet))
    soup = BeautifulSoup(alphabetical_page.content)
    for movie in soup.find_all("ul", {"class": "cat_list"}):
        for link in movie.find_all("a"):
            movie_url_list = movie_url_list + [link.get("href")]
print(len(movie_url_list))

song_url_list = []
for movie_url in movie_url_list:
    movie_page = requests.get(movie_url)
    soup = BeautifulSoup(movie_page.content)
    for song_list in soup.find_all("ul", {"class": "song_list"}):
        for song in song_list.find_all("h3", {"class": "entry-title"}):
            for link in song.find_all("a"):
                song_url_list = song_url_list + [link.get("href")]

print(len(song_url_list))
pd.DataFrame(song_url_list).to_csv('song_url_list.txt', sep='\t', header=False, index=False, mode="a")

with open('song_url_list.txt') as f:
    song_url_list_load = set(f.read().splitlines())
print(len(song_url_list_load))

c=0  #Songs count that gave response code 200
for url in song_url_list_load:
    url_page = requests.get(url)
    if url_page.status_code==200:
        c=c+1
    soup = BeautifulSoup(url_page.content)
    color_words = []
    for lyrics in soup.find_all("div", {"id": "lyricsDiv"}):
        #color_words = re.findall(r"Gor[iae].*?\b", lyrics.text, re.IGNORECASE)
        color_words = color_words + re.findall(r"Sa+n[wv]al.*?\b", lyrics.text, re.IGNORECASE)  # Look for words Saanwale or Saanware, Sanvali, etc.
    if len(color_words) == 0:
        pass
    else:
        color_words = [x.lower() for x in color_words]
        word_count = {i: color_words.count(i) for i in color_words}
        song = []
        for info in soup.find_all("span", {"class": "title"}):
            if re.search("Movie", info.text):
                movie = info.find_next("a").text
                song.insert(0, movie)
            elif re.search("Release on", info.text):
                release_date = info.find_parent("p").text.replace("Release on: ", "")
                song.insert(1, re.search("\d\d\d\d", release_date).group())
            else:
                pass
        if len(song) == 1:
            song.insert(1, re.search("(?<=[(]).*(?=[)])", song[0]).group(0))  # Finds the year from the movie Title
        song.insert(2, url)
        print(song)

        df = pd.DataFrame(columns=["Movie", "Released on", "URL", "Word", "Count"])
        for k, v in word_count.items():
            song.append(k)
            song.append(v)
            df = df.append(pd.Series(song, index=["Movie", "Released on", "URL", "Word", "Count"]), ignore_index=True)
            song.pop()
            song.pop()
        df.to_csv('lyrics_result.txt', sep='\t', header=False, index=False, mode="a")
    print(c)

# df.to_csv('lyrics_result.txt', sep='\t', index=False, mode="a")
