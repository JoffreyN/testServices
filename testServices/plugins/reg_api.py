import logging,time,faker,requests,string
from random import sample,randint
from .common import saveFile,encryption,getHKid
from .database import excuteSQL,delete_redis
from .openbo import getCheckID,checkBO,manualActivate,amlTable,piDocument
from .myAPI import resetpwd,login_acc,w8Submit,openMarket,setPwdTel,changeAccountPwd,sendSMS,smsCodeLogin
from .boss import getMailRecord,getPwd_from_mail,changeChannel,getCifNo


newPwd='aaaa1111'
head={
	'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
	'Connection':'close',
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67',
}
sign_img='data:image/png;base64,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'

def openStatus(args):
	url=f'http://trade-{args.env}.****.*****/app/foOpenAccount/openStatus'
	data={
		'token':args.token,
		'table_class':'personal',
		'lang':'cn',
	}
	logging.info(f'请求URL: {url}')
	logging.info(f'请求数据: {data}')
	resp=requests.post(url,headers=head,data=data,timeout=30)
	respJson=resp.json()
	logging.info(f'响应数据: {respJson}')
	# {"result":1,"data":{"isSecondOpen":"N","isOpened":"N"},"message":"success"}
	return respJson['result']

def checkTable(args):
	url=f'http://trade-{args.env}.****.*****/app/foOpenAccount/checkTable'
	data={
		'token':args.token,
		'lang':'cn',
	}
	logging.info(f'请求URL: {url}')
	logging.info(f'请求数据: {data}')
	resp=requests.post(url,headers=head,data=data,timeout=30)
	respJson=resp.json()
	logging.info(f'响应数据: {respJson}')
	# {"result":"1","message":"查询成功","data":{"cifData":[],"szca_switch":1,"first_open":"Y","change_card":"Y","can_view":"N","can_edit":"N","table_status":"none","user_mobcountry":"86","user_mobile":"13987456984","aaaaaaa":null,"bbbbbbb":null}}
	if respJson['data']['cifData']==[] and respJson['data']['first_open']=="Y":
		return 1
	else:
		args.reason='该手机号已开过户'
		# raise Exception(f'checkTable 返回数据异常')

def save_first(args):
	url=f'http://trade-{args.env}.****.*****/app/foOpenAccount/save'
	data={
		'noLoading':'1','table_type':'1','card_type':'HKID','address_as_card':'0','email':'','aum_card':'','aum_mobile':'','mk_hk':'1','mk_sha':args.market,'mk_sza':args.market,'mk_us':args.market,'mk_otc':args.market,'card_photo1':'202108/20210819550671162935214735.jpg','card_photo2':'','sex':'1','nationality':'1','nationality_other':'','publish_1':'1','publish_2':'1','publish_3':'1','publish_4':'1','publish_5':'1','publish_6':'1','publish_7':'1','publish_8':'1','publish_9':'1','publish_9_1':'1','publish_9_2':'1','publish_9_3':'1','publish_10':'1','education':'2','asset_liquid':'11','source_fund':'1','source_wealth':'1','monthly_invest_amount':'1','ac_cash':'1','der_1':'','der_2':'','der_3':'','der_4':'1','contact_address':'','mobcountry':'86','op_purpose':'1','op_purpose_due':'','q1':'','q2':'','q3':'','q4':'','q5':'','q6':'','q7':'','q8':'','q9':'','q10':'','q11':'','q12':'','sign_method':'online','is_know_risk':'','card_issue':'HKG','card_address':'','address_certify':'202108/20210819747861162935227829.jpg','address_country':'HKG','card_org':'','op':'h5','channel':'','lang':'cn','birth_place':'中国','card_expires_begin':'1984-06-01','card_expires_end':'2050-01-01','birthday':'1984-06-01','hold_HK_ID':'0','hold_China_ID':'0','skipResponseErrorToast': 'true',
		'invite_code':args.invite_code,
		'aum_account':args.aum_account,
		'table_status':args.table_status,
		'ac_margin':str(args.margin),
		'address':args.address,#'广东省香港区大公鸡',
		'mobile':args.tel,#'13987456984',
		'name_cn':args.name_cn,#'杨国庆',
		'name_en':args.name_en,#'samn yang',
		'card_id':args.card_id,#'45678623454576756',
		'token':args.token,#'BA31BC9BE6A8D1B66268AE95A7AE924C',
		'serial_num':f'FromZP_{str(time.time())}',#'dUm5aSaddsX1PV9dKUYqIQTX3Yph1I4p',
	}
	logging.info(f'请求URL: {url}')
	logging.info(f'请求数据: {data}')
	resp=requests.post(url,headers=head,data=data,timeout=30)
	respJson=resp.json()
	logging.info(f'响应数据: {respJson}')
	args.table_no=respJson['data']['table_no']
	args.table_token=respJson['data']['table_token']
	if respJson['result']!='1':
		raise Exception(f'save_first 返回数据异常')
	return args

