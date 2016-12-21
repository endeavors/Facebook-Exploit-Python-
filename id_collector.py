from urllib2 import URLError
from Queue import Queue
import requests, urllib2, json, io,sys, threading, time, math, socket, ssl

ssl._create_default_https_context = ssl._create_unverified_context

fb_access_token = ""

save_loc = "./Extracts/IDFractals/"
male_def_img = "https://scontent-cdg2-1.xx.fbcdn.net/v/t1.0-1/c47.0.160.160/p160x160/1379841_10150004552801901_469209496895221757_n.jpg?oh=419a15de3c545762aa55a28cf672d104&oe=57A2D356"
female_def_img = "https://scontent-cdg2-1.xx.fbcdn.net/v/t1.0-1/c47.0.160.160/p160x160/10354686_10150004552801856_220367501106153455_n.jpg?oh=b5df82644cdd221e1da17017092c51f5&oe=57E04C49"
base_url_prefix = "https://graph.facebook.com/"
base_url_suffix = "?fields=name,picture.height(100).width(100){url}&access_token=" + fb_access_token
error_codes = [4,17,10,341,100]

#precautionary measures if thread dies or data gets corrupt
num_threads = 180 
offset = 0 
run = 1
counter = 0 
goal = 2000000
base_fbid = 100000000000000  #inclusive

headers = {'User-agent': 'Mozilla/5.0'}
id_dict = {}
lock = threading.Lock()
queue = Queue(maxsize=0)

class ThreadWorker(threading.Thread):
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while self.queue.qsize() != 0:
            fbid = self.queue.get(timeout=10)
            parrallel_url(fbid)
            self.queue.task_done()

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def write_to_file():
    print "Writing to file"
    lock.acquire()
    with open(save_loc + "collect_id" + str(run) + ".json", "w") as outfile:
        json.dump(id_dict, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    lock.release()

def parrallel_url(fbid):
    global id_dict, counter
    
    request = urllib2.Request(base_url_prefix + str(fbid) + base_url_suffix, None, headers)

    try:
        response = urllib2.urlopen(request)
        if response.code == 200:
            html = response.read()
            json_data = json.loads(html)
            
            if "error" in json_data:
                error_code = json_data["error"]["code"]
                print "ERROR IN GRAPH API", error_code
                if error_code in error_codes:
                    raise KeyboardInterrupt()

            results = {}
            name = json_data["name"]
            
            if (name == None) or (not all(ord(c) < 128 for c in name)):
                return

            profile_pic_link = json_data["picture"]["data"]["url"]

            if profile_pic_link == male_def_img or profile_pic_link == female_def_img:
                return

            results["name"] = name
            results["profile"] = profile_pic_link
            id_dict[fbid] = results
            
            counter += 1
            print fbid - base_fbid
            if counter % 1000 == 0:
                write_to_file()

    except URLError,e:
        if hasattr(e, 'code'): 
            if e.code != 404 and e.code != 400:
                print "ID: ", fbid, "CODE: ", e.code, "COUNTER: ", counter
                write_to_file()
        elif hasattr(e, 'reason'):
            print "ID: ", fbid, "Reason: ", e.reason, "COUNTER: ", counter
    
    except KeyboardInterrupt:
        print "KEYBOARD_INTERRUPT at ID: ", fbid, "COUNTER: ", counter
        write_to_file()
        sys.exit()
    except Exception, e:
        write_to_file()
        print "EXCEPTION", str(e)
        sys.exit()
    

def spawn():
    for x in xrange(num_threads): 
        thread = ThreadWorker(queue)
        thread.daemon = True
        thread.start()

def add_val_to_queue():
    global queue

    count = offset
    while count < goal:
        queue.put(base_fbid + count)
        count += 1

if __name__ == "__main__":
    print "Real IP", get_ip_address()
    add_val_to_queue()
    spawn()
    queue.join()
    write_to_file()


