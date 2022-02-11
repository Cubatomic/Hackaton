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
fms = []


def loaddata (fname):
    global folder, predictor
    im = cv2.imread (folder + fname)
    outputs = predictor (im)

    vals = np.zeros (20)
    for obj in outputs ["instances"].pred_masks:
        square = obj.sum ()
        if square >= 50:
            vals [min (square // 250, 19)] += 1

    fms.append (vals)


def fb (text):
    try:
        frameid = int (text)
        if frameid > 0 and frameid <= maximg:
            visualize (frameid)
    except:
        pass


def visualize (frameid):
    global x, ax
    ax.clear ()
    y = fms [frameid + 1]
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

    os.mkdir (folder)
    vfn = input ("Video file name: ")
    cap = cv2.VideoCapture (vfn)
    k = 1
    while True:
        ret, frame = cap.read ()
        if frame is None:
            break
        fname = "img" + str (k) + ".jpg"
        cv2.imwrite (folder + fname, frame)
        loaddata (fname)
        #print (k)
        k += 1
    maximg = k - 1

    fout = open ("gistogram.txt", 'w')
    fout.write ("Number of frames: " + maximg)
    for x in range (len (fms)):
        fout.write ("Frame: img" + str (x + 1) + ".jpg")
        for i in range (19):
            fout.write (str (fms [x] [i]) + ", ")
        fout.write ((fms [x] [19]) + '\n')

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
    text_box = TextBox (axbox, "Frame: ", initial = "1")
    text_box.on_submit (fb)
    
    visualize (1)


if __name__ == "__main__":
    main ()
