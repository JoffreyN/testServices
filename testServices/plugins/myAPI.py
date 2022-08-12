import requests,time,simplejson,logging,traceback,json
from jsonpath import jsonpath
from .database import excuteSQL,del_pwdHistory
from .common import encode_md5,encryption
from .boss import getCardsID,getBankAccount,addBankcard,infoJSON,cms_resetpwd,getMailRecord,getPwd_from_mail

head={
	'Content-Type':'application/json;charset=UTF-8',
	'Accept':'application/json',
	'Connection':'close',
}
head_urlencode={
	'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
	'Connection':'close',
}
head_text={
	'Content-Type':'text/xml',
	'Connection':'close',
}
################################ ABC相关接口 ##################################################################################
def resetpwd_abc(uname,newpwd,env='test'):
	url=f"http://{env}-app.****.****/app/exchange/resetPassword"
	try:
		card_id=getCardsID(uname,env)[0][1]
	except:
		logging.info(traceback.format_exc())
		card_id=None
	if card_id:
		head={
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
			'Connection':'close',
		}
		result=resetCode(uname,card_id,env,head)
		if result['result']!='1':return result
		data={
			"accountid":uname,
			"card_id":card_id,
			"sms_code":"8888",
			"password":newpwd,
			"callType":"normal",
		}
		resp=requests.post(url,headers=head,data=data)
		try:
			respJson=resp.json()
		except simplejson.errors.JSONDecodeError:
			respJson={"success":False,"result":"0","msg":"执行失败","responseText":resp.text}
	else:
		msg=f'从boss查询 {env} 环境账户 {uname} 的card_id失败，请检查。'
		respJson={"success":False,"msg":msg}
	return respJson

def resetCode(uname,card_id,env,head):
	url=f"http://{env}-app.****.****/app/exchange/resetCode"
	data={"accountid":uname,"card_id":card_id,"callType":"normal",}
	resp=requests.post(url,headers=head,data=data)
	return resp.json()

################################ 解锁账户 ##################################################################################
def resetAccountPwdSendCode(account,env='uat'):
	global head
	url=f'http://trade-{env}.****.****/gateway/account/resetAccountPwdSendCode'
	cerNo=getCardsID(account,env)
	if cerNo:
		cerNo=cerNo[0][1]
	else:
		return {'success':0,'msg':f'{env}环境查询{account}证件号失败。'}
	data={"traceLogId":f"fromZP{time.time()}","accountNo":account,"cerNo":cerNo,"codeType":"normal","json":True,"lang":"cn","signature":True}
	timestamp,signature=encryption(data,'H5')
	head["timestamp"]=timestamp
	head["signature"]=signature
	resp=requests.post(url,headers=head,json=data)
	del head["signature"]
	del head["timestamp"]

	respJson=resp.json()
	logging.info(f'resetAccountPwdSendCode 返回: {respJson}')
	if not respJson['success']:return respJson

def unlockAcc(account,env='uat'):
	resetAccountPwdSendCode(account,env)
	global head
	url=f'http://trade-{env}.****.****/gateway/account/unlock'
	data={
		"code":"8888",
		"accountNo":account,
		"traceLogId":f"fromZP{time.time()}",
		"lang":"cn",
		"signature":True,
		"json":True,
	}

	timestamp,signature=encryption(data,'H5')
	head["timestamp"]=timestamp
	head["signature"]=signature
	resp=requests.post(url,headers=head,json=data)
	del head["signature"]
	del head["timestamp"]

	respJson=resp.json()
	return respJson

################################ 通过APP接口重置密码 #################################
def resetAccountPwdCheckCode(account,env='uat'):
	global head
	url=f'http://trade-{env}.****.****/gateway/account/resetAccountPwdCheckCode'
	data={
		'accountNo':account,
		'code':"8888",
		'json':True,
		'lang':"cn",
		'signature':True,
		'traceLogId':f"fromTestservices{time.time()}",
	}
	timestamp,signature=encryption(data,'H5')
	head["timestamp"]=timestamp
	head["signature"]=signature
	resp=requests.post(url,json=data,headers=head)
	del head["signature"]
	del head["timestamp"]
	respJson=resp.json()
	try:
		resetToken=respJson.get('result').get('checkToken')
		return 1,resetToken
	except:
		logging.info(f'resetAccountPwdCheckCode 接口返回数据: {resp.text}')
		return 0,respJson

def resetpwd_APP(account,newpwd='aaaa1111',env='uat'):
	result=resetAccountPwdSendCode(account,env)
	if result:return result

	status,resetToken=resetAccountPwdCheckCode(account,env)
	if not status:return {'success':0,'msg':f'重置失败，接口 /gateway/account/resetAccountPwdCheckCode 返回数据异常','result':resetToken}

	url=f'http://trade-{env}.****.****/auth-center/public/account/resetAccountPwdSetPwd'
	data={
		'accountNo':account,
		'json':True,
		'lang':"cn",
		'resetToken':resetToken,
		'traceLogId':f"fromTestservices{time.time()}",
		'tradePwd':newpwd,
	}
	resp=requests.post(url,json=data,headers=head)
	respJson=resp.json()
	return respJson

################################ 通过BOSS重置密码 #################################
def resetpwd_BOSS(account,newpwd='aaaa1111',env='uat'):
	del_pwdHistory(account,env=env)# 删除曾经用过的密码
	result=cms_resetpwd(account,env=env)# 重置密码
	if result['result']!='1':return {'success':0,'msg':'cms重置密码失败！','result':result}

	mailid=getMailRecord(account,env=env,keyword='密码已重置')
	logging.info(f'邮件ID: {mailid}')
	boss_pwd=getPwd_from_mail(mailid[0][-1],env=env)# 查询重置后的密码
	logging.info(f'重置后的密码: {boss_pwd}')
	try:
		sessionDic=login_acc(account,boss_pwd,env,1)
		retResult=changeAccountPwd(sessionDic,boss_pwd,newpwd,env)
		return retResult
	except:
		logging.info(traceback.format_exc())
		return f'重置后的密码: {boss_pwd}'


