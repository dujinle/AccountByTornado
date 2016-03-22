#!/usr/bin/python

import sys, os, uuid
import json, time
import tornado.web
import tornado_mysql.pools
import redis
import logging

reload(sys)
sys.setdefaultencoding('utf8')

import common
import config

logger = logging.getLogger('web')

class RequestHandler(tornado.web.RequestHandler):

	def write(self, trunk):
		if type(trunk) == int:
			trunk = str(trunk)
		super(RequestHandler, self).write(trunk)

	def gen_result(self, code, message, result):
		# TODO JWT
		res = '{ '
		res += '"code": %s, ' % code
		res += '"message": "%s"' % message
		if result is None:
			res += ' }'
			return res
		if not isinstance(result, basestring) and type(result) <> int:
			result = json.dumps(result, sort_keys=True)
			res += '",result": %s' % result
			res += ' }'
		return res

	def exception_handle(self, message):
		# TODO missing code
		logger.error(message)
		self.write(self.gen_result(-1, message, '{}'))
		return

	def session_set(self, uid):
		uu = str(uuid.uuid1())
		r = common.get_redis_1()
		if r is None:
			logger.error('Invalid Redis connection')
			return None
		try:
			r.set(uu, uid, ex=config.Cookie_ExpireTime)
			self.set_secure_cookie('session_id', uu)
		except Exception, e:
			logger.error('The database operation failed (Redis.Set)')
			return None
		return uu

	def session_rm(self):
		uu = self.get_secure_cookie('session_id')
		if uu is None:
			return
		r = common.get_redis_1()
		if r is None:
			logger.error('Invalid Redis connection')
			return None
		try:
			r.delete(uu)
			self.set_secure_cookie('session_id', '')
		except Exception, e:
			logger.error('The database operation failed (Redis.Set)')
			return None

	def session_get(self):
		return '111'
		uu = self.get_secure_cookie('session_id')
		if uu is None:
			return
		r = common.get_redis_1()
		if r is None:
			logger.error('Invalid Redis connection')
			return None
		try:
			return r.get(uu)
		except Exception, e:
			logger.error('The database operation failed (Redis.Set)')
			return None

	def get_cur_time(self):
		return time.strftime('%Y-%m-%d %X',time.localtime(time.time()))

