import traceback,time,logging,datetime
from random import randint,sample

################################################################################
def get_redis(env):
	from rediscluster import RedisCluster
	if env.lower()=='test':
		host_port=[
			{'host':'192.168.**.**','port':7000},{'host':'192.168.**.**','port':7001},
			{'host':'192.168.**.**','port':7002},{'host':'192.168.**.**','port':7003},
			{'host':'192.168.**.**','port':7004},{'host':'192.168.**.**','port':7005}
		]
	elif env.lower()=='uat':
		host_port=[
			{'host':'192.168.**.**','port':7000},{'host':'192.168.**.**','port':7001},
			{'host':'192.168.**.**','port':7002},{'host':'192.168.**.**','port':7003},
			{'host':'192.168.**.**','port':7004},{'host':'192.168.**.**','port':7005}
		]
	redis_conn=RedisCluster(startup_nodes=host_port, decode_responses=True)
	return redis_conn

def delete_redis(key,env):
	conn=get_redis(env)
	logging.info(f'删除{env}环境 key {key}')
	conn.delete(key)
	logging.info(f'删除成功！')
	conn.close()

def getkey_redis(key,env):
	conn=get_redis(env)
	result=conn.get(key)
	logging.info(f'获取{env}环境{key}:{result}')
	conn.close()
	return result
################################################################################
def getDBconn(dbType,env='uat',host=None,user=None,password=None,port=3306):
	# ip=getIP() # pymssql 不支持使用指定IP连接
	if dbType=='mysql':
		import pymysql
		hostDic={'uat':'192.168.**.**','test':'192.168.**.**'}
		if not user:user='******'
		if not password:password='******'
		if not host:host=hostDic[env]
		conn=pymysql.connect(host=host,port=port,user=user,password=password,charset='utf8')
		# conn=pymysql.connect(host=hostDic[env],user=user,password=password,charset='utf8',bind_address=ip)
	elif dbType=='sqlserver':#ABC 数据库
		user='api';password='****'
		hostDic={'uat':'192.168.**.**','test':'192.168.**.**'}
		import pymssql
		conn=pymssql.connect(server=hostDic[env],user=user,password=password)
	return conn

def excuteSQL(sql,dbType='mysql',env='uat',conn=None,keepLive=0):
	if not conn:conn=getDBconn(dbType,env)
	cursor=conn.cursor()
	try:
		if type(sql)==list:
			for s in sql:
				cursor.execute(s)
				logging.info(f'sql执行成功: {s}')
			results=1
		else:
			cursor.execute(sql)
			logging.info(f'执行成功: {sql}')
			results=cursor.fetchall() if sql.startswith('SELECT') else 1
		cursor.close()
		conn.commit()
	except Exception as e:
		conn.rollback() # 事务回滚
		logging.info(f'SQL执行失败 {sql}\n{traceback.format_exc()}')
		results=0
	finally:
		if keepLive:
			return conn
		else:
			conn.close()
			if results:return results
			else:
				logging.info(f'执行失败: {sql}')

def getStockByRand(num=100):
	# sql=f'SELECT market_code,stock_code FROM test_quote_sync.t_stock_info WHERE enable_search=1 AND sec_type=3 ORDER BY RAND() LIMIT {randint(1,num)}'
	# results=excuteSQL(sql,env='test')
	# return list(map(lambda s:''.join(s),results))
	stockList=sample(list(map(lambda s:s.strip(),open('testServices/plugins/stocks.txt','r',encoding='utf-8').readlines())),randint(1,100))
	return stockList

def changeChannel(env,channel='TTL'):
	tableName={'dev':'dev_cmbi_boss','test':'test_cmbi_boss','uat':'cmbi_boss'}
	conn=getDBconn('mysql',env=env,host='192.168.**.**',user='****',password='******')
	now=time.strftime("%Y-%m-%d %X")
	sql=f"UPDATE {tableName[env]}.master_setting SET key_value='{channel.upper()}',update_time='{now}' WHERE id = 14;"
	excuteSQL(sql,conn=conn)