def checkEmail(args):
	url=f'http://trade-{args.env}.****.*****/app/foOpenAccount/checkEmail'
	data={
		'token':args.token,#'BA31BC9BE6A8D1B66268AE95A7AE924C',
		'email':args.email,#'fxghxdhdhfugkj@fhfdyjdghj.com',
		'card_id':args.card_id,#'45678623454576756',
		'lang':'cn',
	}
	logging.info(f'请求URL: {url}')
	logging.info(f'请求数据: {data}')
	resp=requests.post(url,headers=head,data=data,timeout=30)
	respJson=resp.json()
	logging.info(f'响应数据: {respJson}')
	# {"result":"1","message":"success","data":""}
	# {'result': '0', 'message': '此邮箱已被其他用户注册，请更换邮箱', 'data': ''}
	if respJson['result']!='1':
		args.reason=respJson['message']
		# raise Exception(f'checkEmail 返回数据异常')

def sign(args):
	url=f'http://trade-{args.env}.****.*****/app/foOpenAccount/sign'
	data={
		'file_code':'base64',
		'file_type':'png',
		'file_data':args.sign_img,#'sign_img',
		'table_no':args.table_no,#'2021081913513131583',
		'table_token':args.table_token,#'7393f12d7731f1650092dc3e72e29b1b',
		'lang':'cn',
	}
	logging.info(f'请求URL: {url}')
	logging.info(f'请求数据: {data}'.replace(sign_img,'sign_img'))
	resp=requests.post(url,headers=head,data=data,timeout=30)
	respJson=resp.json()
	logging.info(f'响应数据: {respJson}')
	# {"result":"1","message":"签署成功","data":{"url":"http:\\uat-app.****.*****\data\sign\202108\2021081913513131583_20210819015642.png"}}
	if respJson['result']!='1':
		raise Exception(f'sign 返回数据异常')

