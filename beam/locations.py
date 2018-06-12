import json
from beam import https
from django.conf import settings
def load_data():		
	locations=[]
	location_pune={}
	location_pune['location_name']= "pune"
	location_pune['location_id']= "0"
	location_pune['url']= "www.mojopune.com"

	location_mumbai={}
	location_mumbai['location_name']= "mumbai"
	location_mumbai['location_id']= "0"
	location_mumbai['url']= "www.mojomumbai.com"


	locations.append(location_pune)
	locations.append(location_mumbai)
	return locations

def load_tree_data():		
	print " load tree data"
	service = https.getServices()
	split = service.split("?CID=")	
	mwm_url = split[0]
	tree_root=[]
	root={}
	tree_root.append(root)
	locations = https.fetch_location_tree(split[0])
	if locations is not None:		
		d = {}
		for l in locations:			
			location_parent_id = locations[l]["parentId"]
			location_type = locations[l]["type"]
			#print location_type , location_parent_id
			if location_type =="folderlocation":
				if location_parent_id is None:
					root['text'] = locations[l]["name"]
				#print locations[l]["name"]
					root['location_id']= locations[l]["id"]["id"]
					root['url']= mwm_url
					childrens = locations[l]["children"]
					if childrens is not None:
						nodes = get_child_nodes(locations, childrens, mwm_url)
						root["nodes"]= nodes								
		return tree_root
	else:
		print "location not found"		
	return tree_root

def get_child_nodes(locations, childrens, mwm_url):
	nodes = []
	if childrens is not None:
		for child in childrens:									
			if child["id"] != -1:
				node = get_tree_node(locations, child)					
				location_type = node["type"]			
				if location_type =="folderlocation":
					if node is not None:
						child_loc={}
						child_loc['text']=node["name"]
						child_loc['location_id']= node["id"]["id"]
						child_loc['url']= mwm_url
						if "children" in node:
							child_nodes = get_child_nodes(locations, node["children"], mwm_url)
							if child_nodes is not None:
								child_loc["nodes"] = child_nodes
								nodes.append(child_loc)
	return nodes


def get_tree_node(parent, child_node):		
	for location_key in parent:		
		#print location_key
		json_location_key = json.loads(location_key)
		type_value = json_location_key["type"]
		id_value = json_location_key["id"]
		if type_value ==child_node["type"]:
			if id_value==child_node["id"]:
				node = parent[location_key]
				#print node
				return node	
	return None
