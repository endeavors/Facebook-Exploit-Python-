#!python3

from Queue import Queue
from fake_useragent import UserAgent
from cred import USER, PASS, PROX_URL, PORT, SAUCE_USERNAME, SAUCE_ACCESS_KEY
from utility import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.proxy import *
import httpagentparser
import json, io, threading

START_QUEUE = 0
END_QUEUE = 2000000

num_threads = 100
num_skipped = 0

base_url = "https://mbasic.facebook.com/"
usernames = []
queue = Queue(maxsize=0)
useragent = UserAgent()
counter = START_QUEUE

class ThreadWorker(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		options,srv = self.getCapability()
		self.driver = webdriver.PhantomJS("./phantomjs",desired_capabilities=options,
			service_args=srv)

	def run(self):
		while self.queue.qsize() != 0:
			username = self.queue.get()
			self.send_email(self.driver, username)
    		self.queue.task_done()
    		
	def getCapability(self):
		phan_dict = webdriver.DesiredCapabilities.PHANTOMJS
		agent = useragent.chrome
		phan_dict["phantomjs.page.settings.userAgent"] = agent
		platform = httpagentparser.detect(agent)
		try:
			phan_dict["platform"] = platform["os"]["name"]
		except Exception,e:
			phan_dict["platform"] = "Windows"

		phan_dict["browserName"] = "Chrome"
		phan_dict["version"] = platform["browser"]["version"]
		
		service_args = [
			"--proxy=" + PROX_URL + ":" + PORT,
			"--proxy-auth=" + USER + ":" + PASS,
			"--proxy-type=http"
		]
	
		return phan_dict, service_args

	def send_email(self, driver, username):
		global counter

		security_check = "Security Check"
		
		try:
			driver.get(base_url)
			pass_elem = driver.find_elements_by_link_text("Forgot Password?")[0]
			pass_elem.click()
			usr_elem = driver.find_element_by_name("email")
			usr_elem.clear()
			usr_elem.send_keys(username) 
			usr_elem.send_keys(Keys.RETURN)

			if driver.title != security_check and driver.title != \
				"Find Your Account":
				try:
					email_elem = driver.find_element_by_xpath(\
					"//input[@name='recover_method'][@value='send_email']")
					email_elem.click()
				except Exception:
					pass
				cont_elem = driver.find_element_by_name("reset_action")
				cont_elem.click()
				counter += 1
				print "SUCCESS:", driver.title, username, counter
			else:
				raise Exception(driver.title)
		except Exception, e:
			global num_skipped
			num_skipped += 1
			counter += 1
			print "FAILED:", username, "NUM_SKIP:", num_skipped, str(e), counter
		
		driver.delete_all_cookies()
		#driver.quit()

def spawn_browser_instances():
	threads = []
	for x in xrange(num_threads):
		thread = ThreadWorker(queue)
		thread.daemon = True
		threads.append(thread)

	for x in range(num_threads):
		threads[x].start()

def add_to_queue():
	global queue, usernames
	for x in xrange(START_QUEUE,END_QUEUE,1):
		username = usernames[x]
		queue.put(username)

def fetch_usernames():
	global usernames
	with open("./Extracts/2mil_ids1.json","r") as json_file:
		id_dict = json.load(json_file)	
	usernames = [val["username"] for val in id_dict.values()]

if __name__ == '__main__':
	fetch_usernames()
	add_to_queue()
	spawn_browser_instances()
	queue.join()