def save(args):
	url=f'http://trade-{args.env}.****.*****/app/foOpenAccount/save'
	data={
		'table_type':'1','card_type':'HKID','address_as_card':'0','mobcountry':'86','op_purpose':'1','op_purpose_due':'','publish_1':'1','publish_2':'1','publish_3':'1','publish_4':'1','publish_5':'1','publish_6':'1','publish_7':'1','publish_8':'1','publish_9':'1','publish_9_1':'1','publish_9_2':'1','publish_9_3':'1','publish_10':'1','education':'2','asset_liquid':'11','source_fund':'1','source_wealth':'1','monthly_invest_amount':'1','ac_cash':'1','der_1':'','der_2':'','der_3':'','der_4':'1','q1':'','q2':'','q3':'','q4':'','q5':'','q6':'','q7':'','q8':'','q9':'','q10':'','q11':'1','q12':'4','sign_method':'online','is_know_risk':'1','aum_card':'','aum_mobile':'','mk_hk':'1','mk_sha':args.market,'mk_sza':args.market,'mk_us':args.market,'mk_otc':args.market,'card_photo1':'202108/20210819550671162935214735.jpg','card_photo2':'','sex':'1','nationality':'1','nationality_other':'','birthday':'1984-06-01','birth_place':'中国','card_issue':'HKG','card_address':'','address_certify':'202108/20210819747861162935227829.jpg','address_country':'HKG','card_org':'','card_expires_begin':'1984-06-01','card_expires_end':'2050-01-01','job_status':'1','job':'1','com_industry':'1','job_status_other':'','retired_reasons':'','publish_1_name':'','publish_1_card_id':'','publish_1_tel':'','publish_1_address':'','publish_1_us':'','publish_4_agency':'','publish_4_code':'','publish_2_name':'','publish_2_account':'','publish_3_name':'','publish_3_account':'','publish_7_name':'','publish_7_relation':'','revenue':'12','asset':'11','source_fund_note':'','source_wealth_note':'','pi_certify':'','settlement_notify_mail':'1','settlement_notify_postal':'0','q13':'4','q14':'4','q15':'2','q31':'5','q32':'5','q33[0]':'2','q33[1]':'3','q33[2]':'4','q34':'','binded_bankname':'','binded_bankcode':'','binded_cardno':'','binded_certify':'','channel':'','lang':'cn','hold_HK_ID':'0','hold_China_ID':'0','skipResponseErrorToast': 'true',
		'crs_array':'[{"crs_area":"HK","crs_notin_type":"","crs_tin":"'+args.card_id+'","crs_notin_note":"","crs_certify":""}]',
		'invite_code':args.invite_code,
		'aum_account':args.aum_account,
		'table_status':args.table_status,
		'ac_margin':str(args.margin),
		'address':args.address,#'广东省香港区大公鸡',
		'mobile':args.tel,#'13987456984',
		'name_cn':args.name_cn,#'杨国庆',
		'name_en':args.name_en,#'samn yang',
		'card_id':args.card_id,#'45678623454576756',
		'token':args.token,#'BA31BC9BE6A8D1B66268AE95A7AE924C',
		'email':args.email,#'fxghxdhdhfugkj@fhfdyjdghj.com',
		'contact_address':args.address,#'广东省香港区大公鸡',
		'home_tel':args.home_tel,#'026-9874651',
		'com_name':args.com_name,#'发动机黑胡椒有限公司',
		'binded_cardname':args.name_en,#'samn yang',
		'sign_img':args.sign_img,#'sign_img',
		'table_no':args.table_no,#'2021081913513131583',
		'table_token':args.table_token,#'7393f12d7731f1650092dc3e72e29b1b',

	}
	logging.info(f'请求URL: {url}')
	logging.info(f'请求数据: {data}'.replace(sign_img,'sign_img'))
	resp=requests.post(url,headers=head,data=data,timeout=30)
	respJson=resp.json()
	logging.info(f'响应数据: {respJson}')
	# {"result":"1","message":"success","data":{"table_no":"2021081913513131583","table_token":"7393f12d7731f1650092dc3e72e29b1b","table_pdf":"http:\\uat-app.****.*****\file\pdf\table?no=2021081913513131583&expire=20210826&key=92f71c339d28534d1815ab64d0240a8a&name=2021081913513131583.pdf&timestamp=1629352601","w8_pdf":"http:\\uat-app.****.*****\file\pdf\w8?no=2021081913513131583&expire=20210826&key=92f71c339d28534d1815ab64d0240a8a&name=2021081913513131583.pdf&timestamp=1629352601","crs_pdf":"http:\\uat-app.****.*****\file\pdf\crs?no=2021081913513131583&expire=20210826&key=92f71c339d28534d1815ab64d0240a8a&name=2021081913513131583.pdf&timestamp=1629352601"}}
	if respJson['result']!='1':
		raise Exception(f'save 返回数据异常')
	return respJson['message']

def createNotice(args):
	url=f'http://trade-{args.env}.****.*****/app/foOpenAccount/createNotice'
	data={
		'table_no':args.table_no,#'2021081913513131583',
		'table_token':args.table_token,#'7393f12d7731f1650092dc3e72e29b1b',
		'lang':'cn',
	}
	logging.info(f'请求URL: {url}')
	logging.info(f'请求数据: {data}')
	resp=requests.post(url,headers=head,data=data,timeout=30)
	respJson=resp.json()
	logging.info(f'响应数据: {respJson}')
	# {"result":"1","message":"签署成功","data":{"url":"http:\\uat-app.****.*****\data\sign\202108\2021081913513131583_20210819015642.png"}}
	if respJson['result']!='1':
		raise Exception(f'createNotice 返回数据异常')