def changeAccountPwd(sessionDic,oldpwd,newpwd='aaaa1111',env='uat'):
	url=f'http://trade-{env}.****.****/gateway/account/changeAccountPwd'
	# logging.info(f'debug: {sessionDic}')
	data={
		"newPassword":newpwd,
		"oldPassword":oldpwd,
		"session":sessionDic['sessionId'],
		"accountNo":sessionDic['accountId'],
		"traceLogId":f"fromTestservices{time.time()}",
		"json":True,
		"lang":"cn"
	}
	resp=requests.post(url,json=data,headers=head)
	respJson=resp.json()
	return respJson
 # 响应: {"success":true,"result":true,"returnMsg":null,"errorCode":null,"errorMsg":null}

################################ TTL相关接口 ##################################################################################
# def login_ttl(uname,pword,env='test'):
# 	url=f'http://trade-{env}.****.****/auth-center/public/login/accountLogin'
# 	head={
# 		'User-Agent':'zyapp/2.2.1.36591 (HONOR COLAL10; Android 9) uuid/VBJDU19510007442 channel/Atest1 redgreensetting/red language/zhCN versionCode/33562625',
# 		'Content-Type':'application/json;charset=UTF-8',
# 		'Connection':'close',
# 	}
# 	data={"traceLogId":f"fromTestServices_{time.time()}","accountNo":uname,"tradePwd":pword}
# 	resp=requests.post(url,headers=head,json=data)
# 	respJson=resp.json()
# 	# print(f'{uname} debug: {respJson}')
# 	if respJson['success']:
# 		sessionDic={
# 			'token':jsonpath(respJson,'$..loginToken')[0],
# 			'sessionId':jsonpath(respJson,'$..session')[0],
# 			'acctType':'MRGN' if 'M' in uname else 'CASH',
# 			'aeCode':jsonpath(respJson,'$..aeCode')[0],
# 			'marginMax':jsonpath(respJson,'$..marginMax')[0],
# 			'accountId':uname,
# 			'accountName':jsonpath(respJson,'$..acctName')[0],
# 			'operatorNo':jsonpath(respJson,'$..operatorNo')[0],
# 		}
# 		sessionDic['enName'],msg=getBindBankListByAccountId(sessionDic,env)
# 		if sessionDic['enName']:
# 			return {"success":True,"session":sessionDic}
# 		else:
# 			return msg
# 	else:
# 		return {"success":False,"message":f'TTL {env}环境{uname}登录失败: {respJson}'}

def getBindBankListByAccountId(sessionDic,env='test'):
	global head
	url=f'http://trade-{env}.****.****/gateway/casher/getBindBankListByAccountId'
	data={
		"accountid":sessionDic['accountId'],
		"accountNo":sessionDic['accountId'],
		"accountId":sessionDic['accountId'],
		"operatorNo":sessionDic['operatorNo'],
		"sessionId":sessionDic['sessionId'],
		"session":sessionDic['sessionId'],
		"loginToken":sessionDic['token'],
		"token":sessionDic['token'],
		"acctType":sessionDic['acctType'],
		"marginMax":sessionDic['marginMax'],
		"aecode":sessionDic['aeCode'],
		"isProspect":0,
		"currency":"USD",
		"traceLogId":f"fromTestServices_{time.time()}"
	}
	resp=requests.post(url,headers=head,json=data)
	respJson=resp.json()
	try:
		return respJson['result']['client_bank_account_name'],0
	except KeyError:
		return 0,{"success":False,"msg":f'getBindBankListByAccountId 接口返回数据异常: {respJson}'}
	except TypeError:
		logging.info(f'getBindBankListByAccountId: {respJson}')
		return 0,respJson

def resetpwd_CGF(uname,newpwd,env='test'):
	newpwd=encode_md5(f'{uname}_{newpwd}').upper()
	if env=='test':
		url='http://172.0.0.0:8089/mobile/services/v0/updatePassword'
	elif env=='uat':
		url='http://192.0.0.0:8089/mobile/services/v0/updatePassword'
	elif env=='dev':
		return {"success":False,"result":"0","msg":"Dev 环境没有该服务，请联系陈广峰"}
	head={
		'Content-Type':'application/json;charset=UTF-8',
		'X-Request-ID':'00000000001',
		'Accept':'application/json',
		'Connection':'close',
	}
	data={
		"channelID":"INT",
		"clientID":uname,
		"newPassword":newpwd,
		"encrypt":"N"
	}
	resp=requests.post(url,headers=head,json=data)
	try:
		respJson=resp.json()
		# {'returnCode': '0000'}
		respJson['result']='1' if respJson['returnCode']=='0000' else '0'
	except simplejson.errors.JSONDecodeError:
		respJson={"success":False,"result":"0","msg":"执行失败","responseText":resp.text}
	return respJson

def getTTLclientId(uname,pwd,env='test'):
	if env=='test':
		url='http://172.0.0.0.0:8089/mobile/services/v0/clientLogin'
	elif env=='uat':
		url='http://192.0.0.0.0:8089/mobile/services/v0/clientLogin'
	head={
		'Content-Type':'application/json;charset=UTF-8',
		'X-Request-ID':'00000000001',
		'Accept':'application/json',
		'Connection':'close',
	}
	data={
		"clientID":uname,
		"password":pwd,
		"sessionID":"kb+I5SXz4Bq+OY36RJN2NQ\u003d\u003d"
	}
	resp=requests.post(url,headers=head,json=data)
	try:
		respJson=resp.json()
	except simplejson.errors.JSONDecodeError:
		respJson={"success":False,"msg":"执行失败","responseText":resp.text}
	return respJson

