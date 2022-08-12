from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db.models import Q
from django.utils import timezone

import re,traceback,requests,json,time,HTMLReport,faker
from random import choice,random
from uuid import uuid1
from rediscluster import RedisCluster

from testServices.models import ViewXY
from .plugins.myAPI import *
from .plugins.reg_api import reg_main
from .plugins.common import Args,ftp_store_file
from .plugins.boss import *
from .plugins.openbo import getCheckID,loginBO
from .plugins.database import *
# from .plugins.parse_pb2_data import parseData
from .plugins.cmdCenter import getProcess,server_appium_wda,start_UItest,kill_processID

def delete_session(request):
	# 登录之后获取获取最新的session_key
	session_key=request.session.session_key
	# 删除非当前用户session_key的记录
	for session in Session.objects.filter(~Q(session_key=session_key),expire_date__gte=timezone.now()):
		data=session.get_decoded()
		if data.get('_auth_user_id', None)==str(request.user.id):
			session.delete()

def accLogin(request):
	collectIP(request)
	if request.method=='GET':
		return render(request,'login.html')
	else:
		username=request.POST['username']
		password=request.POST['password']
		user=authenticate(username=username, password=password)
		if user is not None:
			login(request, user)
			delete_session(request)
			return redirect('/index')
		else:
			return render(request, 'login.html',{'err_msg':'用户名或密码错误。'})

def accLogout(request):
	collectIP(request)
	logout(request)
	return redirect('/login')

@login_required
def createuser(request):
	# collectIP(request)
	if request.user.username not in ['admin','zp']:
		return render(request,"index.html",{'alert_msg':'权限不足。','jumpto':'/index'})

	if request.method=='GET':
		return render(request,'createUser.html')
	else:
		username=request.POST['username']
		password=request.POST['password']
		user=User.objects.create_user(username,'',password)
		user.save()
		return render(request,'createUser.html',{'alert_msg':'创建成功'})

@login_required
def changepwd(request):
	collectIP(request)
	if request.method=='GET':
		return render(request,'changePwd.html')
	else:
		old_password=request.POST['old_password']
		new_password=request.POST['new_password']
		new_password2=request.POST['new_password2']
		if new_password!=new_password2:
			return render(request,"changePwd.html",{'err_msg':'两次输入的密码不一致。'})
		if new_password=='123456':
			return render(request,"changePwd.html",{'err_msg':'不能使用初始密码。'})
		if check_password(old_password,request.user.password):
			user=User.objects.get(username=request.user)
			user.set_password(new_password)
			user.save()
			return render(request,"changePwd.html",{'alert_msg':'修改成功'})
		else:
			return render(request,"changePwd.html",{'err_msg':'旧密码错误'})

@login_required
def resetpwd(request):
	if request.user.username not in ['admin','zp']:
		return render(request,"index.html",{'alert_msg':'权限不足。','jumpto':'/index'})

	if request.method=='GET':
		return render(request,'resetPwd.html')
	else:
		username=request.POST['username']
		password=request.POST['password']
		user=User.objects.get(username=username)
		user.set_password(password)
		user.save()
		return render(request,'resetPwd.html',{'alert_msg':'重置成功'})

@login_required
def index(request):
	collectIP(request)
	delete_session(request)
	if check_password('123456',request.user.password):
		return render(request,"index.html",{'alert_msg':'检测到你的密码是初始密码，请修改。','jumpto':'/changepwd'})
	else:
		return render(request,"index.html")

@login_required
def index_old(request):
	collectIP(request)
	delete_session(request)
	if check_password('123456',request.user.password):
		return render(request,"index-old.html",{'alert_msg':'检测到你的密码是初始密码，请修改。','jumpto':'/changepwd'})
	else:
		return render(request,"index-old.html")
#####################################################################################################
def getIP(request):
	# collectIP(request)
	if request.META.get("HTTP_X_FORWARDED_FOR"):
		ip=request.META.get("HTTP_X_FORWARDED_FOR")
	else:
		ip=request.META.get("REMOTE_ADDR")
	return ip

def collectIP(request):
	if choice([0,1]):
		try:
			infoJSON('919179','test')
			infoJSON('800676','uat')
			getCheckID(search2='14548224386',env='test',getAcclist=1)
			getCheckID(search2='14548952258',env='uat',getAcclist=1)
		except Exception as er:
			logging.info(traceback.format_exc())
	try:
		username=request.user.username
	except:
		username=''
	msg=f'--------------- 请求 {request.path} 来自: {username} {getIP(request)} ---------------'
	logging.info(msg)
	with open('access.log','a',encoding='utf-8') as file:
		file.write(f'[{time.strftime("%Y-%m-%d %X")}]: {msg}\n')

