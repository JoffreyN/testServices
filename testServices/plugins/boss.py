import requests,time,simplejson,logging,json,traceback,re
from requests_toolbelt import MultipartEncoder
from .common import saveCookie,readCookie,getHKid
from bs4 import BeautifulSoup
from random import randint,random

def getConfig_boss(env):
	global host,head,uname,pwd
	host=f'http://{env}-boss.****.*****'
	uname='uatAdmin'
	pwd='Cmbi6688'
	head={
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
		'Cookie':'',
		'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
		'Connection':'close',
		'X-Requested-With':'XMLHttpRequest',
	}

def loginBOSS(env):
	global host,head,uname,pwd
	getConfig_boss(env)
	keys={"account":uname,"password":pwd,"vcode":""}

	for i in range(3):
		resp=requests.post(f'{host}/admin/login/login',headers=head,data=keys,timeout=30)
		# resp=requests.post(f'{host}/admin/adminUser/login',headers=head,data=keys)
		try:
			respJson=resp.json()
			logging.info(f'{env} BOSS登录结果 {respJson}')
		except (json.decoder.JSONDecodeError,simplejson.errors.JSONDecodeError):
			logging.info(f'{env}环境自动登录BOSS系统失败，登录接口返回异常: {resp.text}')
			continue
		if respJson['result']=='1':
			# print(f"resp-header: {resp.headers}")
			try:
				respCookie=resp.headers['set-cookie']
				head['Cookie']=''.join(re.findall(r'PHPSESSID=.+?;',respCookie)+re.findall(r'BOSS-SIGN=.+?;',respCookie))
			except KeyError:
				head['Cookie']='0'
			saveCookie(head['Cookie'],f'boss_{env}')
			return head['Cookie']
		else:
			logging.info(f'{env}环境自动登录BOSS系统失败: {respJson}')
			logging.info(f'2秒后开始第 {i+1} 次重试...')
			time.sleep(2);head['Cookie']=''
	raise Exception(f'{env}环境自动登录BOSS系统失败')

def requests_boss(methmod,path,backType='json',env='uat',**kwargs):
	global host,head,uname,pwd
	getConfig_boss(env.lower())
	cookieLogined=readCookie(f'boss_{env}')
	for i in range(5):
		head['Cookie']=cookieLogined
		try:
			resp=requests.request(methmod,f'{host}{path}',headers=head,timeout=30,**kwargs)
		except requests.exceptions.ConnectionError:
			if i==4:return {"success":False,"msg":"CMS系统接口无响应，请重试。"}
			else:continue
		if 'window.location.href = "/admin/AdminUser/";' in resp.text or 'window.location.href = "/admin/login";' in resp.text:
			logging.info(f'BOSS后台cookie失效，重新登录…')
			print(f'debug{i}: {resp.text}')
			cookieLogined=loginBOSS(env)
			continue
		else:
			if backType=='json':
				try:
					result=resp.json()
				except:
					logging.error(f'{path}返回数据不是json {resp.text}')
					result=resp.text
			elif backType=='text':
				result=resp.text
			elif backType=='soup':
				# with open('temp.hml','w',encoding='utf-8') as f:f.write(resp.text)
				result=BeautifulSoup(resp.text,'lxml')
			return result
#####################################################################
def getApproveStatus(approveId,env='test',pathType='deposite',keyword='业务状态'):
	# 查询资金存入/提取业务状态
	path=f'/casher/{pathType}/approve?id={approveId}'
	soup=requests_boss('GET',path,backType='soup',env=env)
	status=soup.find('div',text=keyword).next_sibling.next_sibling.text.strip()
	return status

def getCasherDeposite(account,env='test'):
	# 根基账户号查询资金存入申请列表
	key={'step_id':'All','aecode':'','accountid':account}
	path='/casher/deposite/list'
	soup=requests_boss('GET',path,backType='soup',env=env,params=key)
	approveIdList=[]
	for tr in soup.select('tr'):
		try:
			status=tr.select_one('.step_id').text.strip()
			if status!='完成':
				approveIdList.append([tr.select('td')[-1].select_one('a')['href'].split('=')[-1],status,tr.select('td')[4].text.strip(),tr.select('td')[6].text.strip(),tr.select('td')[8].text.strip(),tr.select('td')[-2].text.strip()])
				# approveIdList.append(tr.select('td')[-1].select_one('a')['href'])
		except (TypeError,IndexError,AttributeError):
			pass
	return {"success":True,"format":"ttlCheckIdList","result":approveIdList}

