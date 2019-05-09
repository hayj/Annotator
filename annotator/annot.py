
# pew in st-venv python ~/Workspace/Python/Datasets/Annotator/annotator/annot.py

from systemtools.basics import *
from datatools.dataencryptor import *
try:
	from systemtools.hayj import *
	from tkinter import Tk
	from annotator.ui import *
except: pass
from datastructuretools.hashmap import *

class Annotator:
	def __init__\
	(
		self,
		identifier,
		labels=None,
		dirPath=None,
		taskDescription=None,
		useMongodb=True,
		logger=None,
		verbose=True,
		host=None,
		user=None,
		password=None,
		mongoDbName=None,
		databaseRoot=None,
	):
		"""
			The generator must throw dict looking:
			{id: "a", "text": "Something to print...",
			"firstLabel": int, "secondLabel": bool}

			If id is None, hash(<text>) will be used.

			text can be a list

			TODO make scales default as None to be able to disable the value if the user doesn't know what to label...

		"""
		self.dirPath = dirPath
		self.taskDescription = taskDescription
		self.logger = logger
		self.verbose = verbose
		self.identifier = identifier
		self.generator = None
		self.labels = labels
		if self.labels is not None:
			self.labels = sortByKey(labels)
		self.useMongodb = useMongodb
		self.annotatorUI = None
		self.host = host
		self.user = user
		self.password = password
		self.mongoDbName = mongoDbName
		self.validityFuncts = dict()
		self.ids = []
		self.index = None
		self.databaseRoot = databaseRoot
		if self.useMongodb and self.host is None and self.user is None and self.password is None and self.mongoDbName is None:
			try:
				(self.user, self.password, self.host) = getAnnotatorMongoAuth(logger=self.logger)
				self.mongoDbName = "annotator"
				self.databaseRoot = "annotator"
			except Exception as e:
				logException(e, self)
				logError("A local storage of labels will be used.", self)
				self.useMongodb = False
		self.data = SerializableDict\
		(
			name=self.identifier,
			dirPath=self.dirPath,
			useMongodb=self.useMongodb,
			logger=self.logger,
			verbose=self.verbose,
			serializeEachNAction=1,
			host=self.host, user=self.user, password=self.password,
			useLocalhostIfRemoteUnreachable=False,
			mongoDbName=self.mongoDbName,
			mongoIndex="id",
			databaseRoot=self.databaseRoot,
		)


	def __len__(self):
		return self.size()
	def size(self):
		return len(self.data)

	def getData(self):
		return self.data

	def getAlreadySeen(self):
		return self.data.keys()

	def startUI(self):
		root = Tk()
		root.geometry("1200x800") #+600+100
		self.annotatorUI = AnnotatorUI(rightCallback=self.next, leftCallback=self.previous, logger=self.logger, verbose=self.verbose, taskDescription=self.taskDescription)
		self.annotatorUI.right()
		root.mainloop()

	def start(self, generator):
		self.generator = threadGen(generator, maxsize=100,
			logger=self.logger, verbose=self.verbose)
		self.startUI()

	def reset(self):
		self.data.reset()
	def clean(self):
		self.reset()



	def previous(self):
		self.update(-1)
	def next(self):
		self.update(+1)
	def update(self, inc):
		# If there is no element already displayed:
		if self.index is not None:
			# We get all labels:
			toInsert = self.annotatorUI.getLabelsValues()
			currentId = self.ids[self.index]
			content = self.currentContent
			toInsert["content"] = content
			# We update it:
			self.data[currentId] = toInsert
		# Finally we load the new content:
		if self.index is None:
			newIndex = 0
		else:
			newIndex = self.index + inc
		if newIndex >= 0:
			newContent, newLabels = None, None
			# We get new values from the generator:
			if self.index is None or newIndex == len(self.ids):
				try:
					# We get data:
					newElement = next(self.generator)
					newContent = newElement["content"]
					theNewId = newElement["id"]
					newLabels = self.labels
					# We update ids:
					self.ids.append(theNewId)
					# We update the index:
					self.index = newIndex
				except StopIteration as e:
					log("End of content", self)
					pass # TODO display a message in a status bar ???
				except Exception as e:
					logException(e, self)
			# Else we reload the already displayed element:
			else:
				theNewId = self.ids[newIndex]
				(newContent, newLabels) = self.getElementAndLabelsById(theNewId)
				# We update the index:
				self.index = newIndex
			if newLabels is not None:
				# We update the UI:
				self.annotatorUI.initLabelFrame(newLabels)
				self.annotatorUI.initTextFrame(newContent)
				# We update the current content:
				self.currentContent = newContent

	def getElementAndLabelsById(self, id):
		if self.data.has(id):
			# We get the data:
			data = self.data[id]
			# We load already set labels:
			labels = dict()
			for labelId, value in data.items():
				if labelId in self.labels:
					labels[labelId] = self.labels[labelId]
					labels[labelId]["default"] = value
			# We add all other labels not yet set:
			for labelId, value in self.labels.items():
				if labelId not in labels:
					labels[labelId] = self.labels[labelId]
			return (data["content"], sortByKey(labels))
		else:
			logError(id + " not found!", self)
		

	# TODO tester sur mongo student
	# TODO tester sur fichier
	# tester les cleans

def dataGenerator():
	for current in \
	[
		{
			"id": "a",
			"content": \
			[
				{"text": "aaa " * 10000},
				{"title": "Système B", "text": "a " * 1000},
			],
		},
		{
			"id": "b",
			"content": \
			[
				{"text": "bbb " * 10000},
				{"title": "Système B", "text": "b " * 1000},
			],
		},
		{
			"id": "c",
			"content": \
			[
				{"text": "ccc " * 10000},
				{"title": "Système B", "text": "c " * 1000},
			],
		},
	]:
		yield current


if __name__ == "__main__":

	labels = \
	{
		"a": {"title": "test1", "type": LABEL_TYPE.scale, "from": 0.2},
		"b": {"title": "test2", "type": LABEL_TYPE.scale, "default": 0.2},
		"c": {"title": "test3", "type": LABEL_TYPE.scale},
		"d": {"title": "test4", "type": LABEL_TYPE.scale},
		"e": {"title": "They are the same source", "type": LABEL_TYPE.checkbutton},
		"f": {"title": "They are the samethe samethe same source same source", "text": "Same", "type": LABEL_TYPE.checkbutton, "default": True},
	}

	an = Annotator("test", dataGenerator(), labels, taskDescription="aaaa")
	print("a")
	an.reset()
	an.start()