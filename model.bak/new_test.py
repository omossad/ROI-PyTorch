from __future__ import division

from new_model import *
from utils.new_utils import *
from utils.new_datasets import *
from utils.parse_config import *

import os
import sys
import time
import datetime
import argparse
import tqdm

import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision import transforms
from torch.autograd import Variable
import torch.optim as optim


#def evaluate(model, path, iou_thres, conf_thres, nms_thres, img_size, batch_size):
def evaluate(model, path, conf_thres, nms_thres, img_size, batch_size):
    model.eval()

    # Get dataloader
    dataset = ListDataset(path, img_size=img_size, augment=False, multiscale=False)
    dataloader = torch.utils.data.DataLoader(
        dataset, batch_size=batch_size, shuffle=False, num_workers=1, collate_fn=dataset.collate_fn
    )

    Tensor = torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor

    #labels = []
    temp_metrics = []  # List of tuples (TP, confs, pred)
    #sample_metrics = torch.zeros((1,3)).type(Tensor)
    #sample_metrics = torch.cuda.FloatTensor()
    for batch_i, (_, imgs, targets) in enumerate(tqdm.tqdm(dataloader, desc="Detecting objects")):

        # Extract labels
        #labels += targets[:, 1].tolist()
        # Rescale target
        #targets[:, 2:] = xywh2xyxy(targets[:, 2:])
        #targets[:, 2:] *= img_size

        imgs = Variable(imgs.type(Tensor), requires_grad=False)

        with torch.no_grad():
            outputs_x, outputs_y = model(imgs)
            #outputs = non_max_suppression(outputs, conf_thres=conf_thres, nms_thres=nms_thres)
        batch_statistics = get_batch_statistic(outputs_x, outputs_y, targets)
        #print('BATCH ' + str(batch_i) + ' results')
        ##print(temp_metrics)
        #print(batch_statistics)
        temp_metrics.append(batch_statistics)
        #sample_metrics += get_batch_statistic(outputs_x, outputs_y, targets)
        #sample_metrics = torch.stack((sample_metrics, batch_statistics.type(Tensor)))
    sample_metrics = torch.Tensor(len(temp_metrics), 1, 3)
    torch.cat(temp_metrics, out=sample_metrics)
    #print('OVERALL RESULTS')
    #print(sample_metrics)
    sample_metrics = torch.FloatTensor(sample_metrics.view(-1,3))
    # Concatenate sample statistics
    #tot_acc, x_acc, y_acc = [np.concatenate(x, 0) for x in list(zip(*sample_metrics))]
    #tot_acc, x_acc, y_acc = [torch.cat(x, 0) for x in list(zip(*sample_metrics))]
    tot_acc = sample_metrics[..., 0].mean()
    x_acc   = sample_metrics[..., 1].mean()
    y_acc   = sample_metrics[..., 2].mean()



    #tot_acc = x_acc = y_acc = 0
    #true_positives, pred_scores, pred_labels = [np.concatenate(x, 0) for x in list(zip(*sample_metrics))]
    #precision, recall, AP, f1, ap_class = ap_per_class(true_positives, pred_scores, pred_labels, labels)
    return tot_acc, x_acc, y_acc
    #return precision, recall, AP, f1, ap_class


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", type=int, default=8, help="size of each image batch")
    parser.add_argument("--model_def", type=str, default="config/yolov3.cfg", help="path to model definition file")
    parser.add_argument("--data_config", type=str, default="config/coco.data", help="path to data config file")
    parser.add_argument("--weights_path", type=str, default="weights/yolov3.weights", help="path to weights file")
    parser.add_argument("--class_path", type=str, default="data/coco.names", help="path to class label file")
    parser.add_argument("--iou_thres", type=float, default=0.5, help="iou threshold required to qualify as detected")
    parser.add_argument("--conf_thres", type=float, default=0.3, help="object confidence threshold")
    parser.add_argument("--nms_thres", type=float, default=0.2, help="iou thresshold for non-maximum suppression")
    parser.add_argument("--n_cpu", type=int, default=8, help="number of cpu threads to use during batch generation")
    parser.add_argument("--img_size", type=int, default=416, help="size of each image dimension")
    opt = parser.parse_args()
    print(opt)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    data_config = parse_data_config(opt.data_config)
    valid_path = data_config["valid"]
    class_names = load_classes(data_config["names"])

    # Initiate model
    model = Darknet(opt.model_def).to(device)
    if opt.weights_path.endswith(".weights"):
        # Load darknet weights
        model.load_darknet_weights(opt.weights_path)
    else:
        # Load checkpoint weights
        model.load_state_dict(torch.load(opt.weights_path))

    print("Computing Model Accuracy...")

    #precision, recall, AP, f1, ap_class = evaluate(
    #    model,
    #    path=valid_path,
    #    iou_thres=opt.iou_thres,
    #    conf_thres=opt.conf_thres,
    #    nms_thres=opt.nms_thres,
    #    img_size=opt.img_size,
    #    batch_size=8,
    #)

    tot_acc, x_acc, y_acc = evaluate(
        model,
        path=valid_path,
        conf_thres=0.3,
        nms_thres=0.2,
        img_size=opt.img_size,
        batch_size=32,
    )
    print('accuracies: ' + str(x_acc) + ', ' + str(y_acc) + ', ' + str(tot_acc))
    #print("Average Precisions:")
    #for i, c in enumerate(ap_class):
    #    print(f"+ Class '{c}' ({class_names[c]}) - AP: {AP[i]}")
    #
    #print(f"mAP: {AP.mean()}")