def money_check(approveIdList,env='uat',to_step_id='pass',pathType='deposite',bigMoney=1):
	# 审核通过
	if isinstance(approveIdList,str):approveIdList=[approveIdList]
	result={"success":True,"result":[]}
	stepId_dict={
		'deposite':{'RM修改':'1987038','结算审批':'1987040'},
		'withdrawal':{'RM修改':'1987046','RO审批':'1987220','LCD审批':'1987224','结算审批':'1987052'},
	}
	for approveId in approveIdList:
		if bigMoney and pathType=='withdrawal':limitAmountInfo(approveId,env)
		n=1
		while n:
			status=getApproveStatus(approveId,env,pathType)
			approve_note='Stopped By AppAutoTest' if to_step_id=='-2' else f'{status}通过'
			key={'current_step_id':stepId_dict[pathType][status],'to_step_id':to_step_id,'approve_note':approve_note}
			if status=='结算审批' or to_step_id=='-2':n=0
			elif status not in ['RM修改','RO审批','LCD审批']:
				result["result"].append(f'{approveId}审核失败,该申请ID状态异常: {[status]}')
				break
			path=f'/casher/{pathType}/approve?id={approveId}'
			respJson=requests_boss('POST',path,backType='json',env=env,data=key)
			try:
				result["result"].append(f'{approveId} {status} 审核结果:{respJson}')
			except simplejson.errors.JSONDecodeError:
				result["result"].append(f'{approveId} {status} 审核异常: {resp.text}')
				result["success"]=False
	return result

#####################################################################
def limitAmountInfo(approveId,env='uat'):
	# 大额资金提取背景说明
	path=f'/casher/withdrawal/limitAmountInfo?id={approveId}'
	business_no=getApproveStatus(approveId,env=env,pathType='withdrawal',keyword='业务编号')
	data={
		'id':approveId,
		'business_no':business_no,
		'withdraw_background':'Others',
		'withdraw_background_other':'byAutotest',
		'withdraw_background_confirm[]':'Yes',
		'withdraw_reason':'byAutotest',
	}
	respJson=requests_boss('POST',path,backType='json',env=env,data=data)
	logging.info(f'大额资金提取背景说明: {respJson}')

def getAvailableBalance(account,env='uat'):
	# 获取账户资金余额
	path=f'/casher/withdrawal/getAvailableBalance?accountid={account}'
	respJson=requests_boss('GET',path,backType='json',env=env)
	return respJson

def getSettlementAccount(account,currency,env='uat'):
	# 获取账户银行卡信息
	path=f'/casher/withdrawal/getSettlementAccount?accountid={account}&currency={currency}'
	respJson=requests_boss('GET',path,backType='json',env=env)
	return respJson

def getCompanyBankInfo(currency,bankCode,env='uat'):
	# 获取银行信息
	path=f'/casher/withdrawal/getCompanyBankInfo?currency={currency}&bankCode={bankCode}'
	respJson=requests_boss('GET',path,backType='json',env=env)
	return respJson

def withdrawalSave(account,currency,money=None,env='uat'):
	# 资金提取
	path=f'/casher/withdrawal/save?id=&step_id=1987046'
	userInfo=infoJSON(account,env)
	ableBalance=getAvailableBalance(account,env)
	logging.info(f'账户资金数据: {ableBalance}')
	bankCardInfo=getSettlementAccount(account,currency,env)
	logging.info(f'bankCardInfo: {bankCardInfo}')
	bankInfo=getCompanyBankInfo(currency,bankCardInfo['data'][0]['bank_code'],env)
	data={
		'id':'',
		'accountid':account,
		'account_type':userInfo["data"]["AcctType"],
		'aecode':userInfo['data']['AECode'],
		'account_name':userInfo['data']['CName'],
		'account_name_en':userInfo['data']['Name'],
		'currency_hkd':ableBalance['data']['HKD'],
		'currency_usd':ableBalance['data']['USD'],
		'currency_cny':ableBalance['data']['CNY'],
		'current_balance_time':ableBalance['data']['current_balance_time'],
		'withdrawal_currency':currency,
		'withdrawal_amount':money or ableBalance['data'][currency].replace(',',''),
		'withdrawal_file_ro':'',
		'withdrawal_file_lcd':'',
		'remark':'',
		'settlement_card_id':bankCardInfo['data'][0]['card_id'],
		'settlement_bank_code':bankCardInfo['data'][0]['bank_code'],
		'settlement_bank_account':bankCardInfo['data'][0]['bank_account'],
		'settlement_bank_name':bankCardInfo['data'][0]['bank_name'],
		'settlement_bank_account_name':bankCardInfo['data'][0]['bank_account_name'],
		'settlement_bank_currency':currency,
		'settlement_swift_code':bankCardInfo['data'][0]['swift_code'],

		'company_bank_code':bankInfo['data']['bank_code'],
		'company_bank_account':bankInfo['data']['bank_account'],
		'company_bank_account_name':bankInfo['data']['bank_account_name'],
	}
	logging.info(f'资金提取请求数据: {data}')
	respJson=requests_boss('POST',path,backType='json',env=env,data=data)
	return respJson

