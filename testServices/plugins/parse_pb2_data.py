# from .pb2 import Common_pb2
# from .pb2 import Qot_Common_pb2
# from .pb2 import Qot_GetTimeShare_pb2
# from .pb2 import Qot_UpdateOrderBook_pb2
# from .pb2 import InitConnect_pb2
# from .pb2 import Qot_GetOrderBook_pb2
# from .pb2 import Qot_Sub_pb2
# from .pb2 import Qot_UpdateSnapshotQot_pb2
# from .pb2 import KeepAlive_pb2
# from .pb2 import Qot_GetSnapshotQot_pb2
# from .pb2 import Qot_UpdateBasicQot_pb2
# from .pb2 import Qot_GetBasicQot_pb2

# from .pb2 import pbjson
# import struct,json

# def parseData(data,types='response'):
# 	msgReqTemplate="!******"
# 	try:
# 		protoId,protoFormatType,protoVersion,packetSeqNum,bodyLength,bodySHA1,reserve=struct.unpack(msgReqTemplate,data[:42])
# 	except struct.error:
# 		return {"msg":f"无效数据: {data}"}
# 	if types=='response':
# 		if protoId==1001:
# 			rsp=InitConnect_pb2.Response()
# 		elif protoId==1004:
# 			rsp=KeepAlive_pb2.Response()
# 		elif protoId==3001:
# 			rsp=Qot_Sub_pb2.Response()
# 		elif protoId==3004:
# 			rsp=Qot_GetBasicQot_pb2.Response()
# 		elif protoId==3005:
# 			rsp=Qot_GetSnapshotQot_pb2.Response()
# 		elif protoId==3008:
# 			rsp=Qot_GetTimeShare_pb2.Response()
# 		elif protoId==3012:
# 			rsp=Qot_GetOrderBook_pb2.Response()
# 		elif protoId==3303:
# 			rsp=Qot_UpdateOrderBook_pb2.Response()
# 		elif protoId==3302:
# 			rsp=Qot_UpdateBasicQot_pb2.Response()
# 		elif protoId==3301:
# 			rsp=Qot_UpdateSnapshotQot_pb2.Response()
# 		else:
# 			return {"protoId":-999,"msg":f"未知的 protoId: {protoId}"}
# 	# elif types=='request':
# 	# 	if protoId==1001:
# 	# 		rsp=InitConnect_pb2.Request()
# 	# 	elif protoId==1004:
# 	# 		rsp=KeepAlive_pb2.Request()
# 	# 	elif protoId==3001:
# 	# 		rsp=Qot_Sub_pb2.Request()
# 	# 	elif protoId==3004:
# 	# 		rsp=Qot_GetBasicQot_pb2.Request()
# 	# 	elif protoId==3005:
# 	# 		rsp=Qot_GetSnapshotQot_pb2.Request()
# 	# 	elif protoId==3008:
# 	# 		rsp=Qot_GetTimeShare_pb2.Request()
# 	# 	elif protoId==3012:
# 	# 		rsp=Qot_GetOrderBook_pb2.Request()
# 	# 	elif protoId==3303:
# 	# 		rsp=Qot_UpdateOrderBook_pb2.Request()
# 	# 	elif protoId==3302:
# 	# 		rsp=Qot_UpdateBasicQot_pb2.Request()
# 	# 	elif protoId==3301:
# 	# 		rsp=Qot_UpdateSnapshotQot_pb2.Request()
# 	# 	else:
# 	# 		return {"protoId":-999,"msg":f"未知的 protoId: {protoId}"}
# 	try:
# 		rsp.ParseFromString(data[42:])
# 	except:
# 		return {"msg":f"无效数据: {data}"}
# 	result=json.loads(str(pbjson.pb2json(rsp)))
# 	result["protoId"]=protoId
# 	return result

# if __name__ == '__main__':
# 	data=bytes.fromhex(str("03E9 0000 0000 0001 B411 0000 0066 6E59 B834 469E 26FF 4D78 2030 E271 9252 D53C B2A4 0000 0000 0000 0000 2264 0801 1222 675F 3066 6164 6466 6134 3130 3136 3431 3338 3933 3837 3838 3238 3134 6438 3437 3539 1A2F 5F5F 7665 7274 782E 7773 2E61 3434 6533 6637 382D 3931 6266 2D34 3239 302D 6137 3636 2D38 6533 6164 3463 3230 3236 3538 FFFF FFFF FFFF FFFF FF01 4A00"))
# 	rsp=parseData(data)
# 	print(rsp)