from browser import document,ajax,bind,confirm,alert
import json,datetime

def out_print(outstring,timestr=1):
	now_txt=f"[{datetime.datetime.now().strftime('%Y-%m-%d %X.%f')[:-3]}]:" if timestr else ''
	textarea_out=document.getElementsByTagName("textarea")[0].value
	document["outText"].value=f"{textarea_out}{now_txt}{outstring}\n"

def complete(request):
	respText=request.responseText
	if "登录 - TestServices" in respText:
		alert('你的账户在其它地方登陆')
		document.location.reload()
	else:
		try:
			data=json.loads(respText)
		except:
			data=respText
		try:
			if data["format"]:
				out_print(' ')
				if data["format"]=='account':
					out_print("  账户号      密码        手机号          card_ID",0)
				elif data["format"]=='ttlCheckIdList':
					if data["result"]:
						out_print(" 待审核ID    业务状态    账户号      金额         币种         存入时间",0)
					else:
						out_print(f'未查询到相关申请记录')
						return
				if data["format"]=='ttl_gary':
					out_print("            UUID                     灰度类型  状态 备注",0)
				for i in data["result"]:
					if isinstance(i,list):
						out_print(i,0)
					elif isinstance(i,str):
						out_print(i.strip(),0)
					# out_print(" ".join(i),0)
		except (KeyError,TypeError):
			out_print(data)

def ajax_req(path,msg,method='GET',postData=None):
	req=ajax.ajax()
	req.open(method,f'http://{document.location.host}{path}',True)
	req.set_header('content-type', 'application/x-www-form-urlencoded')
	req.bind("complete",complete)
	out_print(msg)
	if postData:
		req.send(postData)
	else:
		req.send()

##############################################################################################################
@bind("#button0","click")
def clearOut(event):
	document["outText"].value=""

####################################################
# @bind("#button4","click")
# def ttl_inMoney(event):
# 	env=document["env4"].value
# 	currency=document.querySelector('#currency .fs-label').getAttribute("value")
# 	acc=document["name4"].value
# 	money=document["money"].value
# 	if '请选择' in currency:currency=None
# 	if env and currency and acc and money:
# 		currency=currency.replace(',','')
# 		path=f"/ttl_inMoney?env={env}&currency={currency}&account={acc}&money={money}"
# 		msg=f'{env} 环境 {acc} TTL资金存入 {currency} {money} 开始执行,请耐心等待,不要重复点击...'
# 		ajax_req(path,msg)
# 	else:
# 		out_print(f'无效操作。缺少参数，请检查。')
# 		return

# @bind("#acc_type4","mouseout")
# @bind("#acc_type4","mouseover")
# def change_bg_color4(event):
# 	acc_type4=document["acc_type4"].value
# 	if acc_type4=='ABC':
# 		document["button4"].attrs["class"]="waves bg_color1 m_right_60"
# 		document["button4_1"].style.display="block"
# 		document["lineText4"].attrs["class"]="line_text color1"
# 		document["button4"].innerHTML="点击执行"
# 	elif acc_type4=='TTL':
# 		document["button4"].attrs["class"]="waves bg_color2 m_right_60"
# 		document["button4_1"].style.display="None"
# 		document["lineText4"].attrs["class"]="line_text color2"
# 		document["button4"].innerHTML="存入并审核"

@bind("#button4","click")
def inMoney(event):
	env=document["env4"].value
	currency=document.querySelector('#currency .fs-label').getAttribute("value")
	acc=document["name4"].value
	money=float(document["money"].value)
	in_out='存入' if money>=0 else '提取'
	# acc_type4=document["acc_type4"].value
	if '请选择' in currency:currency=None
	if currency and acc and money:
		currency=currency.replace(',','')
		path=f"/ttl_inMoney?env={env}&currency={currency}&account={acc}&money={money}&check=1"
		msg=f'{env} 环境 {acc} 资金{in_out} {abs(money)} {currency} 并审核 开始执行,请耐心等待,不要重复点击...'
		# else:
		# 	path=f"/addMoney?env={env}&account={acc}&currency={currency}&money={money}"
		# 	msg=f'ABC {env}环境{acc}加资金 {currency} {money} 开始执行...'
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')
		return

