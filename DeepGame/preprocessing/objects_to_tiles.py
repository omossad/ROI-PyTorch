

from __future__ import print_function
import numpy as np
import csv
import pickle
import math
import os
from shapely.geometry import Polygon
import torch
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
objects_folder = 'C:\\Users\\omossad\\Desktop\\dataset\\model_data\\objects\\'
output_folder =  'C:\\Users\\omossad\\Desktop\\dataset\\model_data\\tiled_objects\\'

[W,H] = utils.get_img_dim()
num_tiles = utils.get_num_tiles()
[ts, t_overlap, fut] = utils.get_model_conf()

### READ NUMBER OF FILES and NAMES ###
num_files = utils.get_no_files()
file_names = utils.get_files_list(num_files)


for i in range(num_files):
	print(file_names[i])
	input_path = input_folder + file_names[i] + '\\'
	path, dirs, files = next(os.walk(input_path))
	output_path = output_folder + file_names[i] + '\\'
	#try:
	#	os.mkdir(output_path)
	#except:
	#	print('directories already exist')
	file_count = len(files)
	objects_arr_x = torch.zeros([file_count, ts, 2, num_tiles, 3], dtype=torch.int32)
	#objects_arr_y = torch.zeros([file_count, ts, 2, num_tiles, 3], dtype=torch.int32)
	for fidx in range(file_count):
		f = open(input_path + files[fidx], "r")
		for l in range(ts):
			frame_name = f.readline()
			frame_name = frame_name.replace('\n','')
			#frame_name = line.split(',')[0]
			temp = torch.load(objects_folder + file_names[i] + '\\' + frame_name + '.pt')
			for obj in range(len(temp)):
				x1 = temp[obj][0]/W
				y1 = temp[obj][1]/H
				x2 = temp[obj][2]/W
				y2 = temp[obj][3]/H
				[X,Y] = utils.fixation_to_tile((x1+x2)/2.0,(y1+y2)/2.0)
				objects_arr_x[fidx][l][0][X][int(temp[obj][6])] += 1
				objects_arr_x[fidx][l][1][Y][int(temp[obj][6])] += 1
	torch.save(objects_arr_x, output_folder + file_names[i] + '.pt')
				#objects_arr_x[fidx][l][X][int(temp[obj][6])] += 1
				#objects_arr_y[fidx][l][Y][int(temp[obj][6])] += 1
	#torch.save(objects_arr_x, output_folder + file_names[i] + '_x.pt')
	#torch.save(objects_arr_y, output_folder + file_names[i] + '_y.pt')
	#print(objects_arr_x)