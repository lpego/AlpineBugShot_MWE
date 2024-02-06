# import cv2
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
from pathlib import Path
import ast

workdir = Path().absolute()
frames = workdir.parents[0] / "data" / "frames"

# ### proof of concept
# img = Image.open(Path(frames / "PICT2_86A5_2022-07-13_11-22_001.h264_frame3696.jpg"))
# plt.imshow(img)
# plt.gca().add_patch(Rectangle((350,250),35,25,linewidth=1,edgecolor='r',facecolor='none'))

### keep only rows with events
anns = pd.read_csv(Path(workdir.parents[0] / "anns_parsed.csv"))
anns = anns[anns['BB_list'].notna()]
anns.to_csv(Path(workdir.parents[0] / 'anns_parsed_onlypos.csv'), sep=',',encoding='utf-8', index=True)

### plot BBs on top of images
for i in range(0, len(anns)): 
    print("Now plotting image:", anns.iloc[i, 5])
    img = Image.open(Path(frames / anns.iloc[i, 5]))
    plt.imshow(img)
    for sublist in eval(anns.iloc[i,6]): 
        # print(sublist)
        x1 = sublist[0]
        y1 = sublist[1]
        x2 = sublist[2]
        y2 = sublist[3]
        width = x2 - x1
        height = y2 - y1
        print(x1, y1, width, height)
        plt.gca().add_patch(Rectangle((x1, y1), width, height,
                                      linewidth=1,edgecolor='r',facecolor='none'))
    plt.show()