# @bind("#button10","click")
# def addMoney(event):
# 	env=document["env10"].value
# 	acc=document["name10"].value
# 	currency=document.querySelector('#currency10 .fs-label').getAttribute("value")
# 	money=document["money10"].value
# 	if '请选择' in currency:currency=None
# 	if acc and money and currency:
# 		currency=currency.replace(',','')
# 		path=f"/addMoney?env={env}&account={acc}&currency={currency}&money={money}"
# 		ajax_req(path,f'ABC {env}环境{acc}加资金 {currency} {money} 开始执行...')
# 	else:
# 		out_print(f'无效操作。缺少参数，请检查。')

@bind("#button4_1","click")
def addMoney_del(event):
	env=document["env4"].value
	acc=document["name4"].value
	currency=document.querySelector('#currency .fs-label').getAttribute("value")
	if '请选择' in currency:currency=None
	if acc and currency:
		result=confirm(f'确实要删除 {env} 环境账户 {acc} 下的所有 {currency} 资金吗？')
		if result:
			currency=currency.replace(',','')
			path=f"/addMoney?env={env}&account={acc}&currency={currency}&delall=Y"
			ajax_req(path,f'开始删除...')
	else:
		out_print(f'无效操作。缺少参数，请检查。')

####################################################
# @bind("#button1_1","click")
# def get_ttl_checkId(event):
# 	env=document["env1"].value
# 	acc=document["name1"].value
# 	if env and acc:
# 		path=f"/get_ttl_checkId?env={env}&account={acc}"
# 		msg=f'查询 {env} 环境 {acc} TTL资金存入待审核列表 开始执行...'
# 		ajax_req(path,msg)
# 	else:
# 		out_print(f'无效操作。缺少参数，请检查。')
# 		return

# @bind("#button1","click")
# def ttl_checkInMoney(event):
# 	env=document["env1"].value
# 	acc=document["name1"].value
# 	approveId=document["approveId"].value
# 	if env and acc:
# 		path=f"/ttl_checkInMoney?env={env}&account={acc}&approveId={approveId}"
# 		_msg=f"业务ID {approveId} " if approveId else ' '
# 		msg=f'{env} 环境 {acc} TTL资金存入审核{_msg} 开始执行...'
# 		ajax_req(path,msg)
# 	else:
# 		out_print(f'无效操作。缺少参数，请检查。')
# 		return

####################################################
# @bind("#acc_type9","mouseout")
# @bind("#acc_type9","mouseover")
# def change_bg_color9(event):
# 	acc_type9=document["acc_type9"].value
# 	if acc_type9=='ABC':
# 		document["button9"].attrs["class"]="waves bg_color1 m_right_60"
# 		document["button9_1"].attrs["class"]="waves bg_color1"
# 		document["button9_1"].style.display="block"
# 		document["lineText9"].attrs["class"]="line_text color1"
# 	elif acc_type9=='TTL':
# 		document["button9"].attrs["class"]="waves bg_color2 m_right_60"
# 		document["button9_1"].attrs["class"]="waves bg_color2"
# 		document["button9_1"].style.display="None"
# 		document["lineText9"].attrs["class"]="line_text color2"

@bind("#button9","click")
def addHold(event):
	env=document["env9"].value
	acc=document["name9"].value
	markettype=document["markettype"].value
	stockcode=document["stockcode"].value
	stocknum=document["stocknum"].value
	# acc_type9=document["acc_type9"].value
	if acc and stockcode and stocknum:
		msg=f'{env}环境{acc}加持仓 {stockcode} 数量 {stocknum} 开始执行...'
		# if acc_type9=='TTL':
		path=f"/ttl_addHold?env={env}&account={acc}&markettype={markettype}&stockcode={stockcode}&stocknum={stocknum}"
		# else:
		# 	path=f"/addHold?env={env}&account={acc}&markettype={markettype}&stockcode={stockcode}&stocknum={stocknum}"
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')

@bind("#button9_1","click")
def addHold_del(event):
	env=document["env9"].value
	acc=document["name9"].value
	markettype=document["markettype"].value
	acc_type9=document["acc_type9"].value
	if acc:
		result=confirm(f'确实要删除 {env} 环境账户 {acc} 下的所有 {markettype} 类型的持仓吗？')
		if result:
			path=f"/addHold?env={env}&account={acc}&markettype={markettype}&delall=Y"
			ajax_req(path,f'开始删除...')
	else:
		out_print(f'无效操作。缺少参数，请检查。')

