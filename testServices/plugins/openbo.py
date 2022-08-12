from bs4 import BeautifulSoup
from requests_toolbelt import MultipartEncoder
import requests,time,logging,re,simplejson
from .common import saveCookie,readCookie

def getConfig_openbo(env):
	global host,head,uname,pwd
	host=f'http://{env}-openbo.****.*****'
	uname='zoupeng'
	pwd='zoupeng123'

	head={
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
		'Cookie':'',
		'Connection':'Close',
		'X-Requested-With':'XMLHttpRequest'
	}

def loginBO(env):
	logging.info(f'开始登录开户管理系统')
	global host,head,uname,pwd
	getConfig_openbo(env)
	head['Content-Type']='application/x-www-form-urlencoded'
	url=f'{host}/back/signin'
	for i in range(3):
		keys={
			"username":uname,
			"password":pwd,
			"vcode":"",
		}
		# head['Cookie'],keys['vcode']=getCodeBO(head)
		# keys['vcode']='299792458'
		resp=requests.post(url,headers=head,data=keys)
		if 'window.location.href = "/back/"' in resp.text:
			logging.error(f'{env} 登录开户管理系统成功')

			head['Cookie']=resp.headers['set-cookie']
			saveCookie(head['Cookie'],f'openbo_{env}')
			return head['Cookie']
		else:
			logging.error(f'{env} 自动登录开户管理系统失败: {resp.text}')
			logging.info(f'2秒后开始第 {i+1} 次重试...')
			time.sleep(2);head['Cookie']=''
	raise Exception

def requests_openbo(methmod,path,backType='json',env='uat',**kwargs):
	global host,head,uname,pwd
	getConfig_boss(env.lower())
	cookieLogined=readCookie(f'openbo_{env}')
	for i in range(5):
		head['Cookie']=cookieLogined
		resp=requests.request(methmod,f'{host}{path}',headers=head,**kwargs)
		if 'admin/AdminUser' in resp.text or '登录超时' in resp.text:
			logging.info(f'BOSS后台cookie失效，重新登录…')
			cookieLogined=login_boss(env)
			continue
		else:
			if backType=='json':
				try:
					result=resp.json()
				except:
					logging.error(f'{path}返回数据不是json {resp.text}')
					result=resp.text
					continue
			elif backType=='text':
				result=resp.text
			elif backType=='soup':
				# with open('temp.hml','w',encoding='utf-8') as f:f.write(resp.text)
				result=BeautifulSoup(resp.text,'lxml')
			return result
########################################################################
def getCheckID(search2='',account='',protectID='',getAcclist=0,env='uat',ttl=0):
	key2='email' if '@' in search2 else 'mobile'
	global host,head,uname,pwd
	getConfig_openbo(env)
	cookieLogined=readCookie(f'openbo_{env}')
	if getAcclist:
		logging.info(f'查询 {search2} 对应的 户口号')
	else:
		logging.info(f'查询 {search2} 对应的 checkID')
	url=f'{host}/back/cmbi/table/search'
	keys={
		'TableNo':'',
		'table_account':account,
		'table_step':'',
		'key1':'broker_code',
		'search1':'',
		'key2':key2,
		'search2':search2,
	}
	if protectID:keys['type']='secondPersonal'
	for i in range(3):
		checkID=0;head['Cookie']=cookieLogined
		resp=requests.get(url,headers=head,params=keys)
		# print(url,keys)
		if '登录超时' in resp.text:
			logging.info(f'开户管理后台cookie失效，重新登录…')
			cookieLogined=loginBO(env)
			continue
		else:
			soup=BeautifulSoup(resp.text,"lxml")
			if getAcclist:
				accList=soup.select_one('tbody').select_one('tr').select('td')[2].text.split()
				return accList
			for tr in soup.select('tr')[1:]:
				account=tr.select('td')[2].text.strip()
				if not re.search(r'\d+',account):continue
				elif account!=protectID:
					checkID=tr.select_one("[title='开户审核']")['href'].split('=')[-1]
					break
					# print(checkID)
			# checkID=list(map(lambda s:s['href'].split('=')[-1],soup.select("[title='开户审核']")))[n]
			if checkID:
				logging.info(f'对应的 checkID: {checkID}')
				return checkID		
			else:
				logging.error(f'获取checkID失败: {resp.text}')
				logging.info(f'2秒后开始第 {i+1} 次重试...')
				time.sleep(2)
	return 0