def submitDeposite(sessionDic,currency,env='test',money='100000000'):
	# ttl 资金存入 currency: ['HKD','USD','CNY']
	global head
	currency=currency.upper()
	bankCodeDic={'HKD':'44700867093','USD':'44700867131','CNY':'44700867107'}
	url=f'http://trade-{env}.****.****/gateway/casher/submitDeposite'
	data={
		"traceLogId":f"fromTestServices_{time.time()}",
		"org_code":"CMBIS",
		"company_bank_account_name":"CMB INTL S L - C A/C",
		"company_bank_name":"渣打银行（香港）有限公司",
		"company_bank_code":"003",
		"company_bank_account":bankCodeDic[currency],
		"txn_way":1,
		"apply_amount":money,
		"client_bank_account":"333365585266",
		"client_bank_name":"渣打银行（香港）有限公司",
		"client_bank_code":"003",
		"isProspect":0,
		"org_id":"56",
		"certify_data_01":"202103/depositnode_918730_202103291438385803.jpg",
		"certify_data_02":"",

		"currency":currency,
		"client_bank_account_name":sessionDic['enName'],

		"accountid":sessionDic['accountId'],
		"accountNo":sessionDic['accountId'],
		"accountId":sessionDic['accountId'],
		"operatorNo":sessionDic['operatorNo'],
		"sessionId":sessionDic['sessionId'],
		"session":sessionDic['sessionId'],
		"loginToken":sessionDic['token'],
		"token":sessionDic['token'],
		"acctType":sessionDic['acctType'],
		"marginMax":sessionDic['marginMax'],
		"aecode":sessionDic['aeCode'],
	}
	resp=requests.post(url,headers=head,json=data)
	respJson=resp.json()
	return respJson

def addHOld_ttl(account,stockCode,stockNum,market,env='uat'):
	# ttl 加持仓 currency: ['HKD','USD','CNY']
	global head
	try:
		stockNum,cost=stockNum.split()
	except ValueError:
		cost=None
	stockNum=int(stockNum)
	DW='D' if stockNum>0 else 'W'

	marketID_dict={'HKG':'HKEX','USA':'USEX','SHA':'MAMK','SZA':'SZMK','FUND':'FUND','BOND':'BOND','SPMK':'SPMK'}
	if env in ['test','dev']:
		url='http://172.0.0.0.0:8089/mobile/services/v0/instrumentDW'
	elif env=='uat':
		url='http://192.0.0.0.0:8089/mobile/services/v0/instrumentDW'
	data={
		"clientID":account,
		"tranType":DW,
		"marketID":marketID_dict[market],
		"instrumentID":stockCode,
		"settleMethod":DW,
		"qty":stockNum,
		"sessionID":"sessionID",
		"waiveAllFees":"Y"
	}
	if cost:data["costPerShare"]=float(cost)
	resp=requests.post(url,headers=head,json=data)
	# respJson={'result':resp.text}
	try:
		respJson=resp.json()
	except simplejson.errors.JSONDecodeError:
		logging.error(f'返回数据异常: {resp.text}')
		respJson={'success':0,'errorMsg':resp.text}
	return respJson

def checkLoginName(acc,env='uat'):
	url=f"http://trade-{env}.****.****/gateway/operator/checkLoginName"
	data={"loginName":acc,"traceLogId":f"fromTestservices{time.time()}"}
	timestamp,signature=encryption(data)
	
	headers={
		"Content-Type":"application/json; charset=utf-8",
		"User-Agent":"zyapp/3.1.12 (Meizu 16 X; Android 8.1.0) uuid/872QAET9UDVDM channel/Atest1 cmbi-lang/zh-cn versionCode/50335756",
		"uuid":"872QAET9UDVDM",
		"TIMESTAMP":timestamp,
		"SIGNATURE":signature,
		"headerTraceLog":"and"+timestamp
	}
	resp=requests.post(url,json=data,headers=headers)
	try:
		respJson=resp.json()
	except simplejson.errors.JSONDecodeError as err:
		print(resp.text)
		raise err
	return respJson

################################ 灰度控制相关接口 ########################################################################
def grayControlAPI(method,env='test',kword=None):
	host=f"http://rhino-proxy-{env}.****.****"
	head={'RHINO-PROXY-TO':'quote-auth-v1.quote:8080'}
	if method=="get":
		path="/grayControl/config"
		resp=requests.get(host+path,headers=head)
	elif method=="delAll":
		path="/grayControl/whitelist/all"
		resp=requests.delete(host+path,headers=head)
	elif method=="del":
		path=f"/grayControl/whitelist?arg={kword}"
		resp=requests.delete(host+path,headers=head)
	elif method=="add":
		path=f"/grayControl/whitelist?arg={kword}"
		resp=requests.put(host+path,headers=head)
	elif method=="edit":
		path=f"/grayControl/config?end={kword}"
		resp=requests.put(host+path,headers=head)
	elif method=="mockIP":
		head={'RHINO-PROXY-TO':'cloud-api-v1.base-plat:8080'}
		path=f"/cloud-api/mock-config/geo-ip/set?mockStatus={kword}"
		resp=requests.put(host+path,headers=head)
	try:
		respJson=resp.json()
	except simplejson.errors.JSONDecodeError:
		respJson={"msg":resp.text}
	return respJson

