# pew in st-venv python ~/Workspace/Python/Datasets/Annotator/annotator/example.py

from annotator.annot import *

data = \
[
	{"author": "John", "text": "This is the first document." + " X" * 300},
	{"author": "Henry", "text": "The second doc." + " Y" * 30},
	{"author": "Roger", "text": "The third doc." + " Y" * 30},
]

def dataGenerator():
	"""
		Define a function which will yield all documents as dicts with `id` (must be unique) and `content` which will contain the data you want to display. The `content` field can be a list to have mulitple columns in the UI.
	"""
	for current in data:
		author = current["author"]
		text = current["text"]
		yield {"id": author, "content": {"title": author, "text": text}}

if __name__ == "__main__":
	# Labels:
	labels = \
	{
		"relevance": {"title": "Relevance", "type": LABEL_TYPE.scale, "from": 0, "to": 100, "resolution": 10, "default": 50},
		"weight": {"title": "Weight", "type": LABEL_TYPE.scale, "default": 0.2},
		"format": {"title": "The document is well formed", "type": LABEL_TYPE.checkbutton, "default": True},
		"popular": {"title": "The author is popular", "shorttitle": "Popular author", "type": LABEL_TYPE.checkbutton},
	}
	
	# We init the Annotator. The first argument is the name of the file or the name of the mongo collection. Here we store all annotations in a pickle file but you can also use mongodb if you set host, user, and password:
	an = Annotator("my-annotations", labels, useMongodb=True, dirPath="/home/hayj/tmp")
	an.reset()
	# Here we start the UI, so you will have one data on the left and labels to manually edit on the right. You can click the right arrow to switch to the next data, or return to the previous.
	an.start(dataGenerator())