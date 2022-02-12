import os, cv2
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
import json

x = []
ax = None
predictor = None
maximg = 0
folder = "data/"


def get_porridge_dicts(img_dir):
    json_file = os.path.join(img_dir, "1.json")
    with open(json_file) as f:
        imgs_anns = json.load(f)

    dataset_dicts = []
    for idx, v in enumerate(imgs_anns.values()):
        record = {}

        filename = os.path.join(img_dir, v["filename"])
        height, width = cv2.imread(filename).shape[:2]

        record["file_name"] = filename
        record["image_id"] = idx
        record["height"] = height
        record["width"] = width

        annos = v["regions"]
        objs = []
        for _, anno in annos.items():
            # let it be
            assert not anno["region_attributes"]
            anno = anno["shape_attributes"]
            px = anno["all_points_x"]
            py = anno["all_points_y"]
            poly = [(x + 0.5, y + 0.5) for x, y in zip(px, py)]
            poly = [p for x in poly for p in x]

            obj = {
                "bbox": [np.min(px), np.min(py), np.max(px), np.max(py)],
                "bbox_mode": BoxMode.XYXY_ABS,
                "segmentation": [poly],
                "category_id": 0,
            }
            objs.append(obj)
        record["annotations"] = objs
        dataset_dicts.append(record)
    return dataset_dicts


def loaddata(fname):
    print(fname)
    global predictor, fms
    im = cv2.imread(fname)

    outputs = predictor(im)
    vals = np.zeros(20)
    for obj in outputs["instances"].pred_masks:
        square = obj.sum()
        if square >= 50:
            vals[min(square // 250, 19)] += 1
    return vals


def fb(text):
    try:
        fname = text
        if frameid > 0:
            visualize(fname)
    except:
        pass


def visualize(fname):
    global x, ax
    ax.clear()
    y = loaddata(fname)
    ax.set_xticks(np.arange(20), labels=x)
    p = ax.bar(np.arange(20), y)
    ax.bar_label(p, label_type="edge")
    plt.show()


def main():
    global folder, x, ax, predictor, maximg

    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.TEST.DETECTIONS_PER_IMAGE = 1000
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
    cfg.MODEL.DEVICE = "cpu"
    cfg.MODEL.WEIGHTS = "model.pth"
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
    predictor = DefaultPredictor(cfg)

    try:
        os.mkdir(folder)
    except:
        pass

    fms = []
    cc = input("Proceed single image (s) or video (v)?")
    if cc == 'v':
        vfn = input("Video file name: ")
        cap = cv2.VideoCapture(vfn)
        begin = int(input("Begin from frame (indexation from 1): "))
        num = int(input("Number of frames to proceed: "))
        end = begin + num
        k = 1
        while k < end:
            ret, frame = cap.read()
            if frame is None:
                break
            if k < begin:
                continue
            fname = "img" + str(k) + ".jpg"
            cv2.imwrite(folder + fname, frame)
            fms.append(loaddata(folder + fname))
            # print (begin)
            k += 1
        maximg = num

    elif cc == 's':
        sfn = input("Image file name: ")
        # fname = "img" + str(sfn) + ".jpg"
        fms.append(loaddata(sfn))
        maximg = 1

    fout = open("gistogram.txt", 'w')
    fout.write("Number of frames: " + str(maximg) + '\n')
    for q in range(len(fms)):
        fout.write("Frame: img" + str(q + 1) + ".jpg, regions: ")
        for i in range(19):
            fout.write(str(int(fms[q][i])) + ", ")
        fout.write(str(int(fms[q][19])) + '\n')

    vsls = input("Vilualize data on plot (y/n)?")

    if vsls == 'y':
        plt.rc("xtick", labelsize=5)
        fig, ax = plt.subplots()
        ax.set_facecolor("seashell")
        fig.set_facecolor("floralwhite")
        fig.set_figwidth(14)
        fig.set_figheight(6)
        fig.canvas.set_window_title("Test")

        x = ["(50; 250]"]
        for i in range(1, 20):
            x.append("(" + str(i * 250) + "; " + str(i * 250 + 250) + "]")

        axbox = plt.axes([0.4, 0.9, 0.2, 0.075])
        text_box = TextBox(axbox, "Image name: ", initial="1")
        text_box.on_submit(fb)

        visualize(input("Image file name (path included): "))

    vim = input("Show marked images (y/n)?")
    if vim == 'y':
        for d in ["val"]:
            DatasetCatalog.register("porridge_" + d, lambda d=d: get_porridge_dicts("porridge/" + d))
            MetadataCatalog.get("porridge_" + d).set(thing_classes=["porridge"])

        porridge_metadata = MetadataCatalog.get("porridge_train")
        kk = 1
        while True:
            ifn = input("Image file name (path included, enter 0 to leave): ")
            if ifn == "0":
                break
            im = cv2.imread(ifn)
            outputs = predictor(im)
            v = Visualizer(im[:, :, ::-1], metadata=porridge_metadata, scale=1.0)
            out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
            print(out.get_image()[:, :, ::-1])
            cv2.imshow('Image', out.get_image()[:, :, ::-1])
            print("Saved to: " + folder + "marked_" + ifn)
            cv2.imwrite(folder + "marked_" + ifn, out.get_image()[:, :, ::-1])
            kk += 1


if __name__ == "__main__":
    main()
