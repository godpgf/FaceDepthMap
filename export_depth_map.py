import argparse
import os
import numpy as np
import cv2
from tqdm import tqdm
from predictor import PosPrediction
from libfdm import FDM

parser = argparse.ArgumentParser()
parser.add_argument('--data_path', type=str, default="./clean", help='数据文件地址')
parser.add_argument('--model_path', type=str, default="./resources", help="模型文件")
parser.add_argument('--last_name', type=str, default="_1.mp4", help="后置名")
args = parser.parse_args()


def read_frame_list(path):
    cap = cv2.VideoCapture(path)
    frame_list = []
    ret, frame = cap.read()
    while ret:
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_list.append(img)
        ret, frame = cap.read()
    return frame_list


def save_frame_list(path, frame_list, frame_rate=30):
    height, width = frame_list[0].shape[:2]
    # 视频保存初始化 VideoWriter
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video_writer = cv2.VideoWriter(path, fourcc, frame_rate, (width, height))
    for id, img in enumerate(frame_list):
        video_writer.write(img)
    video_writer.release()
    cv2.destroyAllWindows()


def cal_depth_map(img):
    height, width = img.shape[:2]
    img = cv2.resize(img, (256, 256)) / 255.
    cropped_pos = pos_predictor.predict(img)
    # 转化到原图空间
    all_vertices = np.reshape(cropped_pos, [256 * 256, -1])
    vertices = all_vertices[face_ind, :]
    depth = fdm.cal_depth_face(vertices)
    new_img = cv2.resize(depth, (height, width))
    #new_img = cv2.resize(cal_depth_face(img, vertices), (height, width))

    # img = cv2.resize(img, (384, 384))
    # img = np.where(new_img > 0, new_img, img)
    # show_img(img)

    # 只裁剪出面部区域
    # cropped_img = focus_face(new_img)
    # cropped_img = np.where(cropped_img <= 0, img, cropped_img)
    # show_img(cropped_img)
    # return cropped_img
    return new_img


def read_img_list(file_path):
    if file_path.endswith(".mp4"):

        return read_frame_list(file_path)


def write_img_list(file, depth_map_list):
    if file.endswith(".mp4"):
        save_frame_list(os.path.join(args.data_path,  file.replace(".mp4", "_d.mp4")), depth_map_list)


def main():
    file_list = [file for file in os.listdir(args.data_path) if file.endswith(args.last_name) and not file.startswith("depth")]
    for file in tqdm(file_list):
        img_list = read_img_list(os.path.join(args.data_path, file))
        depth_map_list = []
        for img in img_list:
            gray_img = cal_depth_map(img)
            #gray_img = (depth_map * 255).astype(np.uint8)

            # 测试
            # gray_img = np.where(gray_img == 0, img, gray_img)

            depth_map_list.append(gray_img)
        write_img_list(file, depth_map_list)


if __name__ == '__main__':
    # 网络推理
    pos_predictor = PosPrediction(256, 256)
    pos_predictor.restore(os.path.join(args.model_path, "net-data", "256_256_resfcn256_weight"))
    # 这里是标准面部空间的所有点，也是配置死的
    face_ind = np.loadtxt(os.path.join(args.model_path, "uv-data", "face_ind.txt")).astype(np.int32)
    fdm = FDM(256, 256)
    main()