####################################################
@bind("#button3","click")
def resetPwd(event):
	env=document["env3"].value
	acc=document["name3"].value
	pwd=document["pword3"].value
	resetType=document["resetType"].value
	if acc and pwd:
		path=f"/ttl_resetPwd?resetType={resetType}&env={env}&account={acc}&pword={pwd}"
		msg=f'{env} 环境重置 {acc} 密码为 {pwd} 开始执行...'
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')
		return

@bind("#resetType","mouseout")
@bind("#resetType","mouseover")
def change_bg_color3(event):
	resetType=document["resetType"].value
	if resetType=='BOSS':
		document["button3"].attrs["class"]="waves bg_color1"
		document["lineText3"].attrs["class"]="line_text color1"
	elif resetType=='APP':
		document["button3"].attrs["class"]="waves bg_color2"
		document["lineText3"].attrs["class"]="line_text color2"
	elif resetType=='CGF':
		document["button3"].attrs["class"]="waves bg_color3"
		document["lineText3"].attrs["class"]="line_text color3"

####################################################
@bind("#button5","click")
def getTestAccount(event):
	# acc_type=document["acc_type"].value
	env=document["env5"].value
	num=document["input5"].value
	path=f"/getTestAccount?env={env}&acc_type=TTL&num={num}"
	msg=f'查询{env}环境账户 随机{num}个 开始执行...'
	ajax_req(path,msg)

# @bind("#acc_type","mouseout")
# @bind("#acc_type","mouseover")
# def change_bg_color(event):
# 	acc_type=document["acc_type"].value
# 	if acc_type=='ABC':
# 		document["button5"].attrs["class"]="waves bg_color1"
# 		document["lineText5"].attrs["class"]="line_text color1"
# 	elif acc_type=='TTL':
# 		document["button5"].attrs["class"]="waves bg_color2"
# 		document["lineText5"].attrs["class"]="line_text color2"

@bind("#button6","click")
def queryTTLclientId(event):
	env=document["env6"].value
	queryType=document["queryType"].value
	queryTypeName=document.getElementById("queryType").options[document.getElementById("queryType").selectedIndex].text
	acc=document["name6"].value
	pwd=document["pword6"].value
	if acc and pwd:
		path=f"/queryClientInfo?env={env}&account={acc}&pword={pwd}&queryType={queryType}"
		msg=f'查询{env}环境 {acc} 的 {queryTypeName}'
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')

####################################################
@bind("#button7","click")
def unlockAccount(event):
	env=document["env7"].value
	acc=document["name7"].value
	if env and acc:
		path=f"/unlockAccount?env={env}&account={acc}"
		msg=f'解锁 {env} 环境账户 {acc}'
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')

# @bind("#acc_type7","mouseout")
# @bind("#acc_type7","mouseover")
# def change_bg_color7(event):
# 	acc_type7=document["acc_type7"].value
# 	if acc_type7=='ABC':
# 		document["button7"].attrs["class"]="waves bg_color1"
# 		document["lineText7"].attrs["class"]="line_text color1"
# 	elif acc_type7=='TTL':
# 		document["button7"].attrs["class"]="waves bg_color2"
# 		document["lineText7"].attrs["class"]="line_text color2"
####################################################
@bind("#button2_1","click")
def get_grayControl(event):
	env=document["env2"].value
	path=f"/grayControl?method=get&env={env}"
	msg=f'查询{env}环境灰度设置'
	ajax_req(path,msg)

@bind("#button2_2","click")
def delAll_grayControl(event):
	result=confirm('确 定 ？')
	if result:
		env=document["env2"].value
		path=f"/grayControl?method=delAll&env={env}"
		msg=f'清空{env}环境所有白名单'
		ajax_req(path,msg)

@bind("#button2_3","click")
def edit_grayControl(event):
	env=document["env2"].value
	kword=document["end"].value
	if kword:
		path=f"/grayControl?method=edit&env={env}&kword={kword}"
		msg=f'修改{env}环境灰度尾号放量为 0-{kword}'
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')

@bind("#button2_4","click")
def add_grayControl(event):
	env=document["env2"].value
	kword=document["id_tel"].value
	if kword:
		path=f"/grayControl?method=add&env={env}&kword={kword}"
		msg=f'添加{env}环境灰度白名单 {kword}'
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')

@bind("#button2_5","click")
def del_grayControl(event):
	env=document["env2"].value
	kword=document["id_tel2"].value
	if kword:
		path=f"/grayControl?method=del&env={env}&kword={kword}"
		msg=f'删除{env}环境灰度白名单 {kword}'
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')