def TTL_grayControl(method,env='test',grayType=None,status=None,uuid=None,remark=None,user=None):
	databaseName='test_base_plat' if env=='test' else 'base_plat'
	if method=='query':
		sql=f'SELECT UUID,GRAY_TYPE,STATUS,REMARK FROM {databaseName}.T_CUSTOMER_GRAY_CLIENT'
		result=excuteSQL(sql,env=env)
		respJson={"success":True,'result':list(result),'format':'ttl_gary'}
	elif method=='add':
		sql=f'SELECT ID FROM {databaseName}.T_CUSTOMER_GRAY_CLIENT WHERE UUID="{uuid}"'
		result=excuteSQL(sql,env=env)
		now=time.strftime('%Y-%m-%d %X')
		if result:
			remark=f",REMARK='{remark}'" if remark else ''
			sql=f"UPDATE {databaseName}.T_CUSTOMER_GRAY_CLIENT SET GRAY_TYPE='{grayType}',STATUS='{status}',UPDATED_BY='{user}',UPDATED_AT='{now}'{remark} WHERE UUID='{uuid}';"
		else:
			sql=f"INSERT INTO {databaseName}.T_CUSTOMER_GRAY_CLIENT (UUID,GRAY_TYPE,STATUS,CREATED_BY,CREATED_AT,UPDATED_BY,UPDATED_AT,REMARK) VALUES ('{uuid}','{grayType}','{status}','{user}','{now}','{user}','{now}','{remark}');"
		result=excuteSQL(sql,env=env)
		if result:
			respJson={"success":True,'msg':'成功'}
		else:
			respJson={"success":False,'msg':f'执行SQL失败: {sql}'}
	return respJson


################################ APP相关接口 ########################################################################
def w8InfoSubmit(sessionDic,w8table_no=None,env='test'):
	global head_urlencode
	# url=f'http://trade-{env}.****.****/app/exchange/w8InfoSubmit'
	url=f'http://{env}-app.****.****/gw1/business-service/app/exchange/w8InfoSubmit'
	if w8table_no:
		data={
			'submit_type':'submit',
			"w8table_no":w8table_no,
			"sign_img":'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEkAAABVCAYAAAAFZ8k8AAAEUElEQVR4Xu2bWegPURTHf39L5MG+ZCuy5AGJbAl/EgmhLH9L8iTkxYMsZcmWLSUp8iSUpRDyYI1seVBCWVMSsnuQffme/v/RdLszc37zvzNz5vc7t0795t4zc8/5/M69c7epKGiKJFARqaEKBYXECAKFpJAYBBgqGkkKiUGAoaKRpJAYBBgqGkkKiUGAoaKRpJAYBBgq5RBJG8BhOKQu5BZkLeQ9g81/lVKH9BqetjGAXMZ1pUKqJnAKMj4ARjfkP+GCKtVI2g8As0Mg9EPZ7XKGdAzOT44A0Arl78oV0kw4fjDC+aMon8YFRHql1NxWwB96kwWlvyi4CBlVDKBSgnQIzkwPcf4LyvpCHhULqFQgjaiJkCD/v6KgCnIyDqBSgDQATpyFNAkAcAn5YyA/4wLKO6SJcGBfCKB7KOtVGzjevXntuAnQiRAANO3oAvlcrpAawfHHkHYBAI5EdOJFc8tjJJ2Gl+MCPN2N/AVFU4i4IW+QjsOfSQE+3UF+H9eA8tZxP4fBHQMgPKgB9L2cIe2B8/MCAOwNKXPCLA/NbQI8DRoI0hBgrhMSIQ+RDqknbL8KsQ0WnyK/a9KApPdJ/WHgeUhjC4g3yKM1oRflDulTQARdR/5ISCKdtA261OZGIAZbDKZBZCXkZRoR5NUhEdIwGEeL9Wb6gwwaB91NE5DEPqkDjHoGqWcBQSuOYevWibGTFkk34Okgi7e0HEJLHpkkSZCugMBQCwUaSM7PhE5NpVIgdYY9NO4x7fmIvOZZApLSJ9H281tIMwPGB1y3yBqQFEiHYYhti2cZ8jcrpEJhOyAstoBYhbx1EgBJiCTqc5oaMGig2F4KoKwh0ejZnKDS1jNtQYtKWb3daO51wSBBO6xLIVtFEYIxWUH6hrobGDA24Xq5NEBZNTc6sDDFgPEQ1z0kAsoC0lhUesaA8QvX9aUCygKSbTF/CQzZppCqCeyCLDRg0Buuu2RAaUZSJ1RGx178zUrk6972h6X1drMtgayEQeulR1FakbTR8mqng59z8gAoLUg0w2/pA5KbZubZnHRzoz2zIUbE0F7a/bxEUdKR1BoVvILU8QGhs40z8gQoaUg0m2/rAyJilTHOH5RUc6NFNFpM89Jv/KCPYK7FMTLre5KARPv29OFLQ59zNBUJOniVNYPI+pOAdAC1zvLVTJuJvSMtEazgGtIa+Lra8JcApb7r6pK5a0jmBDY3o+owqC4h0anXqb7K6HiM+UGeyz84tWe5gkRr1TSj9xKdn6Y89udSqXkcoyJXkG6i7oG++mmteksMe0Te4gISncynE/peOocfo0V6G9MoF5B+oG5vnSi3o+okO27/aiNtCdFuh4it6ZhBY72ttpHk36YmYItcGiflWbWFRH7shNDn4zukOOXaDheQXNsk7nkKifGXKCSFxCDAUNFIUkgMAgwVjSSFxCDAUNFIUkgMAgwVjSSFxCDAUNFIUkgMAgyVfzq8g1bTHniDAAAAAElFTkSuQmCC',
			'accountid':sessionDic['accountId'],
			'sessionid':sessionDic['sessionId'],
			'acctype':sessionDic['acctType'],
			'aecode':sessionDic['aeCode'],
			'margin_max':sessionDic['marginMax'],
			'token':sessionDic['token'],
		}
	else:
		data={
			'country':'CHN',
			'residence_country':'CHN',
			'residence_country_same':'1',
			'mail_address_country':'CHN',
			'mail_address_country_same':'1',
			'birthday':'1984-06-01',
			'ssn_itin':'',
			'foreign_tax_num':'',
			'address':'xiang gang',
			'mail_address':'xiang gang',
			'mail_address_same':'1',
			'passport_img':'',
			'passport_name':'',
			'passport_number':'',
			'passport_valid_date':'',
			'submit_type':'save',
			'name':sessionDic['enName'],
			'accountid':sessionDic['accountId'],
			'sessionid':sessionDic['sessionId'],
			'acctype':sessionDic['acctType'],
			'aecode':sessionDic['aeCode'],
			'margin_max':sessionDic['marginMax'],
			'token':sessionDic['token'],
		}
	# logging.info(data)
	resp=requests.post(url,headers=head_urlencode,data=data)
	respJson=resp.json()
	return respJson