def insertIPO(stockCode,stockName,env='uat'):
	try:
		int(stockCode)
	except ValueError:
		print(f'输入的股票代码有误: {stockCode}')
		sys.exit(0)
	id0=time.strftime('%Y%m%d%H%M%S')
	publishId=f'{id0}96'
	cmbi_deadline=(datetime.date.today()+datetime.timedelta(days=365)).isoformat()
	cancel_deadline=(datetime.date.today()+datetime.timedelta(days=370)).isoformat()
	stock_pub_date=(datetime.date.today()+datetime.timedelta(days=375)).isoformat()

	dbNameDic={'test':'test_cmbi_ipo','uat':'cmbi_ipo'}
	# ipoNo=str(int(getMaxStockpubNo(env,dbNameDic[env]))+1)

	sqlList=[
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PUBLISH_INFO (id,stock_code,stock_name,financing_fee,cash_fee,publish_status,is_sponsor,is_consignee,sort_weight,cmbi_deadline,cancel_deadline,broker_start_time,broker_end_time,stock_pub_eipo_no,result_pub_date,is_valid,created_by,created_at,updated_by,updated_at,publish_date) VALUES ({publishId},'{stockCode}','{stockName}','100.0000','30.0000','WAIT_PUB',NULL,NULL,NULL,'{cmbi_deadline} 16:00:00','{cancel_deadline} 00:00:00',NOW(),'{cancel_deadline} 00:00:00',NULL,'{cancel_deadline} 00:00:00','UP','SYSTEM',NOW(),'SYSTEM',NOW(),NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_DETAIL (id,stock_code,stock_name,currency_unit,trade_unit,subscribe_vol,subscribe_price,prospectus_pub_date,subscribe_start_date,subscribe_end_date,listed_date,entrance_fee,pricing_date,pay_end_date,result_pub_date,stock_pub_date,refundment_date,total_proceeds,pur_price_interval,over_allotment,over_allot_apply_mul,one_lot_winning_rate,event_procedure,issue_type,public_date,jy_update_date,website,is_valid,created_by,created_at,updated_by,updated_at) VALUES ({id0},'{stockCode}','{stockName}','HKD','2000','375000000',NULL,NOW(),NOW(),'{cmbi_deadline} 16:00:00','{cmbi_deadline}','7000.0000','{cmbi_deadline}','{cmbi_deadline} 12:00:00','{cancel_deadline}','{stock_pub_date}','{stock_pub_date}','134062500.00','3.5~4.0','6286600',NULL,NULL,'PREARRANGED','公开发售 配售新股',NOW(),NOW(),'http://10.0.2.83/index.html','Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_CAPITAL_POOL (id,publish_id,financing_program_id,stock_code,stock_name,currency_unit,total_amount,cmbi_financing_amount,used_amount,usage_alert_line,financing_scale_max,financing_scale_min,apply_end_date,reason,pool_status,is_app_fin,fin_limit,created_by,created_at,updated_by,updated_at) VALUES ({id0}95,'{publishId}',NULL,'{stockCode}','{stockName}','HKD','0.0000','0.0000','0.0000','95.0000','90.0000','5.0000','{cmbi_deadline} 16:00:00','INIT_CLOSE','CLOSE',1,NULL,'AutoTest',NOW(),'AutoTest',NOW());",
		# f"INSERT INTO {dbNameDic[env]}.T_EIPO_FINANCING_RATE_PROGRAM (id,program_name,program_desc,is_valid,created_by,created_at,updated_by,updated_at) VALUES ({id0}99,'{stockCode}','{stockName}','Y','148',NOW(),'148',NOW())",
		# f"INSERT INTO {dbNameDic[env]}.T_EIPO_FINANCING_RATE_PROGRAM_DETAIL (id,program_id,serial_no,financing_amount_min,financing_amount_max,financing_rate,created_by,created_at,updated_by,updated_at) VALUES ({id0}97,'{id0}99','1','0.0000','1000000.0000','2.0000','148',NOW(),'148',NOW())",
		# f"INSERT INTO {dbNameDic[env]}.T_EIPO_FINANCING_RATE_PROGRAM_DETAIL (id,program_id,serial_no,financing_amount_min,financing_amount_max,financing_rate,created_by,created_at,updated_by,updated_at) VALUES ({id0}98,'{id0}99','2','1000000.0000','999999999.9900','5.0000','148',NOW(),'148',NOW())",

		# f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM (id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}01','{stockCode}','{stockName}','1','2000.0000','0.0000','7000.0000','HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		# f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM (id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}02','{stockCode}','{stockName}','2','4000.0000','0.0000','14000.0000','HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		# f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM (id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}03','{stockCode}','{stockName}','3','8000.0000','0.0000','28000.0000','HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		# f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM (id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}04','{stockCode}','{stockName}','4','16000.0000','0.0000','56000.0000','HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		# f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM (id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}05','{stockCode}','{stockName}','5','32000.0000','0.0000','112000.0000','HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		# f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM (id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}06','{stockCode}','{stockName}','6','64000.0000','0.0000','224000.0000','HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		# f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM (id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}07','{stockCode}','{stockName}','7','128000.0000','0.0000','448000.0000','HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		# f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM (id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}08','{stockCode}','{stockName}','8','256000.0000','0.0000','896000.0000','HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		# f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM (id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}09','{stockCode}','{stockName}','9','512000.0000','0.0000','1792000.0000','HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		# f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM (id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}10','{stockCode}','{stockName}','10','1024000.0000','0.0000','3584000.0000','HKD','Y',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",

		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}1','{stockCode}','{stockName}','1',500.0000,0.0000,9999.7700,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}2','{stockCode}','{stockName}','2',1000.0000,0.0000,19999.5200,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}3','{stockCode}','{stockName}','3',1500.0000,0.0000,29999.2900,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}4','{stockCode}','{stockName}','4',2000.0000,0.0000,39999.0500,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}5','{stockCode}','{stockName}','5',2500.0000,0.0000,49998.8200,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}6','{stockCode}','{stockName}','6',3000.0000,0.0000,59998.5700,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}7','{stockCode}','{stockName}','7',3500.0000,0.0000,69998.3400,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}8','{stockCode}','{stockName}','8',4000.0000,0.0000,79998.1000,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}9','{stockCode}','{stockName}','9',4500.0000,0.0000,89997.8700,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}10','{stockCode}','{stockName}','10',5000.0000,0.0000,99997.6200,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}11','{stockCode}','{stockName}','11',6000.0000,0.0000,119997.1500,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}12','{stockCode}','{stockName}','12',7000.0000,0.0000,139996.6700,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}13','{stockCode}','{stockName}','13',8000.0000,0.0000,159996.2000,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}14','{stockCode}','{stockName}','14',9000.0000,0.0000,179995.7200,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}15','{stockCode}','{stockName}','15',10000.0000,0.0000,199995.2500,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}16','{stockCode}','{stockName}','16',15000.0000,0.0000,299992.8700,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}17','{stockCode}','{stockName}','17',20000.0000,0.0000,399990.4900,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}18','{stockCode}','{stockName}','18',25000.0000,0.0000,499988.1200,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}19','{stockCode}','{stockName}','19',30000.0000,0.0000,599985.7400,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}20','{stockCode}','{stockName}','20',35000.0000,0.0000,699983.3600,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}21','{stockCode}','{stockName}','21',40000.0000,0.0000,799980.9800,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}22','{stockCode}','{stockName}','22',45000.0000,0.0000,899978.6100,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}23','{stockCode}','{stockName}','23',50000.0000,0.0000,999976.2300,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}24','{stockCode}','{stockName}','24',60000.0000,0.0000,1199971.4800,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}25','{stockCode}','{stockName}','25',70000.0000,0.0000,1399966.7200,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}26','{stockCode}','{stockName}','26',80000.0000,0.0000,1599961.9700,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}27','{stockCode}','{stockName}','27',90000.0000,0.0000,1799957.2100,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}28','{stockCode}','{stockName}','28',100000.0000,0.0000,1999952.4600,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}29','{stockCode}','{stockName}','29',200000.0000,0.0000,3999904.9200,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}30','{stockCode}','{stockName}','30',300000.0000,0.0000,5999857.3800,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}31','{stockCode}','{stockName}','31',400000.0000,0.0000,7999809.8400,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}32','{stockCode}','{stockName}','32',500000.0000,0.0000,9999762.3000,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}33','{stockCode}','{stockName}','33',600000.0000,0.0000,11999714.7600,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}34','{stockCode}','{stockName}','34',700000.0000,0.0000,13999667.2200,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}35','{stockCode}','{stockName}','35',800000.0000,0.0000,15999619.6800,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}36','{stockCode}','{stockName}','36',900000.0000,0.0000,17999572.1400,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}37','{stockCode}','{stockName}','37',1000000.0000,0.0000,19999524.6000,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}38','{stockCode}','{stockName}','38',2000000.0000,0.0000,39999049.2000,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}39','{stockCode}','{stockName}','39',3000000.0000,0.0000,59998573.8000,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}40','{stockCode}','{stockName}','40',4000000.0000,0.0000,79998098.4000,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}41','{stockCode}','{stockName}','41',5000000.0000,0.0000,99997623.0000,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}42','{stockCode}','{stockName}','42',6000000.0000,0.0000,119997147.6000,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}43','{stockCode}','{stockName}','43',7000000.0000,0.0000,139996672.2000,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}44','{stockCode}','{stockName}','44',8000000.0000,0.0000,159996196.8000,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}45','{stockCode}','{stockName}','45',9000000.0000,0.0000,179995721.4000,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}46','{stockCode}','{stockName}','46',10000000.0000,0.0000,199995246.0000,'HKD','N',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",
		f"INSERT INTO {dbNameDic[env]}.T_EIPO_STOCK_SUBSCRIBE_PROGRAM(id,stock_code,stock_name,serial_number,apply_subscribe_num,apply_num_rate,pay_able,currency_unit,is_can_apply_max,public_date,jy_update_date,is_valid,created_by,created_at,updated_by,updated_at) VALUES ('{id0}47','{stockCode}','{stockName}','47',12863500.0000,0.0000,257263884.7000,'HKD','Y',NOW(),NOW(),'Y','SYSTEM',NOW(),'SYSTEM',NOW());",

	]
	return publishId,cmbi_deadline,sqlList