@bind("#button2_6","click")
def swich_IP(event):
	env=document["env2"].value
	ip=document["mockIP"].value
	path=f"/grayControl?method=mockIP&env={env}&kword={ip}"
	msg=f'切换{env}环境mockIP为{ip}'
	ajax_req(path,msg)

####################################################
# # CMS系统内开户
# @bind("#acc_type11","mouseout")
# @bind("#acc_type11","mouseover")
# def change_bg_color11(event):
# 	acc_type11=document["acc_type11"].value
# 	if acc_type11=='ABC':
# 		document["button11"].attrs["class"]="waves bg_color1"
# 		document["lineText11"].attrs["class"]="line_text color1"
# 	elif acc_type11=='TTL':
# 		document["button11"].attrs["class"]="waves bg_color2"
# 		document["lineText11"].attrs["class"]="line_text color2"

@bind("#button11","click")
def cms_createUesr(event):
	env=document["env11"].value
	cardType=document["cardType"].value
	tel=document["tel11"].value
	# email=document["email"].value
	aecode=document["aecode"].value
	select=document["acc_type11"]
	accTypeText=select.options[select.selectedIndex].text
	accType=select.value

	path=f"/cms_createUesr?env={env}&accType={accType}&tel={tel}&aecode={aecode}&cardType={cardType}"
	ajax_req(path,f'{env}环境CMS内开 {accTypeText} 开始执行...')

####################################################
# # TTL设备灰度控制
# @bind("#button12_1","click")
# def TTLgrayControl(event):
# 	env=document["env12"].value
# 	grayType=document["grayType"].value
# 	status=document["status"].value
# 	uuid=document["uuid"].value
# 	remark=document["remark"].value
# 	if uuid:
# 		path=f"/TTLgrayControl?env={env}&grayType={grayType}&status={status}&uuid={uuid}&remark={remark}&method=add"
# 		ajax_req(path,f'{env}环境TTL设备灰度控制，开始执行...')
# 	else:
# 		out_print(f'无效操作。缺少参数，请检查。')

# @bind("#button12_2","click")
# def TTLgrayControl(event):
# 	env=document["env12"].value
# 	path=f"/TTLgrayControl?env={env}&method=query"
# 	ajax_req(path,f'查询{env}环境TTL设备灰度，开始执行...')

####################################################
# UI自动化控制
@bind("#button13_1","click")
def UIAutoControl(event):
	processName=document["processName"].value
	if processName:
		path=f"/UIAutoControl?server=query&processName={processName}"
		ajax_req(path,f'查询进程 {processName} 开始执行...')
	else:
		out_print(f'无效操作。缺少参数，请检查。')

@bind("#button13_2_stop","click")
def stop_appium(event):
	appiumPort=document.querySelector('#appium .fs-label').getAttribute("value")
	if appiumPort:
		appiumPort=appiumPort.replace(',','')
		path=f"/UIAutoControl?server=appium&method=stop&appiumPort={appiumPort}"
		ajax_req(path,f'停止appium {appiumPort} 开始执行...')
	else:
		out_print(f'无效操作。缺少参数，请检查。')

@bind("#button13_2_start","click")
def start_appium(event):
	appiumPort=document.querySelector('#appium .fs-label').getAttribute("value")
	if appiumPort:
		appiumPort=appiumPort.replace(',','')
		path=f"/UIAutoControl?server=appium&method=start&appiumPort={appiumPort}"
		ajax_req(path,f'启动appium {appiumPort} 开始执行...')
	else:
		out_print(f'无效操作。缺少参数，请检查。')

@bind("#button13_3_stop","click")
def stop_wda(event):
	iosNames=document.querySelector('#wda .fs-label').getAttribute("value")
	wdaPort=''
	if iosNames:
		for ios in iosNames.split(','):
			if 'iPhone 11 Pro Max' in ios:
				wdaPort+='8100 '
			elif 'iPhone 11 Pro' in ios:
				wdaPort+='8101 '
			elif 'iPhone 11' in ios:
				wdaPort+='8102 '
		path=f"/UIAutoControl?server=wda&method=stop&wdaPort={wdaPort}"
		ajax_req(path,f'停止wda {wdaPort} 开始执行...')
	else:
		out_print(f'无效操作。缺少参数，请检查。')