####################################################################################################################################
def createUesr_CMS(env='test',accType=1,tel=None,email=None,aecode=None,cardType='Passport'):
	import faker,string
	from random import sample
	
	fake=faker.Faker('zh-CN')
	fakeEn=faker.Faker('en')
	if not tel:tel=fake.phone_number()
	if not aecode:aecode='988' 
	if not email:email=f"{''.join(sample(string.ascii_lowercase+string.digits,20))}@{''.join(sample(string.ascii_lowercase+string.digits,15))}.com"
	name_cn=f'{fake.name()}{fake.first_name()}{fake.word()}{fake.first_name()}'
	name_en=f"{env}{fakeEn.name()} {fakeEn.first_name()} {fakeEn.first_name()} {fakeEn.word()}".replace('.','')
	cer_no=getHKid() if cardType=='Hongkong ID' else fake.ssn()
	client_category={1:1,2:22,3:31}
	if accType==1:# 开个人户
		path=f'/cms/cmsClient/create'
		key={
			'id':'','name_cn':name_cn,'name_en':name_en,'name':name_en,'name_settlement':name_en,'fatca_flag':'No','client_category':client_category[accType],'open_date':time.strftime('%Y-%m-%d'),'op_purpose':'Investment','op_remark':'','signed_way':'','remark':'','client_status':'Active','relationship_type':'Account','aecode':aecode,'first_name':name_en,'middle_name':'','last_name':name_en,'alias_name':'','sex_prefix':'','sex':'','birthday':'','birth_place':'','nation':'','country':'HKG','country2':'','education':'4','employment_status':'','employment_note':'','annual_income':'','liquid_assets_held':'','net_worth':'','residential_status':'','residential_details':'','years_of_living':'','source_of_fund[]':'1','fund_details':'','source_of_wealth[]':'1','wealth_details':'','asset_certify':'','monthly_invest_amount':'','language':'cn','certificate_type':cardType,'certificate_no':cer_no,'certificate_issue':'','certificate_name':'','certificate_name_en':'','certificate_register_date':'','certificate_expire_long':'No','certificate_expire_date':'','certificate_country':'HKG','phone_type':'Mobile','contact_type_phone':'2FA','phone_number_countrycode':'86','phone_number_phonearea':'','phone_number_phonenumber':tel,'contact_type_email':'2FA','email':email,'address_country':'HKG','address_state':'','address_city':'','address':fake.address(),'is_proof':'','cor_address_country':'HKG','cor_address_state':'','cor_address_city':'','cor_address':fake.address(),'cor_is_proof':'','publish_4_agency':'','publish_4_code':'','publish_4':'0','publish_5':'0','publish_6':'0','publish_7_name':'','publish_7_relation':'','publish_7':'0','publish_2_name':'','publish_2_account':'','publish_2':'0','publish_3_name':'','publish_3_account':'','publish_3':'0','publish_8':'0','publish_10':'1','publish_1':'1','publish_1_name':'','publish_1_card_id':'','publish_1_tel':'','publish_1_address':'','is_assertion':'0','employer':'','job_years':'','job_position':'','job_remark':'','industry':'','job_status':'2','company_phone_countrycode':'','company_phone_phonearea':'','company_phone_phonenumber':'','company_fax_countrycode':'','company_fax_phonearea':'','company_fax_phonenumber':'','company_address':'','is_employment':'0','qualification':'','client_type':'individual','start_date':'','expire_date':'','is_active':'','is_suitability':'0','sex':'Male','birthday': '1992-08-10'
		}
	elif accType in [2,3]:# 开金融机构户/法团客户
		path=f'/cms/cmsClientCreate/organization'

		key=f"type={accType}&name_cn={name_cn}&name_en={name_en}&name={name_en}&name_settlement={name_en}&fatca_flag=&client_category={client_category[accType]}&bcan_client_type=4&client_status=Active&op_purpose=Investment&op_remark=&open_date={time.strftime('%Y-%m-%d')}&signed_way=online&remark=&purpose_remark=&target_effective_date=&target_transaction_date=&FRR_flag=&aml_risk=low&DDC_flag=Regular Due Diligence&relationship_type=Account&aecode=988&contact_name_of_liaisons={name_en}&contact_position_of_liaisons=农民&liaison_email={email}&liaison_mobile_countrycode=86&liaison_mobile_phonearea=&liaison_mobile_phonenumber={tel}&nature_of_company=1&nature_others=&stock_exchange=&stock_code=&nature_of_business=个体户&indusutry_of_company=1&register_country=HKG&register_date=2002-08-09&name_of_liaisons={name_en}&position_of_liaisons=农民&contact_msg={email};86 {tel}&legal_entity_id=&certificate_type=IncorporationNo&certificate_no={cer_no}&certificate_issue=&certificate_name={name_cn}&certificate_name_en={name_en}&certificate_register_date=2002-08-09&certificate_expire_long=No&certificate_expire_date=&certificate_country=HKG&hkg_certificate_type=IncorporationNo&hkg_name_cn={name_cn}&hkg_name_en={name_en}&certificate_issue_country=HKG&hkg_certificate_no={cer_no}&source_of_initial_money[]=1&predict_net_worth=&predict_liquid_assets_held=&gross_assets=&monthly_invest_amount=&phone_type=Mobile&contact_type_phone=2FA&phone_number_countrycode=86&phone_number_phonearea=&phone_number_phonenumber={tel}&contact_type_email=2FA&email={email}&address_country=HKG&address_state=&address_city=&address={fake.address()}&reg_address_country=HKG&reg_address_state=&reg_address_city=&reg_address={fake.address()}&cor_address_country=HKG&cor_address_state=&cor_address_city=&cor_address={fake.address()}&language=cn".encode('utf-8')


	respJson=requests_boss('POST',path,backType='json',env=env,data=key)
	logging.info(f'createUesr_CMS 结果:{respJson}')
	try:
		result=dict(respJson,**{'name_cn':name_cn,'name_en':name_en,'tel':tel,'email':email,'aecode':aecode,'cer_no':cer_no})
		cif_no=result['data']['cif_no']
	except (IndexError,simplejson.errors.JSONDecodeError,KeyError):
		return {'success':False,'msg':respJson}

	aml_result=cmsClientAml(cif_no,env)
	logging.info(f'cmsClientAml 结果:{aml_result}')
	if aml_result['result']=='1':
		result['aml_result']=True
	else:
		result['aml_result']=False
		result['aml_msg']=aml_result['msg']

	genAcc_result=createAcc(cif_no,cer_no,aecode,env)
	logging.info(f'createAcc 结果:{genAcc_result}')
	if genAcc_result['result']=='1':
		result['账户号']=genAcc_result['data']['accountid']
	else:
		result['创建账户失败']=genAcc_result['msg']

	return result