@login_required
def hello(request):
	collectIP(request)
	# userPwd=request.user.password
	# logging.info(check_password('Zp19940130xyz',userPwd))
	# return HttpResponse(f"{userPwd}")
	# return HttpResponse(f"{dir(request.user)}")
	return HttpResponse(f"Hello world! 你的IP: {getIP(request)}")

def echo(request):
	collectIP(request)
	if request.method=='GET':
		msg=request.GET.get('msg')
		return HttpResponse(msg)

@login_required
def ttl_resetPwd(request):
	collectIP(request)
	resetType=request.GET.get('resetType')
	env=request.GET.get('env')
	accounts=request.GET.get('account')
	pword=request.GET.get('pword')
	result={}
	for account in accounts.split():
		if resetType=='APP':
			result[f'{account}_result']=resetpwd_APP(account,pword,env)
		elif resetType=='BOSS':
			result[f'{account}_result']=resetpwd_BOSS(account,pword,env)
		elif resetType=='CGF':
			result[f'{account}_result']=resetpwd_CGF(account,pword,env)
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def abc_resetPwd(request):
	collectIP(request)
	env=request.GET.get('env')
	accounts=request.GET.get('account')
	pword=request.GET.get('pword')
	result={'failed':[]}
	for account in accounts.split():
		try:
			result[f'{account}_result']=resetpwd_abc(account,pword,env)
		except:
			logging.info(traceback.format_exc())
			result[f'{account}_result']='失败'
			result['failed'].append(account)
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def ttl_inMoney(request):
	collectIP(request)
	env=request.GET.get('env')
	accounts=request.GET.get('account')
	check=request.GET.get('check')
	currencys=request.GET.get('currency')
	money=float(request.GET.get('money'))
	result={}
	for account in accounts.split():
		for currency in currencys.split():
			if money>0:
				result_money=inmoney_CMS(account,currency,money,env=env,ttl=1,check=check)
			else:
				approveId=withdrawalSave(account,currency,abs(money),env)
				# result_inMoney=inmoney_CMS(account,currency,money,env=env,ttl=1,check=check)
				result_money=money_check(approveId['data']['id'],pathType='withdrawal',bigMoney=1)#审核提取

			result[f'result_{account}_{currency}']=result_money
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def get_ttl_checkId(request):
	collectIP(request)
	env=request.GET.get('env')
	account=request.GET.get('account')
	result=getCasherDeposite(account,env)
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def ttl_checkInMoney(request):
	collectIP(request)
	env=request.GET.get('env')
	account=request.GET.get('account')
	approveId=request.GET.get('approveId')
	if not approveId:
		approveId=getCasherDeposite(account,env)
		try:
			approveId=[i[0] for i in approveId['result']]
		except KeyError:
			approveId=''
	if approveId:
		result=money_check(approveId,env)
	else:
		result={"message":f"{env}环境CMS_TTL系统内未查询到{account}资金申请记录"}
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def getTestAccount(request):
	collectIP(request)
	env=request.GET.get('env')
	num=request.GET.get('num')
	acc_type='ttl'
	sql=f"SELECT acc,acc_pwd,phone,card_id FROM interfaceTest_data.regInfo WHERE env='{env}' AND acc_type='{acc_type}' ORDER BY RAND() LIMIT {num}"
	logging.info(sql)
	query_result=excuteSQL(sql,dbType='mysql',env='test')
	logging.info(query_result)
	result={"success":True,"result":query_result,"format":"account"}
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def queryClientInfo(request):
	collectIP(request)
	env=request.GET.get('env')
	queryType=request.GET.get('queryType')
	account=request.GET.get('account')
	pword=request.GET.get('pword')
	if queryType=='clientID':
		result=getTTLclientId(account,pword,env)
		try:
			result={"env":env,"account":account,"clientId":result['clientId']}
		except KeyError:
			pass
	elif queryType=='infoJson':
		result=infoJSON(account,env)
	elif queryType=='cardID':
		result=getCardsID(account,env)
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')