####################################################################################################
def reg_api(args):
	regTypeDic={0:'一般投资者',1:'专业投资者'}
	table_status=('personal','background','marketchoose','der','simpleRpq','riskannounce','addHk','sign','handwrite')
	args.sign_img=sign_img
	fake=faker.Faker('zh_CN')
	fakeEn=faker.Faker('en')
	if not args.tel:args.tel=fake.phone_number()
	if not args.email:args.email=f"{''.join(sample(string.ascii_lowercase+string.digits,20))}@{''.join(sample(string.ascii_lowercase+string.digits,15))}.com"
	args.cnName=args.name_cn=f'{fake.name()}{fake.first_name()}{fake.word()}{fake.first_name()}'
	args.enName=args.name_en=f"{args.env}{fakeEn.name()} {fakeEn.first_name()} {fakeEn.first_name()} {fakeEn.word()}".replace('.','')
	args.cardID=args.card_id=getHKid()
	# args.cardID=args.card_id=fake.ssn()
	args.address='香港'
	# args.address=fake.address()
	args.com_name=fake.company()
	args.home_tel=f'0{randint(10,99)}-{randint(10000000,99999999)}'

	_s='TTL-' if args.ttl else ''
	_m_desc='已' if args.margin else '未'
	args.regInfo=f"-----{_s}{args.env.upper()}环境 {regTypeDic[args.pi]} {time.strftime('%Y-%m-%d %X')} -----\n手机号： {args.tel}\n{_m_desc}勾选保证金账户\n中文名: {args.name_cn}\n英文名: {args.name_en}\n证件ID: {args.card_id}\n邮箱号： {args.email}\n"
	saveFile(args.regInfo)
	saveFile(f'出生地址: {args.address}')
	saveFile('出生日期： 1984-06-01')
	saveFile(f'联系地址: {args.address}')
	saveFile(f'公司名称: {args.com_name}')

	sendSMS(args)
	args.token,reason=smsCodeLogin(args,vcode='8888')
	# isDefend(args)
	openStatus(args)
	
	checkTable(args)
	if args.reason:return args

	args.table_status='card'
	args=save_first(args)

	checkEmail(args)
	if args.reason:return args

	for i in table_status:
		args.table_status=i
		if i=='handwrite':sign(args)
		result=save(args)
	if result=='success':
		createNotice(args)
		return args


