#coding:utf-8

import sqlite3,time
import threading

class dbhand:
	def __init__(self,logger):
		self.logger=logger
		self.lock = threading.Lock()
	def dbconnect(self,db):
		self.dbconn=None
		try:
			self.dbconn=sqlite3.connect(db,check_same_thread = False)
			self.con=self.dbconn.cursor()
			self.logger.info("数据库已连接")
			print "数据库已连接"
		except  Exception as e:
			self.logger.error("数据库连接失败")
			print "数据库连接失败"
			quit()
	def init(self):
		'''
		初始化,建表
		链接,标题
		:return:
		'''
		try:
			sql="create table  if not EXISTS urls(url text PRIMARY KEY,title text not NULL,Done Int DEFAULT 0)"
			self.con.execute(sql)
			self.logger.info("数据表初始化成功.")
			print "数据表初始化成功."
		except:
			self.logger.error("数据表初始化失败.")
			pass
	def insert(self,hash,table):
		url=[]
		try:
			for k,v in hash.items():
				url.append((k,v))
			sql1=' insert or ignore into urls (url,title)VALUES(?,?)'
			self.lock.acquire(True)
			self.con.executemany(sql1,url)
		except sqlite3.IntegrityError:
			self.logger.info("数据插入失败.")
			print time.strftime("%H:%M:%S",time.localtime()),"数据插入失败."
			return
		except Exception as e:
			print e
		else:
			self.commitall()
			self.logger.info("数据插入成功.")
			print time.strftime("%H:%M:%S",time.localtime()),"数据插入成功."
		finally:
			 self. lock.release()

	def update(self,url,Done=1):
		sql='update urls set Done=%d where url="%s"'%(Done,url)
		try:
			self.lock.acquire(True)
			self.con.execute(sql)
		except Exception as e:
			print sql,'\n',e
		else:
			self.commitall()
			self.logger.info("数据更新成功.")
			# print "数据更新成功."
		finally:
			self.lock.release()
	def commitall(self):
		try:
			self.dbconn.commit()
		except sqlite3.IntegrityError:
			print
		except:
			pass
	def geturl(self,keys='xinggan',done=0):
		info={}
		sql="select url,title from urls where url like '%"+keys+"%'" +" and done=%d"%done
		try:
			self.con.execute(sql)
			for i in self.con.fetchall():
				info[i[0]]=i[1]
		except:
			pass
		return  info
	def getOne(self,table,var='*',where=''):
		sql="select "+var+" from "+table+where
		self.con.execute(sql)
		result=self.con.fetchone()
		return result[1]
