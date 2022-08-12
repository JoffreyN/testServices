import time,logging
from django.utils.deprecation import MiddlewareMixin
from django.http.response import HttpResponse
from django.core.cache import caches

# 频率限制访问 30秒内30次拉黑20分钟，
class IpLimitMiddleware(MiddlewareMixin):
	def process_request(self,request):
		ip=request.META.get("REMOTE_ADDR")

		cache=caches['default']# 选择缓存的数据库 redis缓存
		black_list=cache.get('black',[])# 获取黑名单

		if ip in black_list:
			return HttpResponse("黑名单用户！联系开发者。")
		requests=cache.get(ip,[])
		while requests and time.time()-requests[-1]>30:# 如果值存在，且当前时间-最后一个时间>30 则清洗掉这个值
			requests.pop()

		requests.insert(0,time.time())# 若没有存在值，则添加，
		cache.set(ip,requests,timeout=30)# 过期时间为30秒，这个过期时间与上面判断的30 保持一致

		if len(requests)>30:# 如果访问次数大于30次，拉入黑名单，封20分钟
			black_list.append(ip)
			cache.set('black',black_list,timeout=60*20)

		logging.info(f"{ip} 访问次数: {len(requests)}")
		if len(requests)>10:# 限制访问次数为 30秒内10 次
			return HttpResponse("请求过于频繁，请稍后重试！")