@login_required
def unlockAccount(request):
	collectIP(request)
	env=request.GET.get('env')
	account=request.GET.get('account')
	result=unlockAcc(account,env)
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def grayControl(request):
	collectIP(request)
	env=request.GET.get('env')
	method=request.GET.get('method')
	kword=request.GET.get('kword')
	result=grayControlAPI(method,env,kword)
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def parsePB2(request):
	collectIP(request)
	data=request.POST.get('data')
	try:
		result=parseData(bytes.fromhex(data))
	except:
		result={"msg":f"无效数据: {data}"}
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def ttl_addHold(request):
	collectIP(request)
	env=request.GET.get('env')
	accounts=request.GET.get('account')
	markettype=request.GET.get('markettype')
	stockcodes=request.GET.get('stockcode')
	stocknum=request.GET.get('stocknum')
	
	result={}
	for account in accounts.split():
		# if account.startswith('E'):
		# 	result[account][f'{stockcode}_result']='暂不支持ESOP账户'
		# 	continue
		if account not in result:result[account]={}
		for stockcode in stockcodes.split():
			result[account][f'{stockcode}_result']=addHOld_ttl(account,stockcode,stocknum,markettype,env)
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def addHold(request):
	collectIP(request)
	env=request.GET.get('env')
	accounts=request.GET.get('account')
	markettype=request.GET.get('markettype')
	stockcodes=request.GET.get('stockcode')
	stocknum=request.GET.get('stocknum')
	delall=request.GET.get('delall')
	result={}
	for account in accounts.split():
		if account not in result:result[account]={}
		acctType='MRGN' if 'M' in account.upper() else 'CUST'
		sql_add=[]
		for stockcode in stockcodes.split():
			sql_add.extend([
				f"INSERT INTO OctOSTP_Front.dbo.InstrumentDepotBalance (BalanceType,Instrument,Market,AcctType,Depot,Position,Location,SyncRef,ClntCode) VALUES ('L','{stockcode}','{markettype}','{acctType}','03','{stocknum}','ST','','{account}')",
				f"INSERT INTO OctOSTP_Front.dbo.InstrumentDepotBalance (BalanceType,Instrument,Market,AcctType,Depot,Position,Location,SyncRef,ClntCode) VALUES ('O','{stockcode}','{markettype}','{acctType}','03','{stocknum}','ST','','{account}')",
			])
		sql_del=f"DELETE FROM OctOSTP_Front.dbo.InstrumentDepotBalance WHERE ClntCode='{account}' AND Market='{markettype}'"
		result_del=excuteSQL(sql_del,dbType='sqlserver',env=env)
		if delall=='Y':
			result[account]['result_del']=result_del
		else:
			result_add=excuteSQL(sql_add,dbType='sqlserver',env=env)
			result[account]['result_add']=result_add
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def addMoney(request):
	collectIP(request)
	env=request.GET.get('env')
	accounts=request.GET.get('account')
	currency=request.GET.get('currency')
	money=request.GET.get('money')
	delall=request.GET.get('delall')
	
	result={}
	for account in accounts.split():
		if account not in result:result[account]={}
		acctType='MRGN' if 'M' in account.upper() else 'CUST'
		for curr in currency.split():
			sql_add=[
				f"INSERT INTO OctOSTP_Front.dbo.CashBankBalance (ClntCode,AcctType,Market,CCY,BalanceType,Bank,Position,OpeningBalance,MTDInterest,SyncRef,CreditInterest,DebitInterest,OverdueInterest,PenaltyInterest) VALUES ('{account}','{acctType}','ALL','{curr}','L','HSBC',{money},.00000000,.00000000,'',.00000000,.00000000,.00000000,.00000000)",
				f"INSERT INTO OctOSTP_Front.dbo.CashBankBalance (ClntCode,AcctType,Market,CCY,BalanceType,Bank,Position,OpeningBalance,MTDInterest,SyncRef,CreditInterest,DebitInterest,OverdueInterest,PenaltyInterest) VALUES ('{account}','{acctType}','ALL','{curr}','O','HSBC',{money},.00000000,.00000000,'',.00000000,.00000000,.00000000,.00000000)",
				f"INSERT INTO OctOSTP_Front.dbo.CashBankBalance (ClntCode,AcctType,Market,CCY,BalanceType,Bank,Position,OpeningBalance,MTDInterest,SyncRef,CreditInterest,DebitInterest,OverdueInterest,PenaltyInterest) VALUES ('{account}','{acctType}','ALL','{curr}','P','HSBC',{money},.00000000,.00000000,'',.00000000,.00000000,.00000000,.00000000)",
			]
			sql_del=f"DELETE FROM OctOSTP_Front.dbo.CashBankBalance WHERE ClntCode='{account}' AND CCY='{curr}'"
			result_del=excuteSQL(sql_del,dbType='sqlserver',env=env)
			if delall=='Y':
				result[account][f'result_del_{curr}']=result_del
			else:
				result_add=excuteSQL(sql_add,dbType='sqlserver',env=env)
				result[account][f'result_add_{curr}']=result_add
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def bankSecuritiesAddMoney(request):
	collectIP(request)
	env=request.GET.get('env')
	account=request.GET.get('account')
	bankName=request.GET.get('bankName')
	bankNum=request.GET.get('bankNum')
	currency=request.GET.get('currency')
	money=request.GET.get('money')
	tradeDate=request.GET.get('tradeDate')
	auto_bankReg=int(request.GET.get('auto_bankReg'))
	auto_addBank=int(request.GET.get('auto_addBank'))

	result={}
	for curr in currency.split():
		result[f"add_{curr}"]=bankSecurities_transfer(account,bankName,bankNum,curr,money,tradeDate,env,auto_bankReg,auto_addBank)
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def rpqTest(request):
	collectIP(request)
	env=request.GET.get('env')
	accounts=request.GET.get('accounts')
	result=[]
	for acc in accounts.split():
		result.append(rpqSave(acc,env))
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

