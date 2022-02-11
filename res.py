import os, cv2
import numpy as np
import detectron2
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from matplotlib import pyplot as plt
from matplotlib.widgets import TextBox

x = []
ax = None
predictor = None
maximg = 0
folder = "data/"


def loaddata (fname):
    global predictor, fms
    im = cv2.imread (fname)
    outputs = predictor (im)
    vals = np.zeros (20)
    for obj in outputs ["instances"].pred_masks:
        square = obj.sum ()
        if square >= 50:
            vals [min (square // 250, 19)] += 1
    return vals


def fb (text):
    try:
        fname = text
        if frameid > 0:
            visualize (fname)
    except:
        pass


def visualize (fname):
    global x, ax
    ax.clear ()
    y = loaddata (fname)
    ax.set_xticks (np.arange (20), labels = x)
    p = ax.bar (np.arange (20), y)
    ax.bar_label (p, label_type = "edge")
    plt.show ()


def main ():
    global folder, x, ax, predictor, maximg

    cfg = get_cfg ()
    cfg.merge_from_file (model_zoo.get_config_file ("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.TEST.DETECTIONS_PER_IMAGE = 1000
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
    cfg.MODEL.DEVICE = "cpu"
    cfg.MODEL.WEIGHTS = "model.pth"
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
    predictor = DefaultPredictor (cfg)

    try:
        os.mkdir (folder)
    except:
        pass

    fms = []
    cc = input ("Proceed single image (s) or video (v)?")
    if cc == 's':
        vfn = input ("Video file name: ")
        cap = cv2.VideoCapture (vfn)
        begin = int (input ("Begin from frame (indexation from 1): "))
        num = int (input ("Number of frames to proceed: "))
        end = begin + num
        k = 1
        while k < end:
            ret, frame = cap.read ()
            if frame is None:
                break
            if k < begin:
                continue
            fname = "img" + str (k) + ".jpg"
            cv2.imwrite (folder + fname, frame)
            fms.append (loaddata (folder + fname))
            #print (begin)
            k += 1
        maximg = num
            
    elif cc == 'v':
        sfn = input ("Image file name (path included): ")
        fms.append (loaddata (fname))
        maximg = 1

    
    fout = open ("gistogram.txt", 'w')
    fout.write ("Number of frames: " + str (maximg) + '\n')
    for q in range (len (fms)):
        fout.write ("Frame: img" + str (q + 1) + ".jpg, regions: ")
        for i in range (19):
            fout.write (str (int (fms [q] [i])) + ", ")
        fout.write (str (int (fms [q] [19])) + '\n')

    
    vsls = input ("Vilualize data on plot (y/n)?")
    if vsls == 'y':
        plt.rc ("xtick", labelsize = 5)
        fig, ax = plt.subplots ()
        ax.set_facecolor ("seashell")
        fig.set_facecolor ("floralwhite")
        fig.set_figwidth (14)
        fig.set_figheight (6)
        fig.canvas.set_window_title ("Test")
            
        x = ["(50; 250]"]
        for i in range (1, 20):
            x.append ("(" + str (i*250) + "; " + str (i*250 + 250) + "]")

        axbox = plt.axes ([0.4, 0.9, 0.2, 0.075])
        text_box = TextBox (axbox, "Image name: ", initial = "1")
        text_box.on_submit (fb)

        visualize (input ("Image file name (path included): "))


if __name__ == "__main__":
    main ()