def addPortfolio(account,env='uat'):
	sql_del=f"DELETE FROM IBFront.dbo.ClntPortfolio WHERE ClntCode='{account}'"
	excuteSQL(sql_del,dbType='sqlserver',env=env,conn=None)
	sql=[
		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','ALL','CNY','{account}','Renminbi','',N'现金',757.89000000,'CNY',1.00000000,757.89000000,1.22180000,925.99000000);",
		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','ALL','HKD','{account}','Hong Kong Dollar','',N'现金',8461.89000000,'HKD',1.00000000,8461.89000000,1.22180000,9841.87000000);",
		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','ALL','USD','{account}','US Dollar','',N'现金',9784.86000000,'USD',1.00000000,9784.86000000,1.22180000,8971.43000000);",

		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','ALL','GBP','{account}','GBP Dollar','',N'现金',3465.45000000,'GBP',1.00000000,3465.45000000,1.22180000,9753.43000000);",
		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','ALL','AUD','{account}','AUD Dollar','',N'现金',6793.45000000,'AUD',1.00000000,6793.45000000,1.22180000,5682.43000000);",
		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','ALL','CHF','{account}','CHF Dollar','',N'现金',7445.84000000,'CHF',1.00000000,7445.84000000,1.22180000,8356.43000000);",
		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','ALL','EUR','{account}','EUR Dollar','',N'现金',3456.35000000,'EUR',1.00000000,3456.35000000,1.22180000,9537.43000000);",
		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','ALL','JPY','{account}','JPY Dollar','',N'现金',4784.24000000,'JPY',1.00000000,4784.24000000,1.22180000,6368.43000000);",
		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','ALL','MYR','{account}','MYR Dollar','',N'现金',5478.68000000,'MYR',1.00000000,5478.68000000,1.22180000,5725.43000000);",
		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','ALL','RUB','{account}','RUB Dollar','',N'现金',2367.57000000,'RUB',1.00000000,2367.57000000,1.22180000,6793.43000000);",
		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','ALL','SGD','{account}','SGD Dollar','',N'现金',5683.85000000,'SGD',1.00000000,5683.85000000,1.22180000,6793.43000000);",


		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','FUN','ALLHKDINACC','{account}','Allianz HKD Income - Class at ACC','',N'另类及其他',350000.00000000,'HKD',10.59000000,3706500.00000000,1.00000000,3706500.00000000);",
		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','BND','333.GF','{account}','DECHENG TECHNOLOGY AG (FRANKFURT)','',N'股票类',2000.00000000,'EUR',0.83000000,1660.00000000,9.67300000,16057.18000000);",
		f"INSERT INTO IBFront.dbo.ClntPortfolio VALUES ('2021-11-11 00:00:00','FUN','AHKDIAR LX','{account}','Allianz HKD Income Fund (AM-Dis) Cash','',N'固定收益类',355691.05700000,'HKD',9.93000000,3532012.19601000,1.00000000,3532012.19601000);",
	]
	excuteSQL(sql,dbType='sqlserver',env=env,conn=None)

def del_pwdHistory(account,env='uat'):
	sql=f"DELETE FROM OctOSTP_Front.dbo.ClntPasswordsReuseHistory WHERE ClntCode='{account}'"
	result=excuteSQL(sql,dbType='sqlserver',env=env)
	return result

def del_market(account,env='test',conn=None):
	if not conn:conn=getDBconn('mysql',env=env,host='192.168.**.**',user='cms',password='******',port=8066)
	tableName={'dev':'dev_cmbi_boss','test':'test_cmbi_boss','uat':'cmbi_boss'}
	sql=f"DELETE FROM {tableName[env]}.cms_account_market WHERE accountid='{account}' AND market!='HKG';"
	conn=excuteSQL(sql,conn=conn,keepLive=1)
	return conn

if __name__ == '__main__':
	changeChannel('uat',channel='TTL')