# @login_required
# def getKafkalog(request):
# 	collectIP(request)
# 	env=request.GET.get('env')
# 	num=request.GET.get('num')
# 	redis_basis_conn={
# 		'test':[
# 			{'host':'192.168.99.181','port':7000},{'host':'192.168.99.181','port':7001},{'host':'192.168.99.181','port':7002},
# 			{'host':'192.168.99.181','port':7003},{'host':'192.168.99.181','port':7004},{'host':'192.168.99.181','port':7005},
# 		],
# 		'uat':[
# 			{'host':'192.168.99.198','port':7000},{'host':'192.168.99.198','port':7001},{'host':'192.168.99.198','port':7002},
# 			{'host':'192.168.99.198','port':7003},{'host':'192.168.99.198','port':7004},{'host':'192.168.99.198','port':7005},
# 		],
# 	}
# 	redisconn=RedisCluster(startup_nodes=redis_basis_conn[env])
# 	data=redisconn.lrange('QOT_TRACE_LOGIN_EVENT_LIST',0,int(num))
# 	redisconn.close()
# 	data=list(map(lambda s:json.loads(s.decode()),data))
# 	for i in range(len(data)):
# 		data[i]['loginAt']=time.strftime('%Y-%m-%d %X',time.localtime(data[i]['loginAt']/1000))+str(data[i]['loginAt']/1000)[-4:]
# 	result={'format':'kafkalog','result':data}
# 	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def cms_createUesr(request):
	collectIP(request)
	env=request.GET.get('env')
	accType=eval(request.GET.get('accType'))
	tel=request.GET.get('tel')
	email=request.GET.get('email')
	aecode=request.GET.get('aecode')
	cardType=request.GET.get('cardType')
	result=createUesr_CMS(env=env,accType=accType,tel=tel,email=email,aecode=aecode,cardType=cardType)
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')
	

@login_required
def TTLgrayControl(request):
	collectIP(request)
	env=request.GET.get('env')
	method=request.GET.get('method')
	grayType=request.GET.get('grayType')
	status=request.GET.get('status')
	uuid=request.GET.get('uuid')
	remark=request.GET.get('remark')
	user=request.user.username
	result=TTL_grayControl(method,env=env,grayType=grayType,status=status,uuid=uuid,remark=remark,user=user)
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def UIAutoControl(request):
	collectIP(request)
	if request.user.username in ['admin','zp']:
		server=request.GET.get('server')
		if server=='query':
			processName=request.GET.get('processName')
			result=getProcess(processName)
			result["format"]=True
			result["result"]=result["result"].split('\n')
		elif server=='appium':
			method=request.GET.get('method')
			appiumPort=request.GET.get('appiumPort')
			result=server_appium_wda(method,appiumPort)
		elif server=='wda':
			method=request.GET.get('method')
			wdaPort=request.GET.get('wdaPort')
			result=server_appium_wda(method,wdaPort)
		elif server=='startUI':
			shellName=request.GET.get('shellName')
			result=start_UItest(shellName)
		elif server=='killProcessID':
			processID=request.GET.get('processID')
			result=kill_processID(processID)
	else:
		result={'success':0,'msg':'无权限'}
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')