def createW8Pdf(sessionDic,w8table_no,env='test'):
	global head_urlencode
	url=f'http://trade-{env}.****.****/app/exchange/createW8Pdf'
	data={
		'accountid':sessionDic['accountId'],
		'sessionid':sessionDic['sessionId'],
		'acctype':sessionDic['acctType'],
		'aecode':sessionDic['aeCode'],
		'margin_max':sessionDic['marginMax'],
		'token':sessionDic['token'],
		'w8table_no':w8table_no,
	}
	resp=requests.post(url,headers=head_urlencode,data=data)
	respJson=resp.json()
	return int(respJson['result'])

def w8Submit(sessionDic,env='test'):
	respJson=w8InfoSubmit(sessionDic,w8table_no=None,env=env)
	logging.info(f"{sessionDic['accountId']} w8InfoSubmit {respJson['result']}")
	w8table_no=respJson['result']['w8table_no']
	result=createW8Pdf(sessionDic,w8table_no,env=env)
	if result:logging.info(f"{sessionDic['accountId']} createW8Pdf 成功")
	respJson=w8InfoSubmit(sessionDic,w8table_no=w8table_no,env=env)
	logging.info(f"{sessionDic['accountId']} {respJson['result']}")
#################################################################################
def derTest(sessionDic,env='test'):
	# 衍生品问卷
	global head_urlencode
	url=f'http://{env}-app.****.****/app/exchange/derTest'
	data={
		'accountid':sessionDic['accountId'],
		'sessionid':sessionDic['sessionId'],
		'acctype':sessionDic['acctType'],
		'aecode':sessionDic['aeCode'],
		'margin_max':sessionDic['marginMax'],
		'token':sessionDic['token'],
		'q1':'1','q2':'4','q3':'4','q4':'4','q5':'2'
	}
	resp=requests.post(url,headers=head_urlencode,data=data)
	respJson=resp.json()
	logging.info(f"{sessionDic['accountId']} {respJson['message']}")

def openMarket(uname,pword,env='test'):
	# 开通市场
	global head_urlencode
	sessionDic=login_acc(uname,pword,env,ttl=1)

	url=f'http://trade-{env}.****.****/app/exchange/openMarket'
	data={
		'accountid':sessionDic['accountId'],
		'sessionid':sessionDic['sessionId'],
		'acctype':sessionDic['acctType'],
		'aecode':sessionDic['aeCode'],
		'margin_max':sessionDic['marginMax'],
		'token':sessionDic['token'],
		# 'mk_hk':'0',
		# 'mk_hs':'1',
		# 'mk_hsb':'1',
		# 'mk_otc':'1',
		# 'mk_us':'1',
		'q1':'3','q2':'4','q3':'2','q4':'5','q5':'4','q6':'5','q7':'5','q8':'5','q9_1':'0','q9_1_1':'0','q9_1_2':'0','q9_2':'0','q9_2_1':'0','q9_2_2':'0','q9_3':'0','q9_3_1':'0','q9_3_2':'0','q9_4':'0','q9_4_1':'0','q9_4_2':'0','q9_5':'1','q9_5_1':'3','q9_5_2':'2','q9_6':'0','q9_6_1':'0','q9_6_2':'0','q9_7':'0','q9_7_1':'0','q9_7_2':'0','q9_8':'0','q9_8_1':'0','q9_8_2':'0','q9_9':'0','q9_9_1':'0','q9_9_2':'0','q9_10':'0','q9_10_1':'0','q9_10_2':'0','q9_11':'0','q9_11_1':'0','q9_11_2':'0','q9_12':'0','q9_12_1':'0','q9_12_2':'0','q9_13':'0','q9_13_1':'0','q9_13_2':'0','q9_14':'0','q9_14_1':'0','q9_14_2':'0','q9_15':'0','q9_15_1':'0','q9_15_2':'0','q9_16':'0','q9_16_1':'0','q9_16_2':'0','rpqSubmit':'true'
	}
	result=[]
	for i in ['HK','HS','HSB','OTC','US']:
		data[f'mk_{i.lower()}']='1'
		resp=requests.post(url,headers=head_urlencode,data=data)
		respJson=resp.json()
		result.append(f"开通{i}结果: {respJson['message']}")
		logging.info(f"开通{i}结果: {respJson['message']}")

###################################################################################
def setPwdTel(args,newPwd):
	#手机号第一次登录 设置密码
	for i in range(30):
		token,reason=smsCodeLogin(args)
		if token:
			key={
				"loginPwd":newPwd,
				"loginToken":token,
				"operatorNo":args.operatorNo,
				"operatorType":"2",
				"traceLogId":f"fromTestServices{time.time()}",
			}
			resp=requests.post(f'http://trade-{args.env}.****.****/gateway/operator/setPassword',headers=head,json=key,verify=False)
			respJson=resp.json()
			if respJson['success']:
				return 1,0
			else:
				return 0,respJson
		else:
			if i==29 or '过于频繁' not in str(reason):return 0,reason
			else:time.sleep(1)

