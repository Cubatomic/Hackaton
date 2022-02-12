import os, cv2, json, shutil
import numpy as np
import detectron2
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.structures import BoxMode
from matplotlib import pyplot as plt
from matplotlib.widgets import TextBox

x = []
ax = None
predictor = None
folder = "data/"
porridge_metadata = MetadataCatalog.get ("porridge_train")
OUT_FOLDER = "out/"



def loaddata (fname):
    global predictor, fms
    im = cv2.imread (fname)

    outputs = predictor (im)
    vals = np.zeros (20)
    for obj in outputs ["instances"].pred_masks:
        square = obj.sum ()
        if square >= 50:
            vals [min (square // 250, 19)] += 1
    return vals, outputs


def fb(text):
    try:
        fname = text
        if frameid > 0:
            visualize (fname)
    except:
        pass


def visualize (fname):
    global x, ax
    ax.clear ()
    y = loaddata (fname) [0]
    ax.set_xticks (np.arange (20), labels=x)
    p = ax.bar (np.arange (20), y)
    ax.bar_label (p, label_type="edge")
    plt.show ()


def saveimage (image_name, frame, outputs):

    v = Visualizer (frame[:, :, ::-1], metadata = porridge_metadata, scale=1.0)
    masks = outputs ["instances"].get ("pred_masks")
    masks = masks.to ("cpu")
    for m in masks:
        v.draw_binary_mask (np.array(m), color = "c")
    out = v.get_output ()

    proc_img = out.get_image () [:, :, ::-1]
    cv2.imwrite (image_name, proc_img)
    return proc_img


def ProceedVideo (videoname):
    cap = cv2.VideoCapture (videoname)
    begin = int (input ("Begin from frame (indexation from 1): "))
    num = int (input ("Number of frames to proceed: "))
    end = begin + num
    k = 1

    out = None
    while k < begin:
        ret, frame = cap.read ()
        if frame is None:
            break
        k += 1
    AllData = []
    size = (0, 0) # just init
    while k < end:
        ret, frame = cap.read ()
        if frame is None:
            break


        fname = "img" + str (k) + ".jpg"
        cv2.imwrite (folder + fname, frame)
        data, outputs = loaddata (folder + fname)
        AllData.append (data)

        image_file = OUT_FOLDER + "img{}.jpg".format (k)
        proc_video = saveimage (image_file, frame, outputs)



        height, width, layers = frame.shape
        size = (width, height)
        if not out:
            out = cv2.VideoWriter ('project.mp4', cv2.VideoWriter_fourcc (*'DIVX'), 24, size)
        out.write(proc_video)

        k += 1
    out.release()

    SaveGistogram (begin, num, AllData)


def SaveGistogram (begin, num, fms):
    fout = open ("gistogram.txt", 'w')
    fout.write ("Number of frames: " + str (num) + '\n')
    for k in range (num):
        fout.write ("Frame: img" + str (begin + k) + ".jpg, regions: ")
        for i in range (19):
            fout.write (str (int (fms [k] [i])) + ", ")
        fout.write (str (int (fms [k] [19])) + '\n')


def ShowMarked ():
    while True:
        ifn = input ("Frame number (enter 0 to leave): ")
        if ifn == "0":
            break
        img = cv2.imread (OUT_FOLDER + "img{}.jpg".format (ifn))
        cv2.imshow ("Image", img)


def main ():
    global folder, x, ax, predictor

    cfg = get_cfg ()
    cfg.merge_from_file (model_zoo.get_config_file ("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.TEST.DETECTIONS_PER_IMAGE = 1000
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
    cfg.MODEL.DEVICE = "cpu"
    cfg.MODEL.WEIGHTS = "model.pth"
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
    predictor = DefaultPredictor (cfg)

    try:
        shutil.rmtree (OUT_FOLDER)
    except:
        pass
    try:
        shutil.rmtree(folder)
    except:
        pass
    try:
        os.mkdir(OUT_FOLDER)
    except:
        pass
    try:
        os.mkdir(folder)
    except:
        pass


    cc = input ("Proceed single image (s) or video (v)?")
    if cc == 'v':
        vfn = input ("Video file name: ")
        ProceedVideo (vfn)

    elif cc == 's':
        sfn = input ("Image file name: ")
        im = cv2.imread (sfn)
        data, out = loaddata (sfn)
        saveimage (OUT_FOLDER + "img1.jpg", im, out)
        

    vsls = input("Vilualize data on plot (y/n)?")

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
            x.append ("(" + str (i * 250) + "; " + str (i * 250 + 250) + "]")

        axbox = plt.axes ([0.4, 0.9, 0.2, 0.075])
        text_box = TextBox (axbox, "Image name: ", initial = "1")
        text_box.on_submit (fb)

        visualize (input ("Image file name (path included): "))

    vim = input ("Show marked images (y/n)?")
    if vim == 'y':
        ShowMarked ()


if __name__ == "__main__":
    main()
