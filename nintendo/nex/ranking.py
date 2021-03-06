
from nintendo.nex.common import NexEncoder, DateTime

import logging
logger = logging.getLogger(__name__)


class RankingOrderParam(NexEncoder):
	version_map = {
		30504: 0
	}

	STANDARD = 0 #1224 ranking
	ORDINAL = 1  #1234 ranking

	def init(self, order_calc, filter_idx, filter_num, time_scope, base_rank, count):
		self.order_calc = order_calc
		self.filter_idx = filter_idx
		self.filter_num = filter_num
		self.time_scope = time_scope
		self.base_rank = base_rank
		self.count = count
		
	def encode_old(self, stream):
		stream.u8(self.order_calc)
		stream.u8(self.filter_idx)
		stream.u8(self.filter_num)
		stream.u8(self.time_scope)
		stream.u32(self.base_rank)
		stream.u8(self.count)
		
	encode_v0 = encode_old


class RankingRankData(NexEncoder):
	version_map = {
		30504: 0
	}
	
	def decode_old(self, stream):
		self.user_id = stream.u32()
		self.unk1 = stream.u64()
		self.rank = stream.u32()
		self.category = stream.u32()
		self.score = stream.u32()
		self.data1 = stream.data()
		self.file_id = stream.u64()
		self.data2 = stream.data()
		
	decode_v0 = decode_old


class RankingResult(NexEncoder):
	version_map = {
		30504: 0
	}
	
	def decode_old(self, stream):	
		self.datas = stream.list(lambda: RankingRankData.from_stream(stream))
		self.total = stream.u32()
		self.datetime = DateTime(stream.u64())
		
	decode_v0 = decode_old
	
	
class RankingStats(NexEncoder):
	version_map = {
		30504: 0
	}
	
	def decode_old(self, stream):
		self.stats = stream.list(stream.double)
	
	decode_v0 = decode_old


class RankingClient:

	METHOD_UPLOAD_SCORE = 1
	METHOD_DELETE_SCORE = 2
	METHOD_DELETE_ALL_SCORES = 3
	METHOD_UPLOAD_COMMON_DATA = 4
	METHOD_DELETE_COMMON_DATA = 5
	METHOD_GET_COMMON_DATA = 6
	METHOD_CHANGE_ATTRIBUTES = 7
	METHOD_CHANGE_ALL_ATTRIBUTES = 8
	METHOD_GET_RANKING = 9
	METHOD_GET_APPROX_ORDER = 10
	METHOD_GET_STATS = 11
	METHOD_GET_RANKING_BY_PID_LIST = 12
	METHOD_GET_RANKING_BY_UNIQUE_ID_LIST = 13
	METHOD_GET_CACHED_TOP_RANKING = 14
	METHOD_GET_CACHED_TOP_RANKINGS = 15

	PROTOCOL_ID = 0x70
	
	MODE_GLOBAL = 0
	MODE_GLOBAL_ME = 1 #Global rankings around me
	MODE_ME = 4 #Me ranking only
	
	STAT_RANKING_COUNT = 1
	STAT_TOTAL_SCORE = 2
	STAT_LOWEST_SCORE = 4
	STAT_HIGHEST_SCORE = 8
	STAT_AVERAGE_SCORE = 0x10

	def __init__(self, back_end):
		self.client = back_end.secure_client

	def delete_all_scores(self, arg):
		logger.info("Ranking.delete_all_scores(%016X)", arg)
		#--- request ---
		stream, call_id = self.client.init_message(self.PROTOCOL_ID, self.METHOD_DELETE_ALL_SCORES)
		stream.u64(arg)
		self.client.send_message(stream)
		
		#--- response ---
		self.client.get_response(call_id)
		logger.info("Ranking.delete_all_scores -> Done")
		
	def upload_common_data(self, data, id=0):
		logger.info("Ranking.upload_common_data(...)")
		#--- request ---
		stream, call_id = self.client.init_message(self.PROTOCOL_ID, self.METHOD_UPLOAD_COMMON_DATA)
		stream.data(data)
		stream.u64(id)
		self.client.send_message(stream)
		
		#--- response ---
		self.client.get_response(call_id)
		logger.info("Ranking.upload_common_data -> done")
		
	def get_common_data(self, id=0):
		logger.info("Ranking.get_common_data(%i)", id)
		#--- request ---
		stream, call_id = self.client.init_message(self.PROTOCOL_ID, self.METHOD_GET_COMMON_DATA)
		stream.u64(id)
		self.client.send_message(stream)
		
		#--- response ---
		stream = self.client.get_response(call_id)
		data = stream.data()
		logger.info("Ranking.get_common_data -> %s", data)
		return data
		
	def get_ranking(self, mode, category, order, arg1=0, arg2=0):
		logger.info("Ranking.get_ranking(%i, %08X, %i - %i, %016X, %08X)", mode, category, order.base_rank + 1, order.base_rank + order.count, arg1, arg2)
		#--- request ---
		stream, call_id = self.client.init_message(self.PROTOCOL_ID, self.METHOD_GET_RANKING)
		stream.u8(mode)
		stream.u32(category)
		order.encode(stream)
		stream.u64(arg1)
		stream.u32(arg2)
		self.client.send_message(stream)
		
		#--- response ---
		stream = self.client.get_response(call_id)
		result = RankingResult.from_stream(stream)
		logger.info("Ranking.get_ranking -> %i results (out of %i total)", len(result.datas), result.total)
		return result
		
	def get_stats(self, category, order, flags=0x1F):
		logger.info("Ranking.get_stats(%08X, %i - %i, %02X)", category, order.base_rank + 1, order.base_rank + order.count, flags)
		#--- request ---
		stream, call_id = self.client.init_message(self.PROTOCOL_ID, self.METHOD_GET_STATS)
		stream.u32(category)
		order.encode(stream)
		stream.u32(flags)
		self.client.send_message(stream)
		
		#--- response ---
		stream = self.client.get_response(call_id)
		result = RankingStats.from_stream(stream)
		logger.info("Ranking.get_stats -> %s", result.stats)
		
		stats = {}
		for i in range(5):
			if flags & (1 << i):
				stats[1 << i] = result.stats[i]
		return stats
		
	def get_ranking_by_pid_list(self, pids, mode, category, order, arg=0):
		logger.info("Ranking.get_ranking_by_pid_list(%s, %i, %08X, <order param>, %016X)", pids, mode, category, arg)
		#--- request ---
		stream, call_id = self.client.init_message(self.PROTOCOL_ID, self.METHOD_GET_RANKING_BY_PID_LIST)
		stream.list(pids, stream.u32)
		stream.u8(mode)
		stream.u32(category)
		order.encode(stream)
		stream.u64(arg)
		self.client.send_message(stream)
		
		#--- response ---
		stream = self.client.get_response(call_id)
		result = RankingResult.from_stream(stream)
		logger.info("Ranking.get_ranking_by_pid_list -> %i results (out of %i total)", len(result.datas), result.total)
		return result