def smsCodeLogin(args,vcode='8888'):
	#接口方式 手机号+验证码登录
	status,reason=sendSMS(args)
	time.sleep(3)
	vcode='8888'
	# vcode=getSMScode(args.tel,args.env,n=4)
	if status:
		url=f'http://trade-{args.env}.****.****/gateway/operator/smsCodeLogin'
		data={
			'areaCode': "86",
			'channel': "OUTER_H5",
			'code': vcode,
			'lang': "cn",
			'mobile': args.tel,
			'signatureApp': True,
			'traceLogId': f"fromTestServices{time.time()}",
		}
		logging.info(f'请求URL: {url}')
		logging.info(f'请求数据: {data}')
		timestamp,signature=encryption(data)
		head["timestamp"]=timestamp
		head["signature"]=signature
		resp=requests.post(url,headers=head,json=data)
		del head["signature"]
		del head["timestamp"]
		respJson=resp.json()
		logging.info(f'响应数据: {respJson}')
		
		if respJson['success']:
			args.operatorNo=respJson['result']['operatorNo']
			return respJson['result']['loginToken'],0
		else:
			return 0,respJson
	else:
		return 0,reason

def sendSMS(args):
	url=f'http://trade-{args.env}.****.****/gateway/operator/sendSmsCode'
	data={
		'areaCode': "86",
		'codeType': "normal",
		'lang': "cn",
		'mobile': args.tel,
		'signatureApp': True,
		'traceLogId': f"fromTestServices{time.time()}",
	}
	logging.info(f'请求URL: {url}')
	logging.info(f'请求数据: {data}')

	timestamp,signature=encryption(data)
	head["timestamp"]=timestamp
	head["signature"]=signature
	resp=requests.post(url,headers=head,json=data)
	del head["signature"]
	del head["timestamp"]

	respJson=resp.json()
	logging.info(f'响应数据: {respJson}')
	# {"success":true,"result":{"areaCode":"86","mobile":"13587945816","fromMobile":null},"returnMsg":null,"errorCode":null,"errorMsg":null}
	if respJson['success']:
		return 1,0
	else:
		return 0,f'手机号登录时发送验证码失败： {respJson}'

################################ 银证入金相关 ######################################################################
# 银证登记
def bankSecurities_reg(account,bankName,bankNum,tradeDate,env='uat',auto_addBank=0):
	cardType_dict={'中国居民身份证':'A','护照':'B','军人证':'C','户口本':'D','居住证':'E','监护人证件':'F','武警身份证':'G','通行证':'H','暂住证':'I','香港永久性居民身份证':'L','香港居民身份证':'L','其他居民身份证':'Z'}
	cardTypeName,card_id=getCardsID(account,env)[0]
	for i in range(5):
		bankcard_dict=getBankAccount(account,env)
		if bankNum in bankcard_dict.keys():
			break
		else:
			if auto_addBank:
				logging.info(f'{account} 开始自动添加结算银行卡 {bankNum}')
				respJson=addBankcard(account,bankNum,env=env)
				logging.info(f'自动添加结算银行卡结果: {respJson}')
			else:
				return {'success':0,'msg':f'{env}环境账户{account}名下没有该结算卡: {bankNum}'}
	bankCustName=bankcard_dict[bankNum][1]

	tradeTime='170915'
	if bankName=='港分银行':
		url=f'http://rhino-proxy-{env}.****.****/capital-trans/cmbhkTocmbi/hkbsTransferRegister'
		head['RHINO-PROXY-TO']='capital-trans-v1.capital:8080'
		data={
			"accountId":account,#户口号
			"acctNo":bankNum,#银行号卡
			"bankCustName":bankCustName,#结算卡账户名称
			"bankCustIdCard":f"{cardType_dict[cardTypeName]}{card_id}",#证件号 
			"remark":""
		}
		resp=requests.post(url,headers=head,json=data,verify=False)
		del head['RHINO-PROXY-TO']
		try:
			respJson=resp.json()
		except Exception:
			traceback.print_exc()
			respJson={'success':0,'result':resp.text}
			# return 
	elif bankName=='永隆银行':
		url=f'http://innersvc-{env}.****.****/capital-wlb/wlbTransfer/indexForTest'
		data={
			"HEAD":{
				"RCVID":"CMBI",
				"ORGREF":f"FromTestServices{str(time.time()).replace('.','')}",
				"MSGCD":"1000",#交易代码 固定 1000
				"DATE":tradeDate+tradeTime#交易日期
			},
			"BODY":{
				"SECURITIESNO":account,#户口号
				"ACCOUNTNAME":bankCustName,#用户姓名 （不校验正确性）
				"DOCUMENTID":f"{cardType_dict[cardTypeName]}{card_id}",#证件账号  多个证件请用 ","分隔  LC502004(3)，LC502005(3)
				"ACCOUNTNO1":bankNum,#港币银行卡
				"CCY1":"HKD",#港币币种
				"REGFLAG1":"Y",#开通 Y ，关闭 N
				"ACCOUNTNO2":bankNum,#人民币银行卡
				"CCY2":"CNY",#人民币币种
				"REGFLAG2":"Y",
				"ACCOUNTNO3":bankNum,#美元银行卡
				"CCY3":"USD",#美元币种
				"REGFLAG3":"Y",
				"REMARK":""
			}
		}
		resp=requests.post(url,headers=head,json=data,verify=False)
		respJson={'success':1,'result':resp.text}
	elif bankName=='民生银行':
		url=f'http://innersvc-{env}.****.****/capital-cmbc/transfer/cmbcTocmbi'
		RefNo=f"FromTestServices{str(time.time()).replace('.','')}" #业务流水号
		comDate=tradeDate
		comTime=tradeTime
		data=f'<DO-DATA BankId="353" ChnlId="BSD" DstApp="SEZHZQ" DstServ="BSDB201" Locale="EN" MsgType="REQ" RefNo="{RefNo}DODATA" ReqSys="IBPBSD" TermNo="000000" TxDate="{comDate}" TxTime="{comTime}" UserId="SEZHZQ01"><DO-MESSAGE AgrNo="{RefNo}" CusAc="{bankNum}" HidNo="{card_id}" HidTyp="CP" IdNo="{card_id}" IdTyp="PP" SDNo="SEXXZQ01" SecAc="{account}"/></DO-DATA>'
		resp=requests.post(url,headers=head_text,data=data,verify=False)

		data=f'<DO-DATA BankId="353" ChnlId="BSD" DstApp="SEZHZQ" DstServ="BSDB202" Locale="EN" MsgType="REQ" RefNo="{RefNo}DODATA" ReqSys="IBPBSD" TermNo="000000" TxDate="{comDate}" TxTime="{comTime}" UserId="SEZHZQ01"><DO-MESSAGE AgrNo="{RefNo}" CusAc="{bankNum}" HidNo="{card_id}" HidTyp="CP" IdNo="{card_id}" IdTyp="PP" RslFlg="Y" SDNo="SEXXZQ01" SecAc="{account}"/></DO-DATA>'
		resp=requests.post(url,headers=head_text,data=data,verify=False)
		respJson={'result':resp.text}
		respJson['success']=1 if resp.text=='00000000' else 0
	return respJson

