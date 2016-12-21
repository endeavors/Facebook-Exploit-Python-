'''Collect usernames of Facebook IDs. You must log into a Facebook account 
to do this. Why? Security measures are less defensive when you are logged in'''

from urllib2 import URLError
from bs4 import BeautifulSoup
from Queue import Queue
import json, io, mechanize, cookielib, re, urllib2, requests
import time, ssl,sys,math, threading


ssl._create_default_https_context = ssl._create_unverified_context

base_url = "https://mbasic.facebook.com/"
header_def = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1"
keys = []
num_threads = 90
res_dict = {}
id_dict = {}
save_loc = "./Extracts/UserFractals/"
lock = threading.Lock()

que = Queue(maxsize=0)
browser = mechanize.Browser()
cj = cookielib.LWPCookieJar()
browser.set_cookiejar(cj)

browser.set_handle_equiv(False)
browser.set_handle_redirect(mechanize.HTTPRedirectHandler)
browser.set_handle_referer(True)
browser.set_handle_robots(False)
browser.set_handle_refresh(False)
browser.addheaders = [('User-agent', header_def)]

startlimit = 0 
endlimit = 0
run = 65

counter = startlimit

class ThreadWorker(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue

	def run(self):
		while self.queue.qsize() != 0:
			curr_idx = self.queue.get(timeout=10)
			gather(keys[curr_idx])
			self.queue.task_done()

def write_to_file():
	print "Writing to file"
	lock.acquire()
	with open(save_loc + "name" + str(run) + ".json", "w") as outfile:
		json.dump(res_dict, outfile, sort_keys=True, indent=4, ensure_ascii=False)
	lock.release()

def alternative_sol(userid):
	
	lock.acquire()

	username = None
	browser.open(base_url)
	browser.select_form(nr=0)
	browser['query'] = id_dict[userid]["name"]
	res = browser.submit()
	
	soup = BeautifulSoup(res.read(), "html.parser")
	profile_link = soup.findAll("table")[1].findAll("tr")[0].findAll("a")[0].get("href")
	req = browser.click_link(url=profile_link)
	res = browser.open(req)

	soup = BeautifulSoup(res.read(), "html.parser")
	if len(soup.findAll(href=re.compile(str(userid)))) != 0:
		table = soup.findAll("table")
		index = -1
		for i in range(len(table)):
			contacts = table[i].findAll("td")
			for idx, contact in enumerate(contacts):
				if len(contact.findAll(text="Contact Info")) != 0:
					index = i + 1
					break
		print "index:", index
		if index != -1:
			username = table[index].findAll("td")[1].text
			if username != None or username != "":
				mgroup = re.match(r"^\/([\w.]+)$", username.strip())
				if mgroup != None:
					username = mgroup.group(1).strip()

	lock.release()
	return username

def gather(key):
	global counter, res_dict 

	try:
		url = "https://www.facebook.com/" + str(key)
		request = urllib2.Request(url, None, {'User-agent':header_def})
		response = urllib2.urlopen(request)
		endurl = response.geturl()

		matcher = re.match(r".*\/([\w.]+)\??.*",endurl)
		if matcher:
			username = matcher.group(1)
			if not username.isdigit():
				res_dict[key] = username
			print counter, username, key
			counter += 1
		
		if counter % 500 == 0:
			write_to_file()

	except URLError, e:
		if hasattr(e, "code"):
			if e.code != 404 and e.code != 400:
				print "CODE:", e.code, "IDX:", counter
			elif e.code == 404:
				counter += 1
				print counter, "404 Error --- Skipping"

		elif hasattr(e, "reason"):
			print "REASON:", e.reason, "IDX:", counter
		
	except KeyboardInterrupt:
		print "KeyboardInterrupt AT IDX:", counter
		write_to_file()
		sys.exit()
	except Exception, e:
		write_to_file()
		print "EXCEPTION", str(e), "IDX:", counter
		sys.exit()

def spawn():
	for x in xrange(num_threads):
		thread = ThreadWorker(que)
		thread.daemon = True
		thread.start()

def add_keys_to_queue():
	global que, endlimit

	count = startlimit
	if endlimit <= startlimit:
		endlimit = len(keys)
	while count < endlimit:
		que.put(count)
		count += 1

def read_input_file():
	global keys, id_dict

	print "Reading json file"
	with open("./Extracts/IDFractals/collect_id17.json","r") as jfile:
		id_dict = json.load(jfile)
	keys = sorted(id_dict.keys())


def login():
	global browser
	print "Logging in"
	browser.open(base_url)
	browser.select_form(nr=0)

	browser['email'] = ''
	browser['pass'] = ''
	res = browser.submit("login")
	
if __name__ == '__main__':
	#login()
	read_input_file()
	add_keys_to_queue()
	spawn()
	que.join()
	write_to_file()
