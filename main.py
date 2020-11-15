from flask import stream_with_context, Flask, Response, render_template, redirect, url_for, request
import requests, re
from bs4 import BeautifulSoup
from werkzeug.datastructures import Headers

def removeComment(element):
  if('#' in element):
    return False
  else:
    return True

app = Flask(__name__)

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/', methods=['POST'])
def home_post():
  url = request.form['url']
  if "live.rbg.tum.de" in url:
    return redirect(url_for("download", videoUrl = url))
  else:
    return redirect(url_for("home"))


@app.route('/<path:videoUrl>')
def download(videoUrl):

  def generateChunks(siteUrl):

    siteHTML = requests.get(siteUrl).content
    soup = BeautifulSoup(siteHTML, 'html.parser')

    playlistUrl = ""

    for i in soup.find_all('script'):
      if "MMstartVideos" in str(i):
        playlistUrl = re.search("(?P<url>https?://[^\s']+)", str(i)).group("url")

    masterUrl = playlistUrl.replace(playlistUrl.split("/")[-1], "")
    playlist = requests.get(playlistUrl).content.splitlines()[-1].decode("utf-8")

    chunklist = requests.get(masterUrl+playlist).content.decode("utf-8").splitlines()
    chunklist = filter(removeComment, chunklist)

    for chunk in chunklist:
      url = masterUrl + chunk
      yield requests.get(url).content

  d = Headers()
  d.add('Content-Type', "video/mp4")
  d.add('Content-Disposition', 'attachment', filename='video.mp4')
  return Response(stream_with_context(generateChunks(videoUrl)),mimetype="video/mp4",headers=d)


if __name__ == "__main__":
  app.run()
