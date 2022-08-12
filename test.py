import HTMLReport
from testServices.plugins.boss import *
# from testServices.plugins.database import *
# from testServices.plugins.myAPI import *
# from testServices.plugins.boss import *
# import random
# from plugins.myAPI import isTTLAcc
# from plugins.common import ftp_store_file

# del_market('917669',env='test',conn=None)
# openMarket_boss('917669','test')
# status=getApproveStatus('17682','uat','withdrawal')
# print(status)
# # acc_pool=['']
# acc_pool=[
# 	# '705052','705053','705055','705056',
# 	'999001',
# 	'999002',
# 	'999003',
# 	'999004',
# 	'999005',
# 	'999006',
# ]
# print(createUesr_CMS(env='test',accType=2))
# print(createAcc('100074046','430302195011241021','988','test'))

# print(infoJSON('292233','uat'))
rpqSave('806079')
# for acc in acc_pool:
# 	respJson=createESOP(acc,env='uat')
# 	if respJson['result']=='1':
# 		print(f'{acc} 成功 {respJson["data"]["accountid"]}')
# 	else:
# 		print(f'{acc} 失败: {respJson}')


# clientInvoice('2021-12-01','test')
# createUesr_CMS(env='uat',ttl=1,tel=None,email=None,aecode=None)
# for acc in ['706158','M706158','706159','M706159','706160','M706160','292231','M292231','292232','M292232','292233','M292233',]:
# 	print(addBankcard(acc,int(random.random()*10**15),env='uat'))
# print(getBankAccount('M917335','test'))
# print(getCardsID('803203',env='test'))
# print(infoJSON('13243136291',env='uat'))

# env='test'
# account='918138'
# cif_no='100019462'
# card_id=getCardsID(cif_no,env)
# print(card_id)

# respJson=cmsSearch_quick('917776','test')
# print(respJson)
# checkid=respJson['data']['list'][0]['url'].split('=')[-1]
# print('checkid:',checkid)
# cif_no=cmsAccount_check(checkid,backInfo='cif_no',env=env)
# print(cif_no)

# loginBOSS(env)
# print(cmsSearch_quick(account,env))

# acc_pool=['918272','918275',]
# i=0
# for acc in acc_pool:
# 	i+=1
# 	print(i,acc,isTTLAcc(acc,'test'))

# filtrateSelectList()
# print(resetpwd_app('292232'))
# print(bankSecurities_transfer('M919190','港分银行','99336436641226','HKD','15000',env='uat'))
# print(bankSecurities_transfer('M919190','民生银行','60650078002','HKD','15000',env='uat'))
# print(bankSecurities_reg('917632','港分银行','6989843546464','20210908','test'))
# print(checkLoginName('M292233',env='uat'))
# print(login_acc('13651920349','aaaa1111',env='uat',ttl=1))

# ftp_store_file("pdf/common.pdf", "/test_invoice/2021/202111/20211130/test.pdf")


###################################################################################################
# # 1，重置密码为aaaa1111
# # 2，增加自选股港股美股A股，各15只
# # 3，增加基金自选，10只
# # 4，加港美A持仓，各3个

# acc_pool=['292232'
# 	'919178','919188','917636','917517','917592','917611','917650','917706','917526','919161','917593','917836','917889','917672',
# 	'917556','917877','917855','917770','917801','917566','918772','917696','917652','917710','919180','917606','917701','917788',
# 	'919162','918997','917595','917599','917683','917563','917569','917698','917870','917682','919208','917578','917688','917765',
# 	'919199','919192','919156','917525','919175','917689','917719','917535','917763','918796',
# 	'917635','919212','917735','917737',
# 	'917831','917799','917766','917553','917702','917802','912086','917583','917533','917570','917685','918793','917717','917657',
# 	'917807','917603','917729','917730','917756','918798','917536','919187','917832','919198','917609','917656','917522','917818',
# 	'917622','917530','290859','917558',
# ]
# stockList=[ 
# 	'E00700','E03690','E02273','E09988','E00868','E00968','E00027','E06098','E01113','E00011','E00316','E06821','E03968','E00067','E09699',
# 	'NBGNE','NBIDU','NBABA','NTSM','NNTES','NSIMO','NJD','NZLAB','NPDD','NBILI','NYY','NAMZN','NGOOG','NBKNG','NAZO',
# 	'B600519','B600111','B601888','B601012','B600406','B600887','B600188','B688185','B603888','B600025',
# 	'A300782','A002241','A002594','A300014','A300750','A000858',
# ]
# fundInfoList=[
# 	('MLU1342487771USD','USD','1791623812449431'),
# 	('MLU0971552830HKD','HKD','3741585132364237'),
# 	('MLU0270814014USD','USD','6931628762511615'),
# 	('MHK0000464252HKD','HKD','6941623812448506'),
# 	('MLU0765755177CNY','CNY','9571624411606721'),
# 	('MHK0000434438USD','USD','9021624842276783'),
# 	('MLU1021289076USD','USD','3431581673088952'),
# 	('MHK0000098829CNH','CNH','8561624589295978'),
# 	('MLU0676280554CAD','CAD','4361627027552192'),
# 	('MLU0516397667USD','USD','6401623812440839'),
# 	('MHK0000039690AUD','AUD','9191627027550958'),
# 	('MLU0149524976HKD','HKD','5651623812438646'),
# 	('MLU0788109634USD','USD','4581623808381695'),
# 	('MLU0969580561USD','USD','4241623808379159'),
# 	('MLU0910996080GBP','GBP','3901627027554484'),
# 	('MLU1516285753HKD','HKD','6021623812442694'),
# 	('MLU0117844026USD','USD','4591581673088951'),
# 	('MLU0028119013EUR','EUR','3091629456128784'),
# 	('MHK0000039658USD','USD','2411623812440238'),
# 	('MLU1791807156HKD','HKD','3601623808381170'),
# 	('MLU0430678424USD','USD','5561628078402439'),
# 	('MCNE100002466CNY','CNY','5551624863129624'),
# ]
# env='uat'
# for account in acc_pool:
# 	sessionDic=login_acc(account,'aaaa1111',env=env,ttl=1)
# # 	openMarket(sessionDic,env)#开通市场
# 	derTest(sessionDic,env)#衍生品

# 	addHOld_ttl(account,'02018','5000','HKG',DW='D',env=env)
# 	addHOld_ttl(account,'BABA','5000','USA',DW='D',env=env)
# 	addHOld_ttl(account,'601398','5000','SHA',DW='D',env=env)
# 	addHOld_ttl(account,'002594','5000','SZA',DW='D',env=env)

# 	addHOld_ttl(account,'00700','5000','HKG',DW='D',env=env)
# 	addHOld_ttl(account,'09898','5000','HKG',DW='D',env=env)
# 	addHOld_ttl(account,'03968','5000','HKG',DW='D',env=env)

# 	addHOld_ttl(account,'BILI','5000','USA',DW='D',env=env)
# 	addHOld_ttl(account,'GOOG','5000','USA',DW='D',env=env)
# 	addHOld_ttl(account,'TSLA','5000','USA',DW='D',env=env)

# 	addHOld_ttl(account,'600519','5000','SHA',DW='D',env=env)
# 	addHOld_ttl(account,'300750','5000','SZA',DW='D',env=env)
# 	addHOld_ttl(account,'002594','5000','SZA',DW='D',env=env)

# 	addOptionalStock(sessionDic,stockList)#自选股
# 	addOptionalFoundation(sessionDic,fundInfoList)#加基金自选

###################################################################################################
