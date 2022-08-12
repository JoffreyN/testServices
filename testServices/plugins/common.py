import sys,os,hashlib,logging,json,hmac,time,operator,random

def getHKid():
	hk_id=int(random.random()*26+1)
	sums=hk_id*8
	hk_id=chr(hk_id+64)
	for i in range(1,7):
		s=round(random.random()*9)
		sums=sums+s*(8-i)
		hk_id=f'{hk_id}{s}'
	return f'{hk_id}{11-(sums%11)}'

def saveCookie(cookie,file):
	sys.path.append('..')
	cookiePath=f'testServices/cookie/'
	if not os.path.exists(cookiePath):os.makedirs(cookiePath)
	with open(f'{cookiePath}/{file}','w',encoding='utf-8') as f:
		f.write(cookie)

def readCookie(file):
	sys.path.append('..')
	cookiePath=f'testServices/cookie/'
	try:
		return open(f'{cookiePath}{file}').read().strip()
	except:
		logging.info(f'读取cookie文件失败: {file}')
		return '0'

def encode_md5(string):
	md5=hashlib.md5()
	md5.update(string.encode(encoding='utf-8'))
	return md5.hexdigest()

def saveFile(strs,out=1):
	if out:logging.info(strs)
	try:
		with open('regFile.txt','a',encoding='utf-8') as f:
			f.write(f'{strs.strip()}\n')
	except FileNotFoundError:
		pass

def encryption(jsonData,keyType='APP'):
	keyDict={'APP':'FE1C95D745DA78CK','H5':'C35730AD927732F6'}
	timestamp=str(int(1000*time.time()))
	jsonData=dict(sorted(jsonData.items(),key=operator.itemgetter(0),reverse=False))# 排序
	msg=json.dumps(jsonData).replace(" ","")+timestamp
	signature=hmac.new(keyDict[keyType].encode('utf-8'),msg.encode('utf-8'),hashlib.md5).hexdigest()
	return timestamp,signature

class Args():
	def __init__(self):
		pass


########################################### FTP 相关 Start #######################################################
import posixpath
from ftplib import error_perm, FTP

def ftp_delete_file(ftpObj,pathTofile):
	try:
		ftpObj.delete(pathTofile)
	except error_perm as e:
		if 'No such file or directory' not in str(e):
			raise e

def ftp_makedirs_cwd(ftpObj, path, first_call=True):
	"""
	设置“FTP”中给出的FTP连接的当前目录
	参数(如ftplib)。)，不存在创建所有父目录
	ftplib对象必须已经连接并登录
	"""
	try:
		ftpObj.cwd(path)
	except error_perm:
		ftp_makedirs_cwd(ftpObj,posixpath.dirname(path),False)
		ftpObj.mkd(path)
		if first_call:ftpObj.cwd(path)

def ftp_store_file(localFile,remotePath,host='192.168.99.123',port=21,username='invoice',password='******',use_active_mode=False):
	logging.info(f'上传文件 {localFile} 至 {remotePath}')
	with open(localFile,'rb') as fileObj:
		with FTP() as ftp:
			ftp.connect(host,port)
			ftp.login(username,password)
			if use_active_mode:ftp.set_pasv(False)
			ftp_delete_file(ftp,remotePath)# 删除已有的
			dirname,filename = posixpath.split(remotePath)
			ftp_makedirs_cwd(ftp,dirname)
			ftp.storbinary('STOR %s' % filename,fileObj)
	logging.info(f'上传成功')

########################################### FTP 相关 Stop #######################################################
if __name__ == '__main__':
	print(encryption({'areaCode': '86', 'codeType': 'normal', 'lang': 'cn', 'mobile': '15654513026', 'signatureApp': True, 'traceLogId': 'fromTestServices1644384847.7728078'}))