def cmsClientAml(cif_no,env):
	# cms 反洗钱表格
	key={
		'reason':'From TestServices',
		'cif_no':cif_no,
		'aml_version':'aml_individual_202010',
		'aml_organization':'CMBIS',
		'id':'','client_type':'1',
		'refresh_id':'client-aml-dom',
		'aml_date':time.strftime('%Y-%m-%d'),
		'info':'{"relation_country":"","address_country":"CHN","nationality_country":"CHN","occupation":"22","industry":"1","sole_beneficiary":"YES","KYC":"YES","money_conform":"NO","explain_source_of_wealth":"YES","cancel_CMBI_account":"NO","face_to_face":"YES","is_politician":"NO","on_the_blacklist":"NO","on_the_watchlist":"NO","sanction":"NO","high_risk_level":"NO","final_risk_score":"0","change_aml_risk_level":"不做更改 Not Change","change_reason":"","rm_agree":"同意 Agree","rm_name":"uatAdmin","rm_note":"","ro_agree":"同意 Agree","ro_name":"uatAdmin","ro_note":"","compliance_agree":"同意 Agree","compliance_name":"uatAdmin","compliance_note":"","source_of_fund":"資金來源","source_of_wealth":"財富來源","anticipated_type_volume":"預期的交易類型和交易量"}',
	}
	path=f'/cms/cmsClientAml/save'
	result=requests_boss('POST',path,backType='json',env=env,data=key)
	if type(result)!=dict:
		result={'result':"0",'msg':result}
	return result

