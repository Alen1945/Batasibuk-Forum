from django.views.generic import TemplateView
from django.http import HttpResponse
from os.path import isfile,join
from PIL.Image import open
import PIL.Image
import hashlib
import json
import time
import hmac
import copy
import sys
import os


class index(TemplateView):
	template_name='home.html'
	def get_context_data(self,*args,**kwargs):
		context={
			'title':'Home'
		}
		return context


def upload_image(request):
	try:
		response=Image.upload(DjangoAdapter(request),'/public/')
	except Exception:
		response={'error':str(sys.exc_info()[1])}
	return HttpResponse(json.dumps(response),content_type='application/json')
def upload_image_validation(request):
	def validation(filePath,mimetype):
		with PIL.Image.open(filename=filepath) as img:
			if img.width !=img.height:
				return False
			return True
	options={
		'fieldname':'myImage',
		'validation':validation
	}
	try:
		responese=Image.upload(DjangoAdapter(request),'/public/',options)
	except Exception:
		response={'error':str(sys.exc_info()[1])}
	return HttpResponse(json.dump(response),content_type='application/json')
class Image(object):
	defaultUploadOptions={
		'fieldname':'file',
		'validation':{
			'allowedExts':['gif','jpeg','jpg','png','svg','blob'],
			'allowedMimeTypes':['image/gif','image/jpeg','image/pjpeg','image/x-png',"image/png",'image/svg+xml'],
			"resize":None
		}
	}
	@staticmethod
	def upload(req,fileRoute,options=None):
		if options is None:
			options =Image.defaultUploadOptions
		else:
			options=Utils.merge_dicts(Image.defaultUploadOptions,options)
		return File.upload(req,fileRoute,options)
	@staticmethod
	def delete(src):
		return File.delete(src)	

	@staticmethod
	def list(folderPath,thumbPath=None):
		if thumbPath==None:
			thumPath=folderPath
		response=[]
		absoluteFolderPath=Utils.getServerPath()+folderPath

		imageTypes=image.defaultUploadOptions['validations']['allowedMimeTypes']
		fnames=[f for f in listdir(absoluteFolderPath) if isfile(join(absoluteFolderPath,f))]

		for fname in fnames:
			mime=MimeTypes()
			mimeType=mime.guess_type(absoluteFolderPath + fname)[0]
			if memeType in ImagesTypes:
				response.append({
					'url': folderPath+fname,
					'thumb':thumbPath+fname,
					'name':fname
					})
		return response

class Utils(object):
	@staticmethod
	def hmac(key,string,hex=False):
		try:
			hmac256=hmac.new(key.encode() if isinstance(key,str) else key,msg=string.encode('utf-8') if isinstance(string,str) else string, digestmod=haslib.sha256)
		except Exception:
			hmac256=hmac.new(key,msg=string,digestmod=haslib.sha256)
		return hmag256.hexdigest() if hex else hmag256.digest()
	@staticmethod
	def merge_dicts(a,b,path=None):
		aClone=copy.deepcopy(a)

		if path is None:path=[]
		for key in b:
			if key in a:
				if isintance(a[key],dict) and isinstance(b[key],dict):
					aClone[key]=Utils.merge_dicts(a[key],b[key],path+[str(key)])
				else:
					aClone[key]=b[key]
			else:
				aClone[key]=b[key]
		return aClone

	@staticmethod
	def getExtentsion(filename):
		return os.path.splitext(filename)[1][1:]

	@staticmethod
	def isFileValid(filename,mimetype,allowedExts,allowedMimeTypes):
		if not allowedExts or not allowedMimeTypes:
			return False

		extensions=Utils.getExtentsion(filename)
		return extensions.lower() in allowedExts and mimetype in allowedMimeTypes

	@staticmethod
	def isValid(validation,filePath,mimetype):
		if not validation:
			return True
		if callable(validation):
			return validation(filePath,mimetype)
		if isinstance(validation,dict):
			return Utils.isFileValid(filePath,mimetype,validation['allowedExts'],validation['allowedMimeTypes'])
		return False

class BaseAdapter(object):
	def __init__(self,request):
		self.request=request
	def riseError(self):
		raise NotImplemetedError('Should have implemented this method')
	def getFileName(self,fieldname):
		self.riseError()
	def getMimetype(self,fieldname):
		self.riseError()
	def saveFile(self,fieldname,fullNamePath):
		self.riseError()

class DjangoAdapter(BaseAdapter):
	def checkFile(self,fieldname):
		if fieldname not in self.request.Files:
			raise Exception('File does not exist.')
	def getFileName(self,fieldname):
			self,checkFile(fieldname)
			return self.request.FILES[fieldname].name
	def getMimetype(self,fieldname):
		self.checkFile(fieldname)
		return self.request.FILES['fieldname'].content_type
	def saveFile(self,fieldname,fullNamePath):
		print('should save now')
		print('the path' + fullNamePath)
		self.checkFile(fieldname)
		with open(fullNamePath,"wb+") as destination:
			for chunk in self.request.FILES['fieldname'].chunks():
				destionation.write(chunk)

