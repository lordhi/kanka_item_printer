import kanka
import os
import shutil
import hashlib
import pdfkit

def readTemplate(filename='template.html'):
	with open(filename) as file:
		return ''.join(file.readlines())

template = readTemplate()

def makeDirIfNotExist(path):
	if not os.path.exists(path):
		os.makedirs(path)

def makeDirectories():
	makeDirIfNotExist('tmp')
	makeDirIfNotExist('tmp/html')
	makeDirIfNotExist('tmp/pdf')
	makeDirIfNotExist('data')

def convertToPdf(src, dest):
	pdfkit.from_file(src, dest)

def cleanup():
	os.system('rm -r tmp/pdf')

def descriptionLengthToSize(description):
	length = len(description)
	if length < 600:
		return 40
	if length < 900:
		return 50
	if length < 1200:
		return 60
	else:
		return 80

def fillTemplate(item, template):
	size = descriptionLengthToSize(item['description'])

	filled = template.replace('{$size}', str(size)) \
					.replace('{$name}', item['name']) \
					.replace('{$type}', item['type']) \
					.replace('{$description}', item['description'])	

	return filled

def saveStringToFile(string, filename):
	with open(filename, 'w+') as file:
		file.write(string)

def makePdfsForItems(items):
	for item in items:
		itemToPdf(item)

def checkHash(itemWithId):
	idNum, item = itemWithId

	filename = 'data/' + str(idNum)

	m = hashlib.sha256()
	m.update(item.encode())
	newHash = m.hexdigest()

	if os.path.exists(filename):
		with open(filename) as file:
			oldHash = file.readline().strip()
			if oldHash == newHash:
				return False

	with open(filename, 'w') as file:
		file.write(newHash)
		return True

def getHtmlFilePath(idNum):
	return 'tmp/html/' + str(idNum) + '.html'

def printItems(items, shouldPrint= lambda x: true):
	itemStringsWithId = [(item['id'], fillTemplate(item, template)) for item in items]
	itemsToPrint = list(filter(shouldPrint, itemStringsWithId))

	[saveStringToFile(item[1], getHtmlFilePath(item[0])) for item in itemsToPrint]
	[convertToPdf(getHtmlFilePath(item[0]), 'tmp/pdf/' + str(item[0]) + '.pdf') for item in itemsToPrint]
	os.system("lp tmp/pdf/*.pdf")

def main():
	cleanup()
	makeDirectories()

	items = kanka.getCleanItemsForActiveMembers()
	printItems(items, checkHash)

if __name__ == '__main__':
	main()