# 银证入金
def bankSecurities_transfer(account,bankName,bankNum,currency,amount,tradeDate,env='uat',auto_bankReg=0,auto_addBank=0):
	if auto_bankReg:
		respJson=bankSecurities_reg(account,bankName,bankNum,tradeDate,env,auto_addBank)
		if not respJson['success']:return respJson

	tradeTime='170915'
	if bankName=='港分银行':
		head['RHINO-PROXY-TO']='capital-trans-v1.capital:8080'
		url=f'http://rhino-proxy-{env}.****.****/capital-trans/cmbhkTocmbi/marginReceiptNotice'
		data={
			"bankTradeSeq":f"FromTestServices{str(time.time()).replace('.','')}",
			"accountId":account,
			"acctNo":bankNum,
			"currency":currency,
			"tradeAmount":amount,
			"tradeDate":tradeDate,
			"tradeTime":tradeTime,
			"bookDate":tradeDate
		}
		resp=requests.post(url,headers=head,json=data,verify=False)
		del head['RHINO-PROXY-TO']
	elif bankName=='永隆银行':
		url=f'http://innersvc-{env}.****.****/capital-wlb/wlbTransfer/indexForTest'
		data={
			"HEAD":{
				"RCVID":"CMBI",
				"ORGREF":f"FromTestServices{str(time.time()).replace('.','')}",#流水号
				"MSGCD":"2000",
				"DATE":tradeDate+tradeTime#交易日期
			},
			"BODY":{
				"SECURITIESNO":account,#户口号
				"ACCOUNTNO":bankNum,# 银行卡
				"CCY":currency,# 币种
				"AMOUNT":amount# 金额
			}
		}
		resp=requests.post(url,headers=head,json=data,verify=False)
	elif bankName=='民生银行':
		url=f'http://innersvc-{env}.****.****/capital-cmbc/transfer/cmbcTocmbi'
		RefNo=f"FromTestServices{str(time.time()).replace('.','')}" #业务流水号
		comDate=tradeDate
		comTime=tradeTime
		data=f'<DO-DATA BankId="353" ChnlId="BSD" DstApp="SEZHZQ" DstServ="BSDB101" Locale="EN" MsgType="REQ" RefNo="{RefNo}DODATA" ReqSys="IBPBSD" TermNo="000000" TxDate="{comDate}" TxTime="{comTime}" UserId="SEZHZQ01"><DO-MESSAGE AcCkDt="{comDate}" Amt="{amount}" Ccy="{currency}" CusAc="{bankNum}" RefNo="{RefNo}" SDNo="SEXXZQ01" SecAc="{account}" TraDat="{comDate}" TraTim="{comTime}"/></DO-DATA>'
		resp=requests.post(url,headers=head_text,data=data,verify=False)

	try:
		respJson=resp.json()
	except:
		respJson={'result':resp.text}
	return respJson

################################ 登录登出接口 ########################################################################
def login_acc(uname,pword,env='test',ttl=1):
	#账户登录接口
	global head
	head['User-Agent']='zyapp/2.2.1.36591 (HONOR COLAL10; Android 9) uuid/VBJDU19510007442 channel/Atest1 redgreensetting/red language/zhCN versionCode/33562625'
	try:
		result=checkLoginName(uname,env)
		accountType=result['result']['accountType']
	except:
		return {'success':0,'msg':f'无效用户名','result':result}

	if accountType=='ACCOUNT':
		url=f'http://trade-{env}.****.****/auth-center/public/login/accountLogin'
		data={"traceLogId":f"fromTestServices_{time.time()}","accountNo":uname,"tradePwd":pword}
	elif accountType=='MOBILE':
		url=f'http://trade-{env}.****.****/auth-center/public/login/mergeLogin'
		data={"traceLogId":f"fromTestServices_{time.time()}","loginType":"MOBILE","loginName":uname,"loginPwd":pword,"channel":"ANDROID"}

	resp=requests.post(url,headers=head,json=data)
	respJson=resp.json()
	print(f'{uname} debug: {respJson}')
	if respJson:
		doTwoFa(uname,env)
		try:
			sessionDic={
				# 'token':jsonpath(respJson,['$..loginToken','$..token'])[0],
				'token':(jsonpath(respJson,'$..loginToken') or jsonpath(respJson,'$..token'))[0],
				'sessionId':(jsonpath(respJson,'$..session') or jsonpath(respJson,'$..sessionid'))[0],
				'acctType':'MRGN' if 'M' in uname else 'CASH',
				'aeCode':(jsonpath(respJson,'$..aeCode') or jsonpath(respJson,'$..aecode'))[0],
				'marginMax':(jsonpath(respJson,'$..marginMax') or jsonpath(respJson,'$..margin_max'))[0],
				'accountId':uname,
				'accountName':(jsonpath(respJson,'$..acctName') or jsonpath(respJson,'$..account_name'))[0],
				'operatorNo':(jsonpath(respJson,'$..operatorNo') or jsonpath(respJson,'$..user_id'))[0],
			}
			if accountType=='ACCOUNT':sessionDic['enName']=getBindBankListByAccountId(sessionDic,env)[0]
			sessionDic['env']=env
			sessionDic['success']=1
			return sessionDic
		except Exception:
			logging.error(f'{traceback.format_exc()}')
			logging.error(f'登录失败: {respJson}')
			return {'success':0,'msg':f'登录失败','result':respJson}
	else:
		return {'success':0,'msg':f'登录失败','result':respJson}