def amlTable(checkID=None,env='uat',ttl=0):
	global host,head,uname,pwd
	getConfig_openbo(env)
	cookieLogined=readCookie(f'openbo_{env}')
	m=MultipartEncoder(fields={
		"add_date":"","version":"v3","address_country":"CHN","nationality_country":"CHN","relation_country":"",
		"occupation":"22","industry":"2","sole_beneficiary":"YES","KYC":"YES","money_conform":"NO","explain_source_of_wealth":"YES",
		"cancel_CMBI_account":"NO","face_to_face":"NO","is_politician":"NO","on_the_blacklist":"NO","on_the_watchlist":"NO",
		"sanction":"NO","high_risk_level":"NO","unknown_risks":"","risk_score":"1","aml_risk_level":"Medium Risk","change_aml_risk_level":"Not Change",
		"change_reason":"","rm_agree":"Agree","rm_name":"autotest","rm_note":"","ro_agree":"Agree","ro_name":"autotest","ro_note":"",
		"compliance_agree":"Agree","compliance_name":"autotest","compliance_note":"","source_of_fund":"","source_of_wealth":"","anticipated_type_volume":""
	})

	logging.info(f'{checkID} 开始 反洗钱表格...')
	for i in range(3):
		head['Cookie']=cookieLogined
		head['Content-Type']=m.content_type
		resp=requests.post(f'{host}/back/cmbi/table/amlTable?id={checkID}',headers=head,data=m)
		if '登录超时' in resp.text:
			logging.info(f'开户管理后台cookie失效，重新登录…')
			cookieLogined=loginBO(env)
			continue
		else:
			try:
				respJson=resp.json()
			except (IndexError,simplejson.errors.JSONDecodeError):
				raise Exception(f'反洗钱表格时返回数据异常： {resp.text}')		
		try:
			flag=respJson['status']
		except KeyError:
			raise Exception(f'反洗钱表格时返回数据异常： {respJson}')
		if flag=='000':
			logging.info(f'{checkID} 反洗钱表格成功')
			return checkID
		else:
			logging.info(f'反洗钱表格失败：{respJson}')
			logging.info(f'2秒后开始第 {i+1} 次重试...')
			time.sleep(2)
	raise Exception

def checkBO(phone,t,checkID=None,env='uat',ttl=0):
	global host,head,uname,pwd
	getConfig_openbo(env)
	cookieLogined=readCookie(f'openbo_{env}')
	if not checkID:checkID=getCheckID(search2=phone,env=env,ttl=ttl)
	if t==1:
		m=MultipartEncoder(fields={"sfc_result":"3","from_step_id":"9","table_step":"5","table_status":"start"})
		msg1=f'{checkID} 开始 COB预审...';msg='COB预审 审核通过'
	elif t==2:
		m=MultipartEncoder(fields={"sfc_result":"3","from_step_id":"5","table_step":"6","table_status":"start"})
		msg1=f'{checkID} 开始 RM审批...';msg='RM审批 审核通过'
	elif t==3:
		m=MultipartEncoder(fields={"sfc_result":"3","from_step_id":"6","table_step":"7","table_status":"start"})
		msg1=f'{checkID} 开始 RO审批...';msg='RO审批 审核通过'
	elif t==4:
		m=MultipartEncoder(fields={"from_step_id":"7","table_step":"100","table_status":"start"})
		msg1=f'{checkID} 开始 COB开户 审核...';msg='COB开户 审核通过'
	logging.info(msg1)
	for i in range(3):
		head['Cookie']=cookieLogined
		head['Content-Type']=m.content_type
		try:
			resp=requests.post(f'{host}/back/cmbi/table/approve?id={checkID}',headers=head,data=m)
		except requests.exceptions.ConnectionError:
			if i==4:raise Exception(f'{env} 环境开户管理系统审核无响应')
			else:
				time.sleep(1)
				continue
		if '登录超时' in resp.text:
			logging.info(f'开户管理后台cookie失效，重新登录…')
			cookieLogined=loginBO(env)
			continue
		else:
			respJson=0
			try:
				respText=resp.text.replace('null','None')
				respJson=eval(re.findall(r'\{.+\}',resp.text)[0])
				# if not respJson:
				# 	logging.error(f'审核失败: {resp.text}')
				# 	logging.info(f'2秒后开始第 {i+1} 次重试...')
				# 	time.sleep(2);continue
				flag=respJson['status']
			except (IndexError,KeyError):
				reason=f'审核时返回数据异常: {resp.text}'
				logging.error(reason)
				return 0,reason

		if flag=='000':
			logging.info(msg)
			return checkID,0
		elif '审核状态被' in respJson["message"] and '更改' in respJson["message"]:
			logging.info(msg)
			return checkID,0
		else:
			reason=f'审核失败：{respJson["message"]}'
			logging.info(reason)
			return 0,reason

