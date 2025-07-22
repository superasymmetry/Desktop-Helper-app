import sys
import os
import urllib.request
from PIL import Image
# os.environ["USE_FLASH_ATTENTION"] = "0"
# === Path setup ===
omni_parser_path = r"C:\Users\yroeh\OneDrive\Documents\GitHub\OmniParser"
sys.path.append(r"C:\Users\yroeh\OneDrive\Documents\GitHub\OmniParser")

from util.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
import torch
from ultralytics import YOLO
from PIL import Image
device = 'cuda'
model_path = r"C:\Users\yroeh\OneDrive\Documents\GitHub\OmniParser\weights\icon_detect\model.pt"

som_model = get_yolo_model(model_path)

som_model.to(device)
print('model to {}'.format(device))


# two choices for caption model: fine-tuned blip2 or florence2
import importlib
# import util.utils
# importlib.reload(utils)
from util.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
caption_model_processor = get_caption_model_processor(model_name="florence2", model_name_or_path=r"C:\Users\yroeh\OneDrive\Documents\GitHub\OmniParser\weights\icon_caption_florence", device=device)
print("This step completed")

som_model.device, type(som_model)
print("That step completed")

# reload utils
import importlib
import utils
importlib.reload(utils)
# from utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model

image_path = r"C:\Users\yroeh\OneDrive\Pictures\Camera Roll\screenshot.png"


image = Image.open(image_path)
image_rgb = image.convert('RGB')
print('image size:', image.size)

box_overlay_ratio = max(image.size) / 3200
draw_bbox_config = {
    'text_scale': 0.8 * box_overlay_ratio,
    'text_thickness': max(int(2 * box_overlay_ratio), 1),
    'text_padding': max(int(3 * box_overlay_ratio), 1),
    'thickness': max(int(3 * box_overlay_ratio), 1),
}
BOX_TRESHOLD = 0.05

import time
start = time.time()
ocr_bbox_rslt, is_goal_filtered = check_ocr_box(image_path, display_img = False, output_bb_format='xyxy', goal_filtering=None, easyocr_args={'paragraph': False, 'text_threshold':0.9}, use_paddleocr=True)
text, ocr_bbox = ocr_bbox_rslt
cur_time_ocr = time.time() 

dino_labled_img, label_coordinates, parsed_content_list = get_som_labeled_img(image_path, som_model, BOX_TRESHOLD = BOX_TRESHOLD, output_coord_in_ratio=True, ocr_bbox=ocr_bbox,draw_bbox_config=draw_bbox_config, caption_model_processor=caption_model_processor, ocr_text=text,use_local_semantics=True, iou_threshold=0.7, scale_img=False, batch_size=128)
cur_time_caption = time.time()


import base64
import matplotlib.pyplot as plt
import io
plt.figure(figsize=(15,15))
image = Image.open(io.BytesIO(base64.b64decode(dino_labled_img)))
plt.axis('off')
plt.imshow(image)
image.save("output.png")
import pandas as pd
df = pd.DataFrame(parsed_content_list)
df['ID'] = range(len(df))
df
df.to_excel("output.xlsx", index=False)
