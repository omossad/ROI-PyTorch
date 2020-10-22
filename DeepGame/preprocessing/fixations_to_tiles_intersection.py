

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

########################################
### THIS FILE GENERATE FIXATIONS     ###
### FOR TS FRAMES AS DICTIONARY      ###
########################################
## VARIABLES ###
# input folder is where the selected data is located #
input_folder = 'C:\\Users\\omossad\\Desktop\\dataset\\model_data\\filenames\\'
output_folder =  'C:\\Users\\omossad\\Desktop\\dataset\\model_data\\tiled_labels\\'

[W,H] = utils.get_img_dim()
num_tiles = utils.get_num_tiles()
[ts, t_overlap, fut] = utils.get_model_conf()
radius = utils.get_visual_pixels()

### READ NUMBER OF FILES and NAMES ###
num_files = utils.get_no_files()
file_names = utils.get_files_list(num_files)


for i in range(num_files):
	input_path = input_folder + file_names[i] + '\\'
	path, dirs, files = next(os.walk(input_path))
	output_path = output_folder + file_names[i] + '\\'
	#try:
	#	os.mkdir(output_path)
	#except:
	#	print('directories already exist')
	file_count = len(files)
	#targets_x = np.zeros((file_count, fut, 2, num_tiles))
	targets_x = torch.zeros([file_count, fut, 2, num_tiles], dtype=torch.int32)

	#targets_y = np.zeros((file_count, num_tiles))
	for fidx in range(file_count):
		f = open(input_path + files[fidx], "r")
		tiles_array_x = np.zeros((num_tiles))
		tiles_array_y = np.zeros((num_tiles))
		for s in range(ts):
			f.readline()
		for l in range(fut):
			fixations = f.readline()
			#fixations = line.split(',')[1]
			fixations = fixations.replace('[','')
			fixations = fixations.replace(']','')
			x = float(fixations.split()[0])
			y = float(fixations.split()[1])
			#x1 = x*W - W/(num_tiles*2)
			#x2 = x*W + W/(num_tiles*2)
			#y1 = y*H - H/(num_tiles*2)
			#y2 = y*H + H/(num_tiles*2)
			x1 = x*W - radius
			x2 = x*W + radius
			y1 = y*H - radius
			y2 = y*H + radius
			#print('tile coor : ' + str(x1) + ' ' + str(x2) + ' ' + str(y1) + ' ' + str(y2))
			arr = utils.object_to_tile_intersection(x1,y1,x2,y2)
			for k in range(len(arr[0])):
				if arr[0][k] > 0.01:
			#tiles_array_x[X] = 1
			#tiles_array_y[Y] = 1
					targets_x[fidx][l][0][k] = 1
					targets_x[fidx][l][1][k] = 1
		#targets_x[fidx] = tiles_array_x
		#targets_y[fidx] = tiles_array_y
	torch.save(targets_x, output_folder + file_names[i] + '.pt')
	#np.savetxt(output_folder + file_names[i] + '_x.txt', targets_x)
	#np.savetxt(output_folder + file_names[i] + '_y.txt', targets_y)

			#f.readline()
			#print(f.readline().split())