def createAcc(cif_no,certificate_no,aecode,env):
	# 开 金融机构户/法团客户 后创建账户号
	key={
		'cif_no':cif_no,
		'certificate_no':certificate_no,
		'select_operation':'create',
		'related_accountid':'',
		'related_account_name':'',
		'related_account_org':'',
		'related_account_category':'',
		'related_account_class':'',
		'related_account_type':'',
		'accountid':f'999{randint(100000,999999)}',
		'account_org[]':'CMBIS',
		'account_class':'Security',
		'related_account':'',
		'account_category':'Normal',
		'omnibus_master_accountid':'',
		'account_type':'Cash',
		'account_status':'Active',
		'aecode':aecode,
		'sgaecode':'',
		'qualification':'Accredited',
		'cif_code':'',
		'account_org_opponent':'',
		'opponent_type':'counterparty',
		'counterparty_account_status':'Active',
	}
	path=f'/cms/cmsBinding/editHolderSave'
	result=requests_boss('POST',path,backType='json',env=env,data=key)
	if type(result)!=dict:
		result={'result':"0",'msg':result}
	return result
####################################################################################################################################

def infoJSON(account,env='test'):
	# 获取账户信息
	path=f'/casher/deposite/infoJSON?accountid={account}'
	result=requests_boss('POST',path,backType='json',env=env)
	if type(result)!=dict:
		result={'result':"0",'msg':result}
	return result


def inmoney_CMS(account,currency,amount,env='test',ttl=1,check=0):
	# cms资金存入
	for i in range(5):
		userInfo=infoJSON(account,env)
		logging.info(f'{account} 账户信息: {userInfo}')
		try:
			userInfo['data']
		except KeyError:
			return {"result":"0","msg":"casher/deposite/infoJSON 接口获取用户信息失败。",'userInfo':userInfo}
		if int(userInfo['result']) and userInfo['data']:
			if not userInfo['data']['EName']:
				return {"result":"0","msg":f"{account} 该账户英文名为空",'userInfo':userInfo}
			elif not userInfo['data']['CName']:
				userInfo['data']['CName']='--'
				# return {"result":"0","msg":f"{account} 该账户中文名为空",'userInfo':userInfo}
			else:
				break
		else:
			if i==4:
				return {"result":"0","msg":"casher/deposite/infoJSON 接口获取用户信息失败。",'userInfo':userInfo}
			else:
				time.sleep(1)
	
	bank_code_dict={'HKD':'238','USD':'238','CNY':'238'}
	bank_account_dict={'HKD':'20089188','USD':'20089199','CNY':'20510161'}
	key={
		"id":"",
		"accountid":account,
		"account_type":userInfo["data"]["AcctType"],
		"aecode":userInfo['data']['AECode'],
		"account_name":userInfo['data']['CName'],
		"account_name_en":userInfo['data']['Name'],
		"deposite_amount":amount,
		"currency":currency,
		"settlement_date":time.strftime('%Y-%m-%d'),
		"deposite_type":"1",
		"remark":"",
		"deposite_voucher_1":("4.png",open("testServices/plugins/4.png","rb"),"image/png"),
		"deposite_voucher_2":"",
		"deposite_voucher_3":"",
		"settlement_bank_account":"1",
		"deposite_bank_code":"238",
		"deposite_bank_account":str(randint(1000000000,9999999999)),
		"deposite_bank_account_name":userInfo['data']['CName'],
		"deposite_currency":currency,
		"third_deposits":"No",
		"bank_code":bank_code_dict[currency],
		"bank_account":bank_account_dict[currency],
		"bank_account_name":"CMB INTERNATIONAL SECURITIES LIMITED-CLIENT ACCOUNT",
		"bank_account_currency":currency,
		"fps_identification_code":"",
		"swift_code":"CMBCHKHH",
		"bank_address":"27/F, Three Exchange Square, 8 Connaught Place, Hong Kong",
	}
	path=f'/casher/deposite/save?id=&step_id=1987038'
	logging.info(f'inmoney_CMS 请求数据: {key}')
	respJson=requests_boss('POST',path,backType='json',env=env,data=key)
	logging.info(f'/casher/deposite/save 返回: {respJson}')
	if type(respJson)==dict:
		try:
			data_id=respJson['data']['id']
		except:
			data_id=None
		result={'success':respJson['result'],'申请ID':data_id,'message':respJson['message'],'审核状态':'未审核'}
		if check:
			result_check=money_check(result['申请ID'],env=env)
			result['审核状态']=result_check['result']
	else:
		result={"result":"0","msg":f"{account} 存入 {amount}{currency} 异常: {respJson}"}
	return result

