'''Utility functions for merging data if anything goes wrong
during aggregation.'''

import json, io

input_path = "./Extracts/UserFractals/"
output_path = "./Extracts/"


def write_to_file(output_file_name, output_path, all_data):
	with open(output_path + output_file_name, "w") as json_file:
		json.dump(all_data, json_file, sort_keys=True, indent=4,ensure_ascii=False)


def assimilate_files(numfiles,base_file_name, output_file_name,output_path,input_path):
	all_data = {}
	for x in range(1,numfiles+1):
		with open(input_path + base_file_name+ str(x) + ".json","r") as json_file:
			json_data = json.load(json_file)
			all_data.update(json_data)
		print x
	print "Number of Entries:", len(all_data)
	write_to_file(output_file_name, output_path,all_data)

def assimilate_file(path1,path2,file1,file2):
	
	with open(path1 + file1, "r") as json_file:
		file1_dict = json.load(json_file)
	with open(path2 + file2, "r") as json_file:
		file2_dict = json.load(json_file)

	file1_dict.update(file2_dict)
	print "Number of Entries:", len(file1_dict)
	write_to_file(file1,path1,file1_dict)


def diff_dict_check(**kwargs):
	result_dict = {}
	with open("./Extracts/" + kwargs["main_dict_name"],"r") as json_file:
		main_dict = json.load(json_file)
	
	with open("./Resources/" + kwargs["read_dict_name"], "r") as json_file:
		input_dict = json.load(json_file)

	key_diff = set(main_dict) ^ set(input_dict)

	if len(key_diff) != 0:
		for key in key_diff:
			result_dict[key] = main_dict[key]

	print "Found %d extra keys" % len(result_dict)
	#The result_dict contains all keys for which no username exists yet
	write_to_file("key_diff.json", "./Resources/", result_dict)


def assimilate_id_fractal():
	#Assimilate all IDFractals with a given filename
	assimilate_files(7,"collect_id","id_batch2.json", 
		"./Extracts/IDFractals/", "./Extracts/IDFractals/")

	assimilate_file("./Extracts/","./Resources/", "all_ids.json",
		"collect_ids.json")


def assimilate_user_fractal():
	#Assimilate all UserFractals with a given filename
	assimilate_files(65,"name","usernames.json","./Resources/",
		"./Extracts/UserFractals/")


def delete_keys_main_dict():
	with open("./Extracts/all_ids.json","r") as json_file:
		json_data = json.load(json_file)

	with open("./Resources/usernames.json","r") as json_file:
		usernames = json.load(json_file)

	for key in json_data.keys():
		if key not in usernames:
			del json_data[key]

	#now all_ids.json contains all ids for which there is a username
	#in usernames.json
	print "Number of Entries:", len(json_data)
	write_to_file("all_ids1.json","./Extracts/",json_data)



def create_id_batch():
	assimilate_id_fractal()
	with open("./Extracts/IDFractals/id_batch1.json","r") as json_file:
		json_data = json.load(json_file)

	result_dict = {}
	for key,val in json_data.items():
		result_dict[val["id"]] = {"name":key, "profile":val["profile"]}
	
	write_to_file("id_batch1.json","./Extracts/IDFractals/",result_dict)



def merge_usernames_main_dict():
	with open("./Extracts/all_ids.json","r") as json_file:
		json_data = json.load(json_file)

	with open("./Resources/usernames.json","r") as json_file:
		usernames = json.load(json_file)

	for key, val in json_data.items():

		val["username"] = usernames[key]
		json_data[key] = val

	print "Number of Entries:", len(json_data)
	write_to_file("all_ids1.json","./Extracts/",json_data)



if __name__ == '__main__':

	diff_dict = {
		"main_dict_name": "all_ids.json",
		"read_dict_name": "usernames.json"

	}
	diff_dict_check(**diff_dict)
	delete_keys_main_dict()
	assimilate_file("./Extracts/IDFractals/","./Extracts/IDFractals/",
		"id_batch1.json",
		"id_batch2.json")
	assimilate_id_fractal()
	merge_usernames_main_dict()
	assimilate_user_fractal()
