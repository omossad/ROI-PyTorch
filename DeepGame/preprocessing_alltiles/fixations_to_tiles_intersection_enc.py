

from __future__ import print_function
import numpy as np
import csv
import pickle
import math
import os
import torch
from shapely.geometry import Polygon
import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))
import utils
import re
########################################
### THIS FILE GENERATE FIXATIONS     ###
### FOR TS FRAMES AS DICTIONARY      ###
########################################
## VARIABLES ###
# input folder is where the selected data is located #
game = 'nhl'
input_folder = 'D:\\Encoding\\encoding_files\\nhl\\model\\filenames\\'
output_folder = 'D:\\Encoding\\encoding_files\\nhl\\model\\tiled_labels\\'


[W,H] = [2560,1440]
[W,H] = [1920,1080]

num_tiles = 8
[ts, t_overlap, fut] = utils.get_model_conf()
radius = utils.get_visual_pixels()*1.3
intersection_threshold = utils.get_intersection_threshold()


print('Processing nhl :')
input_path = input_folder
path, dirs, files = next(os.walk(input_path))
output_path = output_folder
#try:
#	os.mkdir(output_path)
#except:
#	print('directories already exist')
files.sort(key=lambda var:[int(x) if x.isdigit() else x for x in re.findall(r'[^0-9]|[0-9]+', var)])
file_count = len(files)
#targets = np.zeros((file_count, fut, 2, num_tiles))
targets = torch.zeros([file_count, fut, 2, num_tiles], dtype=torch.int32)
invalid = 1
#targets_y = np.zeros((file_count, num_tiles))
for fidx in range(file_count):
	#print('Processing : ' + files[fidx])
	f = open(input_path + files[fidx], "r")
	#tiles_array_x = np.zeros((num_tiles))
	#tiles_array_y = np.zeros((num_tiles))
	for s in range(ts):
		f.readline()
	for l in range(fut):
		fixations = f.readline()
		#fixations = line.split(',')[1]
		fixations = fixations.replace('[','')
		fixations = fixations.replace(']','')
		x = float(fixations.split()[0])
		y = float(fixations.split()[1])
		#print(x)
		#print(y)
		#x1 = x*W - W/(num_tiles*2)
		#x2 = x*W + W/(num_tiles*2)
		#y1 = y*H - H/(num_tiles*2)
		#y2 = y*H + H/(num_tiles*2)
		x1 = x*W - radius
		x2 = x*W + radius
		y1 = y*H - radius
		y2 = y*H + radius
		#print('tile coor : ' + str(x1) + ' ' + str(x2) + ' ' + str(y1) + ' ' + str(y2))
		[arr_x, arr_y] = utils.object_to_tile_intersection(x1,y1,x2,y2)
		#print(arr_x)
		#print(arr_y)
		#print(arr)
		for k in range(len(arr_x)):
			if arr_x[k] > intersection_threshold:
				#print(k)
				#tiles_array_x[X] = 1
				#tiles_array_y[Y] = 1
				targets[fidx][l][0][k] = 1
			if arr_y[k] > intersection_threshold:
				#print(k)
				targets[fidx][l][1][k] = 1
	if sum(targets[fidx][l][0]) > 0:
		previous_arr_x = targets[fidx][l][0]
	else:
		targets[fidx][l][0] = previous_arr_x
	if sum(arr_y) > 0:
		previous_arr_y = targets[fidx][l][1]
		invalid = 0
	else:
		if invalid > 0:
			print(fidx)
			targets[fidx][l][1] = previous_arr_x
		else:
			targets[fidx][l][1] = previous_arr_y
	#targets[fidx] = tiles_array_x
	#targets_y[fidx] = tiles_array_y
torch.save(targets, output_folder + 'nhl.pt')