#!/usr/bin/python

import sys, os
import tornado.ioloop
import tornado.web
import tornado.httpserver
import logging
import logging.handlers
import re
from urllib import unquote

import config
from travellers import *

reload(sys)
sys.setdefaultencoding('utf8')

def deamon(chdir = False):
	try:
		if os.fork() > 0:
			os._exit(0)
	except OSError, e:
		print 'fork #1 failed: %d (%s)' % (e.errno, e.strerror)
		os._exit(1)

def init():
	pass

class DefaultHandler(tornado.web.RequestHandler):
	def get(self):
		self.write('Travellers Say Hello! (v%s)' % config.VERSION)

class LogHandler(tornado.web.RequestHandler):
	def get(self):
		log_filename = 'logs/logging'
		if not os.path.exists(log_filename):
			self.write('The log file is empty.')
			return
		log_file = None
		log_file_lines = None
		try:
			log_file = open(log_filename, 'r')
			if log_file is None:
				raise Exception('log_file is None')
			log_file_lines = log_file.readlines()
			if log_file_lines is None:
				raise Exception('log_file_lines is None')
		except Exception, e:
			logger = logging.getLogger('web')
			logger.error('Failed to read the log file (logs/logging), error: %s' % e)
		finally:
			if log_file is not None:
				log_file.close()
		if log_file_lines is None:
			self.write('Failed to read the log file.')
		line_limit = 500
		for _ in log_file_lines[::-1]:
			line_limit -= 1
			if line_limit > 0:
				self.write(unquote(_) + '<BR/>')


settings = {
	"static_path": os.path.join(os.path.dirname(__file__), "static"),
	"cookie_secret": "SAB8LF2sGBflryMb6eXFkX#ou@CNta9V",
}

routes = [
	(r"/", DefaultHandler),
	(r"/api/user/authkey", AuthKeyHandler), # Send AuthKey (POST)(JWT)
	(r"/api/user/register", RegisterHandler), # Register (POST)(JWT)
	(r"/api/user/login", LoginHandler), # Login (POST)(JWT)
	(r"/api/user/logout", LogoutHandler), # Logout (POST)
	(r"/api/user/reset", ResetHandler), # Reset password (POST)(JWT)
	(r"/api/user/forget", ForgetHandler), # Forget password (POST)(JWT)
	(r"/api/user/update", UUpdateHandler), # UserUpdate (GET/POST)
	(r"/api/user/getuser", GetUserHandler), # GetUser (GET/POST)
	(r"/api/user/getall", GetAllMbersHandler), # GetAllUsers (GET/POST)
	(r"/api/user/icon", AvatarHandler), # UpdateIcon (GET/POST)
	(r"/api/user/geticon", GetIconHandler), # GetIcon (GET/POST)
	(r"/api/user/pos", PostionHandler), # Update Pos info (GET/POST)
	(r"/api/group/create", AddGroupHandler), # AddGroup (GET/POST)
	(r"/api/group/destroy", DelGroupHandler), # DelGroup (GET/POST)
	(r"/api/group/join", AddMemberHandler), # AddMember (GET/POST)
	(r"/api/group/quit", DelMemberHandler), # DelMember (GET/POST)
	(r"/api/group/getgroup", GetMembersHandler), # GerMembers (GET/POST)
	(r"/api/group/rename", RenameGroupHandler), # GerMembers (GET/POST)
	(r"/api/group/setshare",SetPosShareHandler), # GerMembers (GET/POST)
]

if config.Mode == 'DEBUG':
	routes.append((r"/log", LogHandler))

application = tornado.web.Application(routes, **settings)

if __name__ == "__main__":
	if '-d' in sys.argv:
		deamon()
	logdir = 'logs'
	if not os.path.exists(logdir):
		os.makedirs(logdir)
	fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
	formatter = logging.Formatter(fmt)
	handler = logging.handlers.TimedRotatingFileHandler(
		'%s/logging' % logdir, 'M', 20, 360)
	handler.suffix = '%Y%m%d%H%M%S.log'
	handler.extMatch = re.compile(r'^\d{4}\d{2}\d{2}\d{2}\d{2}\d{2}')
	handler.setFormatter(formatter)
	logger = logging.getLogger('web')
	logger.addHandler(handler)
	if config.Mode == 'DEBUG':
		logger.setLevel(logging.DEBUG)
	else:
		logger.setLevel(logging.ERROR)

	init()

	if '-P' in sys.argv:
		http_server = tornado.httpserver.HTTPServer(application)
		http_server.bind(8080, '0.0.0.0')
		http_server.start() #TODO Based on CPU kernel number
		print 'Server is running, listening on port 80....'
		tornado.ioloop.IOLoop.instance().start()
	else:
		http_server = tornado.httpserver.HTTPServer(application)
		application.listen(8080)
		print 'Server is running, listening on port 80....'
		tornado.ioloop.IOLoop.instance().start()

