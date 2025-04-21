import gdown

# URL of the Google Drive file
url = "https://drive.google.com/uc?export=download&id=1lrgt9ijt0ocmY-q2Cga-GYJZh9Q4miLE"

# Download the file directly
gdown.download(url, quiet=False)