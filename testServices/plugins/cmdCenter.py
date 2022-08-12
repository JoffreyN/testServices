import subprocess,time

def executeCmd(cmd):
	try:
		result=subprocess.getoutput(cmd)
		return {'success':1,'result':result}
	except Exception as err:
		return {'success':0,'cmd':cmd,'result':f'执行失败: {err}'}

def getProcess(name):
	cmd_resp=executeCmd(f'ps -ef|grep {name}')
	return cmd_resp



def getProcessID(cmd_resp):
	cmd_resp_list=cmd_resp.split('\n')
	return [i.split()[1] for i in cmd_resp_list if 'grep' not in i]

def kill_process(name):
	cmd_resp=getProcess(name)
	if cmd_resp['success']:
		processID=getProcessID(cmd_resp['result'])
		if len(processID)>0:
			return executeCmd(f'kill {" ".join(processID)}')
		else:
			return {'success':0,'result':f'没有找到 {name} 相关进程'}

def server_appium_wda(method,ports):
	ports=ports.strip().split()
	port_wda={'8100':'start_wda_11ProMax.sh','8101':'start_wda_11Pro.sh','8102':'start_wda_11.sh','8103':'start_wda_11ProMax_13.6.sh'}
	result={}
	if method=='start':
		for port in ports:
			if port in ['4723','4725','4727','4729','4731','4733','4735','4737']:
				result[port]=executeCmd(f'sh ~/zp/bin/startAppium_{port}.sh')
			elif port in ['8100','8101','8102','8103']:
				result[port]=executeCmd(f'sh ~/zp/bin/{port_wda[port]}')
				time.sleep(10)
	elif method=='stop':
		for port in ports:
			result[port]=kill_process(port)
	return result

def start_UItest(shellNames):
	executeCmd('git -C ~/zp/myCode/appAutoTest pull')
	if '发送邮件' in shellNames:
		shellNames=shellNames.replace('发送邮件','')
		sendmail='--sendMail'
	else:
		sendmail=''
	shellNames=shellNames.split()
	result={}
	for shellName in shellNames:
		result[shellName]=executeCmd(f'sh ~/zp/myCode/appAutoTest/{shellName} {sendmail}')
	return result

def kill_processID(processID):
	return executeCmd(f'kill {processID}')
