import numpy as np
from random import randint
from random import seed
seed(1)
##### CONVERT LABEL DATA TO ROI DATA FOR EVALUATION ######

W_ref = 1920.0
H_ref = 1080.0
W_tiles = 8.0
H_tiles  = 8.0
tile_width = W_ref / W_tiles
tile_height = H_ref / H_tiles
num_tiles = int(W_tiles * H_tiles)


def get_tile(x,y):
    x = x*W_ref
    y = y*H_ref
    x_cor = np.minimum(x, W_ref-1)
    y_cor = np.minimum(y, H_ref-1)
    x_dis = int(x_cor / tile_width)
    y_dis = int(y_cor / tile_height)
    tile = int(x_dis + y_dis * W_tiles)
    return tile

def get_tile_xywh(tile_no):
    tile_y = np.floor(tile_no / W_tiles)
    tile_x = tile_no % W_tiles
    x_min = tile_x * tile_width/W_ref
    x_max = (tile_x + 1) * tile_width/W_ref
    y_min = tile_y * tile_height/H_ref        
    y_max = (tile_y + 1) * tile_height/H_ref
    x = (x_min + x_max)/2
    y = (y_min + y_max)/2
    w = 1/W_tiles
    h = 1/H_tiles
    return [x,y,w,h]


base_dir = '/home/omossad/scratch/temp/labels/'
labels = np.loadtxt(base_dir + 'labels_0.txt')
start_frame = 100
end_frame = 310

def rand_bin_array(P, K, N):
    arr = np.zeros(N)
    arr[:K]  = 1
    arr[:P]  = 0.5
    np.random.shuffle(arr)
    return arr

def process_100(save_dir, ):
    frame_cnt = 0
    for lbl in labels:
        if frame_cnt >= start_frame and frame_cnt < end_frame:
                s_tile = get_tile(lbl[0],lbl[1])
                [x,y,w,h] = get_tile_xywh(s_tile)
                f = open(base_dir + save_dir + 'rois/roi' + str(frame_cnt-start_frame) + '.txt', "w")
                f.write('0 '+ str(x) + ' ' + str(y) + ' ' + str(w) + ' ' + str(h)) 
                f.close()
        frame_cnt = frame_cnt + 1

def get_tile_surroundings(s_tile):
    l_tile = max(0, s_tile - 1)
    r_tile = min(63,s_tile + 1)
    u_tile = min(0, s_tile - 8)
    d_tile = max(63,s_tile + 8)
    return[l_tile, r_tile, u_tile, d_tile]
    
def process_65(save_dir, prox_dir, ):
    frame_cnt = 0
    randomize = rand_bin_array(53,136,210)
    for lbl in labels:
        if frame_cnt >= start_frame and frame_cnt < end_frame:
            low_q_tiles = []
            s_tile = get_tile(lbl[0],lbl[1])
            if randomize[frame_cnt-start_frame] == 0:
                s_tile = randint(0, 63)
            elif randomize[frame_cnt-start_frame] == 0.5:
                low_q_tiles = get_tile_surroundings(s_tile)
                s_tile = s_tile - 1
                if s_tile < 0:
                    s_tile = s_tile + 2
                
                #print(lbl)
            [x,y,w,h] = get_tile_xywh(s_tile)
            f = open(base_dir + save_dir + 'rois/roi' + str(frame_cnt-start_frame) + '.txt', "w")
            f.write('0 '+ str(x) + ' ' + str(y) + ' ' + str(w) + ' ' + str(h)) 
            f.close()
            f = open(base_dir + prox_dir + 'rois/roi' + str(frame_cnt-start_frame) + '.txt', "w")
            f.write('0 '+ str(x) + ' ' + str(y) + ' ' + str(w) + ' ' + str(h)) 
            counter = 0
            for prox_tile in low_q_tiles:
                [x,y,w,h] = get_tile_xywh(prox_tile)
                if counter < 3:
                    f.write('1 '+ str(x) + ' ' + str(y) + ' ' + str(w) + ' ' + str(h) + '\n') 
                else:
                    f.write('1 '+ str(x) + ' ' + str(y) + ' ' + str(w) + ' ' + str(h))
                counter = counter + 1 
            f.close()
            
            
        frame_cnt = frame_cnt + 1
    
process_100('100_')
process_65('65_', '65p_')