########################################################################################################################################
def getMailRecord(account,env='uat',start_date=None,end_date=None,keyword='登录通知',timeLimit=180):
	date=time.strftime("%Y-%m-%d")
	if not start_date:start_date=date
	if not end_date:end_date=date
	param={
		'key':'accountid',
		'search':account,
		'start_date':start_date,
		'end_date':end_date,
	}
	path='/panel/mailRecord/list'
	soup=requests_boss('GET',path,backType='soup',env=env,params=param)
	mailRecord=[]
	for tr in soup.select_one('table').select_one('tbody').select('tr'):
		acc=tr.select('td')[1].text.strip()
		mailTxt=tr.select('td')[3].text.strip()
		sendTime=tr.select('td')[4].text.strip()
		mailid=tr.select('td')[-1].select_one('a')['href'].split('=')[-1]
		if re.findall(keyword,mailTxt) and (acc==account) and (int(time.time())-time.mktime(time.strptime(sendTime,'%Y-%m-%d %X'))<timeLimit):#3分钟内的:
			mailRecord.append((acc,mailTxt,sendTime,mailid))
	return mailRecord
########################################################################################################################################
# 开通市场
def openMarket_boss(account,env='uat'):
	respJson=cmsSearch_quick(account,env)
	result=[]
	if len(respJson['data']['list'])>0:
		checkid=respJson['data']['list'][0]['url'].split('=')[-1]
		path=f'/cms/cmsAccount/editMarket?id={checkid}'
		for mk in ['SHA','SZA','USA','FUN','BOND','SP']:
			key=f'id={checkid}&market[]={mk}'
			respJson=requests_boss('POST',path,backType='json',env=env,data=key)
			msg=f'{account} 开通市场{mk}结果: {respJson}'
			result.append(msg)
			logging.info(msg)
		return result

def rpqScore(cif_no,env='uat'):
	path='/console/Count/rpqScore'
	data=f'reason=no reason&cif_no={cif_no}&rpq_version=rpq_individual_202101&id=&rpq_date={time.strftime("%Y-%m-%d")}&info='+'{"q1":"5","q2":"4","q3":"4","q4":"5","q5":"4","q6":"5","q7":"5","q8":"5","q9_1":1,"q9_1_1":"3","q9_1_2":"2","q9_2":1,"q9_2_1":"3","q9_2_2":"2","q9_3":1,"q9_3_1":"3","q9_3_2":"2","q9_4":1,"q9_4_1":"3","q9_4_2":"2","q9_5":1,"q9_5_1":"3","q9_5_2":"2","q9_6":1,"q9_6_1":"3","q9_6_2":"2","q9_7":1,"q9_7_1":"3","q9_7_2":"2","q9_8":1,"q9_8_1":"3","q9_8_2":"2","q9_9":1,"q9_9_1":"3","q9_9_2":"2","q9_10":1,"q9_10_1":"3","q9_10_2":"2","q9_11":1,"q9_11_1":"3","q9_11_2":"2","q9_12":1,"q9_12_1":"3","q9_12_2":"2","q9_13":1,"q9_13_1":"3","q9_13_2":"2","q9_14":1,"q9_14_1":"3","q9_14_2":"2","q9_15":1,"q9_15_1":"3","q9_15_2":"2","q9_16":1,"q9_16_1":"3","q9_16_2":"2"}&client_type=1'
	respJson=requests_boss('POST',path,backType='json',env=env,data=data)
	logging.info(f'{cif_no} rpqScore结果: {respJson}')
	# return f'{account}rpqScore结果: {respJson}'

def rpqSave(account,env='uat'):
	cif_no=getCifNo(account,env)
	rpqScore(cif_no,env)
	path='/cms/cmsClientRpq/save'
	data=f'reason=no reason&cif_no={cif_no}&rpq_version=rpq_individual_202101&id=&rpq_date={time.strftime("%Y-%m-%d")}&client_type=1&rpq_result=Aggressive&score=44&business_vars='+'{"q1":5,"q2":4,"q3":4,"q4":5,"q5":4,"q6":5,"q7":5,"q8":5,"q9":[[1,3,2],[1,3,2],[1,3,2],[1,3,2],[1,3,2],[1,3,2],[1,3,2],[1,3,2],[1,3,2],[1,3,2],[1,3,2],[1,3,2],[1,3,2],[1,3,2],[1,3,2],[1,3,2]]}&work_id='
	respJson=requests_boss('POST',path,backType='json',env=env,data=data)
	logging.info(f'{account} rpq结果: {respJson}')
	return f'{account} rpq结果: {respJson}'