def reg_main(args):
	start=time.perf_counter()
	areaCodeDic={'zh_CN':'86','zh_HK':'852'}
	args.areaCode=areaCodeDic[args.location]
	args=reg_api(args)
	if args.reason:return args

	acc_type='ttl' if args.ttl else 'abc'
	if args.check:
		logging.info('开始审核……')
		checkID=0
		end=4
		for i in range(1,end):
			if i==2:
				amlTable(checkID,args.env,args.ttl)#反洗钱表格
				if args.pi:piDocument(checkID,args.env,args.ttl)#补充PI资料
			if i==end-1:changeChannel(acc_type,args.env)
			checkID,args.reason=checkBO(args.tel,i,checkID,args.env,args.ttl)
			if args.reason:return args
			time.sleep(1)
		_reginfo='审核完成！'
		saveFile(_reginfo)
		time.sleep(3)
		args.regInfo=f'{args.regInfo}{_reginfo}\n'
		active=0
		if args.pi:
			#专业投资者无激活这一步骤，审核完就是已激活状态
			_reginfo='激活完成！'
			saveFile(_reginfo)
			args.regInfo=f'{args.regInfo}{_reginfo}\n'
			active=1
		else:
			if args.active:
				args.reason=manualActivate(checkID,args.env,args.ttl)
				if args.reason:return args
				_reginfo='激活完成！'
				saveFile(_reginfo)
				args.regInfo=f'{args.regInfo}{_reginfo}\n'
				active=1
		if active:
			accList=getCheckID(search2=args.tel,getAcclist=1,env=args.env,ttl=args.ttl)
			_reginfo=f'{args.tel} 对应户口号 {" ".join(accList)}'
			saveFile(_reginfo)
			args.regInfo=f'{args.regInfo}{_reginfo}\n'
			args.acc=[i for i in accList if 'M' not in i][0]
			try:args.Macc=[i for i in accList if 'M' in i][0]
			except IndexError:args.Macc=''
			accList_pwd=[]
			time.sleep(10)
			for _acc in accList:
				mailid=getMailRecord(_acc,env=args.env,keyword='默认激活码|默認激活碼',timeLimit=18000)[0][-1]
				firstpwd=getPwd_from_mail(mailid,env=args.env,mod='first')
				_reginfo=f'{_acc} 初始密码 {firstpwd}'
				args.regInfo=f'{args.regInfo}{_reginfo}\n'
				saveFile(_reginfo)
				accList_pwd.append([_acc,firstpwd])
			
			if args.setPwd:
				for acc_pwd in accList_pwd:
					acc,pwd=acc_pwd

					cif_no=getCifNo(acc,args.env)
					delete_redis(f'CIF_CMS_2_{cif_no}',args.env)

					sessionDic=login_acc(acc,pwd,args.env,args.ttl)
					if sessionDic['success']:
						retResult=changeAccountPwd(sessionDic,pwd,newPwd,args.env)
						if retResult['success']:
							_reginfo=f'{acc} 已重置密码为 {newPwd}'
							saveFile(_reginfo)
							args.regInfo=f'{args.regInfo}{_reginfo}\n'
							sessionDic=login_acc(acc,newPwd,args.env,args.ttl)
							if sessionDic:
								if args.w8:
									# 提交w8
									w8Submit(sessionDic,args.env)
									_reginfo=f'{acc} 提交w8成功'
									saveFile(_reginfo,0)
									args.regInfo=f'{args.regInfo}{_reginfo}\n'
								# if args.market:
								# 	# 开通市场
								# 	openMarket(sessionDic,args.env)
								# 	_reginfo=f'{acc} 开通市场成功'
								# 	saveFile(_reginfo,0)
								# 	args.regInfo=f'{args.regInfo}{_reginfo}\n'
							else:
								_reginfo=f'{acc} 重置密码后登陆失败\n'
								saveFile(_reginfo)
								args.regInfo=f'{args.regInfo}{_reginfo}\n'
						else:
							_reginfo=f'{acc} 重置密码失败: {retResult}\n'
							saveFile(_reginfo)
							args.regInfo=f'{args.regInfo}{_reginfo}\n'
					else:
						_reginfo=f'{acc} 使用初始密码 {pwd} 登录失败\n'
						saveFile(_reginfo)
						args.regInfo=f'{args.regInfo}{_reginfo}\n'

				if args.setPwdTel:
					#设置手机账号 登录密码
					status,reason=setPwdTel(args,newPwd)
					if status:
						_reginfo=f'{args.tel} 设置密码成功 新密码 {newPwd}'
						saveFile(_reginfo)
						args.regInfo=f'{args.regInfo}{_reginfo}\n'
					else:
						logging.info(f'{args.tel} 设置密码失败 {reason}')
			else:
				pass
		create_at=time.strftime('%Y-%m-%d %X')
		is_pi=1 if args.pi else 0
		saveSQL=f"INSERT INTO interfaceTest_data.regInfo (acc_type,create_at,env,is_pi,acc,acc_pwd,Macc,Macc_pwd,phone,email,cn_name,en_name,card_id,birth_date) VALUES ('{acc_type}','{create_at}','{args.env}',{is_pi},'{args.acc}','{newPwd}','{args.Macc}','{newPwd}','{args.tel}','{args.email}','{args.cnName}','{args.enName}','{args.cardID}','1984-06-01');"
		excuteSQL(sql=saveSQL,env='test')
	t=time.strftime('%M{m}%S{s}',time.gmtime(time.perf_counter()-start)).format(m='分',s='秒')
	_reginfo=f"用时：{t}\n----- 开户完成! {time.strftime('%Y-%m-%d %X')} -----\n"
	saveFile(_reginfo)
	args.regInfo=f'{args.regInfo}{_reginfo}'
	return args