def getStockList(request):
	result={'success':1,'result':getStockByRand()}
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def regByApi(request):
	collectIP(request)
	args=Args()

	args.env=request.GET.get('env')
	args.ttl=1 if request.GET.get('acc_type')=='TTL' else 0
	args.tel=request.GET.get('tel')
	args.email=request.GET.get('email')
	args.margin=int(request.GET.get('margin'))
	args.check=args.active=int(request.GET.get('active'))
	args.setPwd=int(request.GET.get('setPwd'))
	args.setPwdTel=int(request.GET.get('setPwdTel'))
	args.w8=int(request.GET.get('w8'))
	args.market=int(request.GET.get('market'))
	try:
		args.invite_code=int(request.GET.get('invite_code'))# 推荐号
		args.aum_account=str(int(random()*10**16))
	except:
		args.invite_code=''
		args.aum_account=''

	args.regbyapi=True
	args.pi=False
	args.location='zh_CN'
	args.reason=0

	args=reg_main(args)
	if args.reason:
		return HttpResponse(f"开户失败: \n{args.reason}\n\n{args.regInfo}")
	else:
		return HttpResponse(f"开户成功: \n{args.regInfo}")
	# if args.reason:
	# 	result={"success":False,"result":f"开户失败: \n{args.reason}\n\n{args.regInfo}"}
	# else:
	# 	result={"success":True,"result":[f"开户成功: \n{args.regInfo}"],"format":True}
	# 	logging.info(result)
	# return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

def health(request):
	# collectIP(request)
	return HttpResponse('OK')

@login_required
def addIPO(request):
	collectIP(request)
	env=request.GET.get('env')
	stockcode=request.GET.get('stockcode')
	stockname=request.GET.get('stockname')

	fake=faker.Faker('zh-CN')
	if not stockcode:stockcode=f'98{fake.random_int()}'
	if not stockname:
		stockname=fake.company_prefix()
		if len(stockname)==2:
			suffix=['股份','集团','科技','医药','时代','数码','技术']
			stockname=f'{stockname}{choice(suffix)}'
	publishId,cmbi_deadline,sqlList_SZ=insertIPO(stockcode,stockname,env)
	try:
		excuteSQL(sqlList_SZ,dbType='mysql',env=env)
		result={'success':1,'msg':f'{env} 环境创建新股: {stockcode} {stockname} 成功'}
	except:
		result={'success':0,'msg':f'{env} 环境创建新股: {stockcode} {stockname} 失败'}
		logging.info(sqlList_SZ)

	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def accountLogout(request):
	collectIP(request)
	env=request.GET.get('env')
	account=request.GET.get('account')
	sessionid=request.GET.get('sessionid')
	result=logout_acc(account,sessionid,env)
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def portfolio(request):
	collectIP(request)
	env=request.GET.get('env')
	account=request.GET.get('account')
	addPortfolio(account,env)
	return HttpResponse(json.dumps({'success':1,'msg':None},ensure_ascii=False),content_type='application/json')