########################################################################################################################################
# cms重置密码
def cms_resetpwd(account,env='uat'):
	path='/panel/selfReset/save'
	key={
		'accountid':account,
		'verifyway':'客户邮件',
		'is_notify':'1',
	}
	respJson=requests_boss('POST',path,backType='json',env=env,data=key)
	logging.info(f'cms重置密码 结果: {respJson}')
	# {'result': '1', 'message': 'success', 'data': {'business_id': '77414'}, 'now': '2021-08-16 16:25:28'}
	return respJson if respJson else {'result': '0', 'message': f'{env} BOSS系统返回数据异常', 'respJson': respJson}

def getPwd_from_mail(mailid,env='uat',mod='reset'):
	path=f'/panel/mailRecord/view?id={mailid}'
	soup=requests_boss('GET',path,backType='soup',env=env)
	if mod=='reset':# 获取重置的密码
		pwd=soup.select('strong')[1].text
	elif mod=='first':# 获取初始密码
		pwd=soup.select('td')[1].text
	return pwd
########################################################################################################################################
# 查询账户的证件id
def cmsSearch_quick(account,env='uat'):
	path=f'/cms/cmsSearch/quick'
	key={'searching':account}
	respJson=requests_boss('POST',path,backType='json',env=env,data=key)
	# {'result': '1', 'message': 'success', 'data': {'list': [{'title': '472775 自动化测试后台开户', 'url': '/cms/cmsAccount/check?id=26264'}]}, 'now': '2021-09-01 17:46:13'}
	return respJson

def cmsAccount_check(checkid,backInfo='cif_no',env='uat'):
	path=f'/cms/cmsAccount/check?id={checkid}'
	soup=requests_boss('GET',path,backType='soup',env=env)
	ele=soup.find('div',text='账户持有人').parent.parent
	logging.info(f'{checkid} 对应账户持有人: {[ele.select_one(".a-left").text.strip()]}')
	if backInfo=='cif_no':
		result=ele.select_one('.a-right').text.strip()
		logging.info(f'cif_no查询结果: {[result]}')
		result=result.split()[0]
	return result

def getCifNo(account,env):
	respJson=cmsSearch_quick(account,env)
	if len(respJson['data']['list'])>0:
		checkid=respJson['data']['list'][0]['url'].split('=')[-1]
		cif_no=cmsAccount_check(checkid,env=env)
		return cif_no

def getCardsID(account,env='uat'):
	respJson=cmsSearch_quick(account,env)
	cards=None
	try:
		if respJson['data']['list']:
			checkid=respJson['data']['list'][0]['url'].split('=')[-1]
			cif_no=cmsAccount_check(checkid,env=env)

			path=f'/cms/cmsClientCertificate/refresh?cif_no={cif_no}'
			soup=requests_boss('GET',path,backType='soup',env=env)
			cards=[]
			for tr in soup.select_one('tbody').select('tr'):
				card_type=tr.select('td')[1].text.strip()
				card_id=tr.select('td')[2].text.strip()
				cards.append((card_type,card_id))
			logging.info(f'cards: {[cards]}')
			# [('香港居民身份证', 'R625079(2)'), ('中国居民身份证', '421022197904201518')]
		else:
			logging.info(f'查询账户{account}的checkid失败: {respJson}')
	except Exception:
		traceback.print_exc()
		logging.error(f'cmsSearch_quick 查询失败: {respJson}')
		cards=None
	return cards

# 查询账户结算银行卡
def getBankAccount(account,env='uat'):
	path=f'/cms/cmsAccount/bankAccount?accountid={account}'
	soup=requests_boss('GET',path,backType='soup',env=env)
	bankcard_dict={}
	try:
		for tr in soup.select('tbody')[0].select('tr'):
			bankName=tr.select('td')[0].text.strip()
			bankCode=tr.select('td')[1].text.strip()
			bankAccName=tr.select('td')[2].text.strip()
			curr=tr.select('td')[3].text.split()[0]
			bankcard_dict[bankCode]=[bankName,bankAccName,curr]
	except:
		logging.info(f'查询账户{account}结算银行卡失败: {soup.text}')
	return bankcard_dict

# 新增结算银行卡
def addBankcard(account,bankCode,curr='MTC',bankType='238',env='uat'):
	path=f'/cms/cmsClientBankAccount/edit?accountid={account}'
	# bankType 238:招商银行(香港)分行;020:招商永隆银行;353:中国民生银行(香港)分行;003:渣打银行(香港)有限公司
	respJson=cmsSearch_quick(account,env)
	if len(respJson['data']['list'])>0:
		checkid=respJson['data']['list'][0]['url'].split('=')[-1]
		cif_no=cmsAccount_check(checkid,env=env)
		userInfo=infoJSON(account,env)
		key={
			'cif_no':cif_no,
			'bank_code':bankType,
			'bank_account':bankCode,
			'bank_account_name':userInfo['data']['Name'],
			'deal_currency':curr,
			'belong_place':'HK',
			'swift_code':'',
			'remark':'',
			'priority':'0',
		}
	respJson=requests_boss('POST',path,backType='json',env=env,data=key)
	# {'result': '1', 'message': 'success', 'data': {'list': [{'title': '472775 自动化测试后台开户', 'url': '/cms/cmsAccount/check?id=26264'}]}, 'now': '2021-09-01 17:46:13'}
	return respJson

