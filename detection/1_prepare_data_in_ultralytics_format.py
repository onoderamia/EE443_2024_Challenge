import os
import os.path as osp
import cv2
from tqdm import tqdm
import numpy as np
import json
import shutil

# root path to your data folder
raw_data_root = 'C:/Users/konya/Desktop/UW/ee classes/ee443/EE443_2024_Challenge/data/data'
ultra_data_root = 'C:/Users/konya/Desktop/UW/ee classes/ee443/EE443_2024_Challenge/ultralytics_data'

# shared variables
W, H = 1920, 1080
data_list = {
    'train': ['camera_0001', 'camera_0003', 'camera_0011', 'camera_0013', 'camera_0020', 'camera_0021'],
    'val': ['camera_0005', 'camera_0017', 'camera_0025']
}
sample_rate = 30  # Changed this to 30 for better performance

# Create directories for images and labels in each split
for split in ['train', 'val']:
    # path where you want to move and rename the images
    ultra_img_path = osp.join(ultra_data_root, split, 'images')
    # path where you want to create the labels
    ultra_label_path = osp.join(ultra_data_root, split, 'labels')

    # Create directories if they don't exist
    if not osp.exists(ultra_img_path):
        os.makedirs(ultra_img_path)
    if not osp.exists(ultra_label_path):
        os.makedirs(ultra_label_path)


if __name__ == "__main__":
    for split in ['train', 'val']:
        for folder in data_list[split]:

            # 1. Copy and rename the images
            img_folder = osp.join(raw_data_root, split, folder)
            ultra_img_path = osp.join(ultra_data_root, split, 'images')

            # List all images in the original folder
            img_list = os.listdir(img_folder)
            img_list.sort()
            for img_name in tqdm(img_list):
                # Sample frames based on sample_rate
                if int(img_name.split('.')[0]) % sample_rate != 0:
                    continue
                original_path = osp.join(img_folder, img_name)
                new_path = osp.join(ultra_img_path, f'{folder}_{img_name}')
                print(f'Copying {original_path} to {new_path}')
                shutil.copyfile(original_path, new_path)

            # 2. Extract the labels
            ultra_label_path = osp.join(ultra_data_root, split, 'labels')
            gt_path = osp.join(raw_data_root, split, folder + '.txt')
            gt = np.loadtxt(gt_path, delimiter=',')

            # Iterate over unique frame IDs in ground truth
            for frame_id in sorted(np.unique(gt[:, 2])):
                if frame_id % sample_rate != 0:
                    continue
                # Filter detections for the current frame
                frame_det = gt[gt[:, 2] == frame_id]
                x = frame_det[:, 3]
                y = frame_det[:, 4]
                w = frame_det[:, 5]
                h = frame_det[:, 6]

                # Normalize bounding box coordinates
                normalized_center_x = (x + w / 2) / W
                normalized_center_y = (y + h / 2) / H
                normalized_w = w / W
                normalized_h = h / H
                cls = np.array([0] * len(frame_det))  # Assuming class 0 for all detections

                # Create label in YOLO format
                label = np.stack([cls, normalized_center_x, normalized_center_y, normalized_w, normalized_h], axis=1)

                # Save label to file
                label_path = osp.join(ultra_label_path, f'{folder}_{int(frame_id):05d}.txt')
                np.savetxt(label_path, label, fmt='%.3f', delimiter=' ')