@bind("#button13_3_start","click")
def start_wda(event):
	iosNames=document.querySelector('#wda .fs-label').getAttribute("value")
	wdaPort=''
	if iosNames:
		for ios in iosNames.split(','):
			if 'iPhone 11 Pro Max' in ios:
				wdaPort+='8100 '
			elif 'iPhone 11 Pro' in ios:
				wdaPort+='8101 '
			elif 'iPhone 11' in ios:
				wdaPort+='8102 '
		path=f"/UIAutoControl?server=wda&method=start&wdaPort={wdaPort}"
		ajax_req(path,f'启动wda {wdaPort} 开始执行...')
	else:
		out_print(f'无效操作。缺少参数，请检查。')

@bind("#button13_4","click")
def start_UItest(event):
	shellName=document.querySelector('#ui_auto .fs-label').getAttribute("value")
	if shellName:
		shellName=shellName.replace(',','')
		path=f"/UIAutoControl?server=startUI&shellName={shellName}"
		ajax_req(path,f'启动UI自动化测试 {shellName} 开始执行...')
	else:
		out_print(f'无效操作。缺少参数，请检查。')

@bind("#button13_5","click")
def stop_processID(event):
	processID=document["processID"].value
	if processID:
		path=f"/UIAutoControl?server=killProcessID&processID={processID}"
		ajax_req(path,f'终止进程 {processID} 开始执行...')
	else:
		out_print(f'无效操作。缺少参数，请检查。')

####################################################
# APP 开户
# @bind("#acc_type14","mouseout")
# @bind("#acc_type14","mouseover")
# def change_bg_color14(event):
# 	acc_type14=document["acc_type14"].value
# 	if acc_type14=='ABC':
# 		document["button14"].attrs["class"]="waves bg_color1"
# 		document["lineText14"].attrs["class"]="line_text color1"
# 	elif acc_type14=='TTL':
# 		document["button14"].attrs["class"]="waves bg_color2"
# 		document["lineText14"].attrs["class"]="line_text color2"

@bind("#active","click")
def active_gary(event):
	active=document["active"]
	setPwd=document["setPwd"]
	if active.checked:
		document["setPwd"].disabled=False
		document["setPwd_desc"].attrs["class"]=""
		if setPwd.checked:
			document["setPwdTel"].disabled=False
			document["setPwdTel_desc"].attrs["class"]=""
			document["w8"].disabled=False
			document["w8_desc"].attrs["class"]=""
			document["market"].disabled=False
			document["market_desc"].attrs["class"]=""
		else:
			document["setPwdTel"].disabled=True
			document["setPwdTel_desc"].attrs["class"]="gray"
			document["w8"].disabled=True
			document["w8_desc"].attrs["class"]="gray"
			document["market"].disabled=True
			document["market_desc"].attrs["class"]="gray"
	else:
		document["setPwd"].disabled=True
		document["setPwd_desc"].attrs["class"]="gray"

		document["setPwdTel"].disabled=True
		document["setPwdTel_desc"].attrs["class"]="gray"
		document["w8"].disabled=True
		document["w8_desc"].attrs["class"]="gray"
		document["market"].disabled=True
		document["market_desc"].attrs["class"]="gray"

@bind("#setPwd","click")
def setPwd_gary(event):
	setPwd=document["setPwd"]
	if setPwd.checked:
		document["setPwdTel"].disabled=False
		document["w8"].disabled=False
		document["market"].disabled=False
		document["setPwdTel_desc"].attrs["class"]=""
		document["w8_desc"].attrs["class"]=""
		document["market_desc"].attrs["class"]=""
	else:
		document["setPwdTel"].disabled=True
		document["w8"].disabled=True
		document["market"].disabled=True
		document["setPwdTel_desc"].attrs["class"]="gray"
		document["w8_desc"].attrs["class"]="gray"
		document["market_desc"].attrs["class"]="gray"

@bind("#button14","click")
def regByApi(event):
	env=document["env14"].value
	# acc_type=document["acc_type14"].value
	tel=document["tel14"].value
	email=document["emai14"].value
	margin=int(document["margin"].checked)
	active=int(document["active"].checked)
	setPwd=int((document["setPwd"].checked) and (not document["setPwd"].disabled))
	setPwdTel=int((document["setPwdTel"].checked) and (not document["setPwdTel"].disabled))
	w8=int((document["w8"].checked) and (not document["w8"].disabled))
	market=int((document["market"].checked) and (not document["market"].disabled))
	path=f"/regByApi?env={env}&acc_type=TTL&tel={tel}&email={email}&margin={margin}&active={active}&setPwd={setPwd}&setPwdTel={setPwdTel}&w8={w8}&market={market}"
	ajax_req(path,f' {env}环境 app开户 开始执行...')