########################################################################################################################################
def createESOP(account,env='uat'):
	path='/cms/cmsBinding/editHolderSave'
	respJson=cmsSearch_quick(account,env)
	if len(respJson['data']['list'])>0:
		checkid=respJson['data']['list'][0]['url'].split('=')[-1]
		logging.info(f'{env}环境 {account} checkID: {checkid}')

		cif_no=cmsAccount_check(checkid,env=env)
		logging.info(f'{env}环境 {account} cif_no: {cif_no}')

		respJson=cmsClientAml(cif_no,env)
		logging.info(f'{env}环境 {cif_no} 反洗钱结果: {respJson}')

		card_id=getCardsID(account,env)[0][1]
		logging.info(f'{env}环境 {account} card_id: {card_id}')

		key={
			'cif_no':cif_no,
			'certificate_no':card_id,
			'select_operation':'create',
			'related_accountid':'',
			'related_account_name':'',
			'related_account_org':'',
			'related_account_category':'',
			'related_account_class':'',
			'related_account_type':'',
			'accountid':f'E{account.upper().replace("M","")}',
			'account_org[]':'CMBIS',
			'account_class':'ESOP',
			'tap_related_account':'',
			'account_category':'Omnibus',
			'omnibus_master_accountid':'340552',
			'account_type':'Cash',
			'account_status':'Active',
			'aecode':'988',
			'cif_code':'',
			'account_org_opponent':'',
		}
		respJson=requests_boss('POST',path,backType='json',env=env,data=key)
		return respJson
		# {'result': '1', 'message': 'success', 'data': {'id': '26300', 'accountid': 'E200075', 'inferno_id': '', 'inferno_accountid': '', 'inferno_cmbiaccountcode': '', 'inferno_accounttype': '', 'account_name': 'Qi Wu', 'account_name_en': 'Qi Wu', 'account_name_cn': '七五', 'account_name_settlement': 'Qi Wu', 'account_category': 'Normal', 'account_type': 'Cash', 'account_class': 'ESOP', 'account_org': 'CMBIS', 'remark': '', 'account_status': 'Active', 'discretionary_flag': '', 'discretionary_manager': '', 'open_date': '2021-09-02', 'active_date': '', 'active_reason': '', 'close_date': '', 'account_contact': '', 'account_remark': '', 'welcome_letter': 'No', 'client_type': '1', 'client_binded': 'Yes', 'aecode': '988', 'is_sync': '1', 'standing_authority_date': '2022-09-01', 'tap_related_account': '', 'open_way': '', 'channel': 'TTL', 'status': '1', 'create_time': '2021-09-02 11:34:40', 'create_user': '1060', 'update_time': '2021-09-02 11:34:40', 'update_user': '1060'}, 'now': '2021-09-02 11:34:53'}
	else:
		logging.info(f'{env}环境查询{account}checkID失败: {respJson}')
		return {'result': '0', 'message': '创建失败'}

###################### 切换开户渠道 ####################################################
def changeChannel(channel='TTL',env='uat'):
	path=f'/master/masterSetting/edit'
	data={
		'id':'14',
		'key_code':'CHANNEL',
		'key_value':channel.upper(),
		'remark':'证券系统渠道(ABC/TTL)',
	}
	respJson=requests_boss('POST',path,backType='json',env=env,data=data)
	logging.info(f'{env} 切换开户渠道为 {channel} 结果: {respJson}')

###################### 导入结单 ####################################################
def clientInvoice(date,env='uat'):
	path=f'/panel/clientInvoice/import'
	data={'import_date':date}
	respJson=requests_boss('POST',path,backType='json',env=env,data=data)
	logging.info(f'{env} 导入结单结果: {respJson}')
	return respJson

if __name__ == '__main__':
	account='918138'
	env='test'
	# respJson=cmsSearch_quick(account,env)
	# checkid=respJson['data']['list'][0]['url'].split('=')[-1]
	# cif_no=cmsAccount_check(checkid,env=env).split()[0]
	cif_no='100019462'
	card_id=getCardsID(cif_no,env)[0][1]