@login_required
def uploadPDF(request):
	collectIP(request)
	env=request.GET.get('env')
	account=request.GET.get('account')
	invoiceType=request.GET.get('invoiceType')
	invoiceDate=request.GET.get('invoiceDate')
	accType=request.GET.get('accType')
	accInfo=infoJSON(account,env)
	if accInfo['result']=='404':
		response=HttpResponse(json.dumps(accInfo,ensure_ascii=False),content_type='application/json')
		return response

	year,month,day=invoiceDate.split('-')
	try:
		int(account)
		accType2='CUST'
	except ValueError:
		if account.startswith('M'):
			accType2='MRGN'
		else:
			return HttpResponse(json.dumps({'success':0,'msg':f'账户类型不支持: {account}'},ensure_ascii=False),content_type='application/json')

	remotePath=f'/test_invoice' if env.lower()=='test' else f'/invoice'
	if accType=='normal':
		remotePath=f'{remotePath}/{year}'
		if invoiceType=='Monthly':
			remotePath=f'{remotePath}/Monthly_{year}{month}{day}/{year}{month}{day}_{account}_{accType2}.pdf'
		elif invoiceType=='Daily':
			remotePath=f'{remotePath}/{year}{month}/{year}{month}{day}/{year}{month}{day}_{account}_{accType2}.pdf'
	elif accType=='gm':
		remotePath=f'{remotePath}/CMBIGM/{year}'
		if invoiceType=='Monthly':
			remotePath=f'{remotePath}/Monthly_{year}{month}{day}/{year}{month}{day}_{account}_{accType2}.pdf'
		elif invoiceType=='Daily':
			remotePath=f'{remotePath}/{year}{month}/{year}{month}{day}/{year}{month}{day}_{account}_{accType2}.pdf'
	elif accType=='futures':
		remotePath=f'{remotePath}/SplittedStatement_{invoiceType}/{account}.{year}{month}{day}.{invoiceType.lower()}.pdf'#期货日结单
	elif accType=='options':
		remotePath=f'{remotePath}/StkOpt_SplittedStatement_{invoiceType}/{account}.{year}{month}{day}.{invoiceType.lower()}.pdf'

	ftp_store_file("testServices/pdf/common.pdf",remotePath)
	respJson=clientInvoice(invoiceDate,env)
	return HttpResponse(json.dumps({'上传结单PDF结果':'成功','导入结单结果':respJson},ensure_ascii=False),content_type='application/json')

@login_required
def openmarket(request):
	collectIP(request)
	env=request.GET.get('env')
	account=request.GET.get('account')
	conn=None;result={}
	for acc in account.split():
		conn=del_market(acc,env=env,conn=conn)
		result[f'{acc}_result']=openMarket_boss(acc,env=env)
	conn.close()
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

@login_required
def getViewXY(request):
	collectIP(request)
	userID=str(User.objects.get(username=request.user).id)

	width=request.GET.get('width')
	width=float(width) if width else 2524
	if width<=1300:
		username=f'{userID}_half' 
		defaultUser='default_half'
	else:
		username=f'{userID}_full'
		defaultUser='default_full'
	try:
		result=ViewXY.objects.get(username=username)
		logging.info(f'查询用户 {request.user} 配置成功')
	except ViewXY.DoesNotExist:
		logging.info(f'查询用户 {request.user} 配置失败，使用默认配置')
		result=ViewXY.objects.get(username=defaultUser)
		ViewXY.objects.create(username=username,xy=result.xy)
	return HttpResponse(json.dumps({"user":str(request.user),"result":eval(result.xy)},ensure_ascii=False),content_type='application/json')

@login_required
def saveViewXY(request):
	collectIP(request)
	postData=json.loads(request.body)
	xy=postData.get('data')
	width=postData.get('width')
	userID=str(User.objects.get(username=request.user).id)
	# username=str(request.user)
	width=float(width) if width else 2524
	userID=f'{userID}_half' if width<=1300 else f'{userID}_full'
	# logging.info(f'debug: {xy}')
	ViewXY.objects.filter(username=userID).update(xy=xy)
	return HttpResponse(json.dumps({"success":1,"msg":"保存成功"},ensure_ascii=False),content_type='application/json')

@login_required
def unBinding(request):
	collectIP(request)
	env=request.GET.get('env')
	account=request.GET.get('account')
	pword=request.GET.get('pword')	
	result=unBind(account,pword,env)
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')

def getTTLsessionID(request):
	collectIP(request)
	env=request.GET.get('env')
	key=request.GET.get('key')
	operatorDic={'uat':'WS01','test':'CMBI03','dev':'CMBI02'}
	if key=='TC4HFqebwzYBT5jsjXamY6I7GN63d':
		# uat：{host:'192.168.93.2:8089',operatorId:'WS01',password:'E9CEE71AB932FDE863338D08BE4DE9DFE39EA049BDAFB342CE659EC5450B69AE'}
		# test: {host:'172.20.99.2:8089',operatorId:'CMBI03',password:'EF797C8118F02DFB649607DD5D3F8C7623048C9C063D532CC95C5ED7A898A64F'}
		# dev: {host:'172.20.99.2:8089',operatorId:'CMBI02',password:'EF797C8118F02DFB649607DD5D3F8C7623048C9C063D532CC95C5ED7A898A64F'}
		result={'success':True,'sessionID':getkey_redis(f"NEBULA_SESSION_ID_{operatorDic[env]}",env)}		
	else:
		result={'success':False,'msg':'key错误'}
	return HttpResponse(json.dumps(result,ensure_ascii=False),content_type='application/json')