def manualActivate(checkID,env='uat',ttl=0):
	global host,head,uname,pwd
	getConfig_openbo(env)
	logging.info(f'开始激活 {checkID}')
	cookieLogined=readCookie(f'openbo_{env}')
	head['Cookie']=cookieLogined
	m=MultipartEncoder(fields={'active_reason':'AutoTest'})
	head['Content-Type']=m.content_type
	resp=requests.post(f'{host}/back/cmbi/table/manualActivate?id={checkID}',headers=head,data=m)
	respJson=eval(re.findall(r'\{.+\}',resp.text)[0])
	try:
		flag=respJson['status']
	except KeyError:
		return f'激活时返回数据异常： {resp.text}'
	if flag=='000':
		logging.info('激活成功')
		return 0
	else:
		return f'激活失败：{respJson["message"]}'

def piDocument(checkID,env='uat',ttl=0):
	global host,head,uname,pwd
	getConfig_openbo(env)
	logging.info(f'开始补充PI资料 {checkID}')
	cookieLogined=readCookie(f'openbo_{env}')
	head['Cookie']=cookieLogined
	m=MultipartEncoder(fields={
		'pi_document':'','pi_certify':'',
		'pi_purpose':'感情不是一块金枪鱼找另一块金枪鱼，而是金枪鱼找合适的醋饭，是羊肉汤找合适的馍，是一杯葡萄酒找合适的奶酪，是一碗面找合适的肉臊子。',
		'pi_estimated_onboarding':'4','pi_estimated_trade_times':'4','pi_estimated_trade_amount':'4',
		'pi_note':'最近总有传言说我是老涩p，在此我要澄清一下，我不老',
		'pi_background':'明明是因为失望才会离开，却以为是你不够喜欢、人总是珍惜未得到的、却忘了已经拥有的、用一转身离开，用一辈子遗忘！定心加我',
		'pi_appointment_approved':'1','pi_appointment_attachement':''
	})
	head['Content-Type']=m.content_type
	resp=requests.post(f'{host}/back/cmbi/table/piDocument?id={checkID}',headers=head,data=m)
	respJson=eval(re.findall(r'\{.+\}',resp.text)[0])
	try:
		flag=respJson['status']
	except KeyError:
		raise KeyError(f'补充PI资料时返回数据异常： {resp.text}')
	if flag=='000':
		logging.info('补充PI资料成功')
		return 
	else:
		raise ValueError(f'补充PI资料失败：{respJson["message"]}')

#####################################################################
def delAccount(search2='',account='',protectID='',env='uat',ttl=0):
	checkID=getCheckID(search2=search2,account=account,protectID=protectID,env=env,ttl=ttl)
	if not checkID:
		logging.info(f'查询 {search2} 的chechID失败')
		return
	cookieLogined=readCookie(f'openbo_{env}')
	head['Cookie']=cookieLogined
	head['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
	keys={
		'action':'delete',
		'id[]':checkID,
	}
	logging.info(f'删除 {account} ...')
	resp=requests.post(f'{host}/back/cmbi/table/operation',headers=head,data=keys)
	respJson=eval(re.findall(r'\{.+\}',resp.text)[0])
	try:
		flag=respJson['status']
	except KeyError:
		# logging.error(f'删除时返回数据异常： {resp.text}')
		raise KeyError(f'删除时返回数据异常： {resp.text}')
	if flag=='000':
		logging.info(f'{account} 删除成功')
		return
	else:
		raise ValueError(f'{account} 删除失败：{respJson["message"]}')