####################################################
@bind("#button15","click")
def bankSecuritiesInMoney(event):
	env=document["env15"].value
	bankName=document["bankName"].value
	currency=document.querySelector('#currency15 .fs-label').getAttribute("value")
	acc=document["name15"].value
	bankNum=document["bankNum"].value
	money=document["money15"].value
	tradeDate=document["tradeDate"].value.replace('-','').replace('/','').replace(' ','')
	auto_bankReg=int(document["bankReg"].checked)
	auto_addBank=int(document["addBank"].checked)

	if '请选择' in currency:currency=None
	if env and currency and acc and money and bankNum and tradeDate:
		currency=currency.replace(',','')

		path=f"/bankSecuritiesAddMoney?env={env}&account={acc}&bankName={bankName}&bankNum={bankNum}&currency={currency}&money={money}&tradeDate={tradeDate}&auto_bankReg={auto_bankReg}&auto_addBank={auto_addBank}"
		msg=f'{env} 环境 {acc} {bankName}银证入金 {currency} {money} 开始执行,请耐心等待,不要重复点击...'
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')
		return

@bind("#bankReg","click")
def addBank_gary(event):
	bankReg=document["bankReg"]
	if bankReg.checked:
		document["addBank"].disabled=False
		document["addBank_desc"].attrs["class"]=""
	else:
		document["addBank"].disabled=True
		document["addBank_desc"].attrs["class"]="gray"

####################################################
@bind("#button16","click")
def addIPO(event):
	env=document["env16"].value
	newStockname=document["newStockname"].value
	newStockcode=document["newStockcode"].value

	path=f"/addIPO?env={env}&stockname={newStockname}&stockcode={newStockcode}"
	msg=f'{env} 环境创建新股开始执行'
	ajax_req(path,msg)

####################################################
@bind("#button17","click")
def accountLogout(event):
	env=document["env17"].value
	account=document["name17"].value
	sessionid=document["sessionid"].value
	if env and account and sessionid:
		path=f"/accountLogout?env={env}&account={account}&sessionid={sessionid}"
		msg=f'{env} 环境{account}session失效 开始执行'
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')
		return

####################################################
@bind("#button8","click")
def parsePBdata(event):
	data=document["data_pb2"].value
	if data:
		path=f"/parsePB2"
		ajax_req(path,'解析protocol数据...','POST',postData=f"data={data}")
	else:
		out_print(f'无效操作。缺少参数，请检查。')

###########################
@bind("#button8_1","click")
def getKafkalog(event):
	env8=document["env8"].value
	num8=document["num8"].value
	if num8:
		path=f"/getKafkalog?env={env8}&num={num8}"
		ajax_req(path,f'查询{env8}环境Kafka日志最近 {num8} 条...')
	else:
		out_print(f'无效操作。缺少参数，请检查。')

####################################################
@bind("#button8_2","click")
def portfolio(event):
	env=document["env8"].value
	account=document["name8"].value
	if account:
		path=f"/portfolio?env={env}&account={account}"
		msg=f'{env} 环境{account} 添加静态资产 开始执行'
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')
		return

####################################################
@bind("#button8_3","click")
def openmarket(event):
	env=document["env8"].value
	account=document["name8_3"].value
	if account:
		path=f"/openmarket?env={env}&account={account}"
		msg=f'{env} 环境{account} 开通市场 开始执行'
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')
		return

####################################################
@bind("#button18","click")
def uploadPDF(event):
	env=document["env18"].value
	acc=document["name18"].value
	invoiceType=document["invoiceType"].value
	invoiceDate=document["invoiceDate"].value.replace('/','-')

	if acc and invoiceDate:
		path=f"/uploadPDF?env={env}&account={acc}&invoiceType={invoiceType}&invoiceDate={invoiceDate}"
		msg=f'{env} 环境 {acc} 推送结单文件 开始执行...'
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')
		return

####################################################
@bind("#button12","click")
def unBinding(event):
	env=document["env12"].value
	acc=document["name12"].value
	pwd=document["pword12"].value

	if acc:
		path=f"/unBinding?env={env}&account={acc}&pword={pwd}"
		msg=f'{env} 环境 {acc} 解绑证券账户 开始执行...'
		ajax_req(path,msg)
	else:
		out_print(f'无效操作。缺少参数，请检查。')
		return