def doTwoFa(account,env):
	global head
	url=f'http://trade-{env}.****.****/gw1/auth-center/twoFa/applyTwoFaCode'
	data={"accountNo":account,"codeType":"normal","traceLogId":f"fromAutotest{time.time()}"} 
	resp=requests.post(url,headers=head,json=data)
	respJson=resp.json()
	logging.info(f'applyTwoFaCode 响应: {respJson}')

	url=f'http://trade-{env}.****.****/gw1/auth-center/twoFa/verifyTwoFaByCode'
	data={"accountNo":account,"code":"888888","traceLogId":f"fromAutotest{time.time()}"} 
	resp=requests.post(url,headers=head,json=data)
	respJson=resp.json()
	logging.info(f'verifyTwoFaByCode 响应: {respJson}')

def logout_acc(account,sessionid,env='uat'):
	url=f'http://trade-{env}.****.****/auth-center/logout/acctLogout'
	userInfo=infoJSON(account,env)
	if userInfo['result']=='1':
		data={
			"accountId":account,
			"accountNo":account,
			"acctType":userInfo['data']['AcctType'],
			"aecode":userInfo['data']['AECode'],
			"sessionId":sessionid,
			"traceLogId":f"fromTestServices_{time.time()}"
		}
		resp=requests.post(url,headers=head,json=data,verify=False)
		return resp.json()
	else:
		return {'success':0,'msg':f'{env}环境从boss查询{account}信息失败','result':userInfo}

################################ 其它接口 ########################################################################
def resetpwd(uname,newpwd,env='test',ttl=0):
	if ttl:
		return resetpwd_CGF(uname,newpwd,env)
	else:
		return resetpwd_abc(uname,newpwd,env)

def addOptionalStock(sessionDic,market_codes):
	#添加自选股接口
	url=f'http://{sessionDic["env"]}-app.****.****/gateway2/stock/addOptionalStock'
	data={
		"traceLogId":f"fromTestServices_{time.time()}",
		"market":"",
		"code":"",
		"operatorNo":sessionDic['operatorNo'],
		"token":sessionDic['token']
	}
	for m_code in market_codes:
		data['market']=m_code[0]
		data['code']=m_code[1:]
		logging.info(f"{sessionDic['accountId']} 添加自选 {data}")
		resp=requests.post(url,headers=head,json=data,verify=False)
		respJson=resp.json()
		logging.info(f"{sessionDic['accountId']} 添加自选 {m_code} 结果: {respJson}")

def addOptionalFoundation(sessionDic,fundInfoList):
	#添加基金自选股接口
	url=f'http://{sessionDic["env"]}-app.****.****/gateway2/stock/addOptionalFoundation'
	data={
		"traceLogId":f"fromTestServices_{time.time()}",
		"isinCode":"",
		"currency":"",
		"productId":"",
		"operatorNo":sessionDic['operatorNo'],
		"token":sessionDic['token']
	}
	for fundInfo in fundInfoList:
		data['isinCode']=fundInfo[0]
		data['currency']=fundInfo[1]
		data['productId']=fundInfo[2]
		logging.info(f"{sessionDic['accountId']} 添加基金自选 {data}")
		resp=requests.post(url,headers=head,json=data,verify=False)
		respJson=resp.json()
		logging.info(f"{sessionDic['accountId']} 添加基金自选 结果: {respJson}")

def filtrateSelectList(env='test'):
	url=f'http://trade-{env}.****.****/gateway/fund/filtrateSelectList'
	data={"page":2,"pageSize":999,"broadCategoryGroup":"Equity","currencyType":"","riskId":"","domicileType":"","brandingType":"","sellChannel":"APP","returnId":"1","returnSort":"desc","orgId":"CMBI","traceLogId":"ifaCG9dYw4I4"}
	resp=requests.post(url,headers=head,json=data,verify=False)
	respJson=resp.json()
	logging.info(respJson)
	for item in respJson['result']['fundBoList']:
		print(item['isin'],item['currency'],item['productCode'])

def unBind(account,pword,env):
	# 解绑所有关联的证券账户
	sessionDic=login_acc(account,pword,env,ttl=1)
	if sessionDic['success']:
		data={
			"loginToken":sessionDic['token'],
			"operatorNo":sessionDic['operatorNo'],
			"traceLogId":f"fromTestServices_{time.time()}",
		}
		url=f"http://trade-{env}.****.****/gw1/auth-center/operator/cancel"
		resp=requests.post(url,headers=head,json=data,verify=False)
		respJson=resp.json()
		return respJson
	else:
		return sessionDic

