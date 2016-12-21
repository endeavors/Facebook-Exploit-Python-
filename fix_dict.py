import json, io, re

def fixids():
	with open("./Extracts/ids91.json","r") as file:
		file_str = file.read()

	all_ids = re.findall(r".*(10000000\d{7}).*",file_str)

	for idx, ids in enumerate(all_ids):
		parrallel_urls(int(ids), True if idx == len(all_ids)-1 else False)

def split_dict():
	with open("./Extracts/2mil_ids.json", "r") as file:
		big_json = json.load(file)

	print len(big_json)

	num_files = 4
	divisor = len(big_json)/num_files
	start = 0
	end = divisor
	for x in range(num_files):
		dict1 = dict(big_json.items()[start:end])
		with open("./Extracts/passchecker/2mil_ids%d.json"% (x+1), "w") as json_file:
			json.dump(dict1, json_file, sort_keys=True, indent=4,ensure_ascii=False)
		
		print len(dict1)
		start = end
		end = ((x+1) * divisor) + divisor


split_dict()