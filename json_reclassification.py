"""
The purpose of this code is to create a custom gallery_class.json file
that contains each possible object available in the ImageNet-1000 json
file (imagenet_class_index.json) . In the gallery_class.json, each
 object name is a json property with a temporary value "objects".
 Once the json file is created, we will manually change the "objects"
 value of each of the json properties to its corresponding category name as seen
 in the "custom class.txt" file.

"""

import json
import os

execution_path = os.getcwd()

object_dictionary = {}

with open(execution_path + "\\imagenet_class_index.json") as inputFile:
    json_data = json.load(inputFile)
    for aa in range(1000):
        eachItem = json_data[str(aa)][1]
        object_dictionary[eachItem] = "category"

with open(execution_path + "\\gallery_class.json", "w+") as outfile:
   json.dump(object_dictionary, outfile, indent=4, sort_keys=True, separators=(",", " : "), ensure_ascii=True)
   outfile.close()



