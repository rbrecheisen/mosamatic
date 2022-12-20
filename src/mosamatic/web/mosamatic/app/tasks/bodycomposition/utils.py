import os
import json
import zipfile
import logging
import numpy as np

from barbell2 import tag2npy
from barbell2.utils import get_tag_file_for_dicom, is_dicom_file

logger = logging.getLogger(__name__)


MUSCLE = 1
VAT = 5
SAT = 7


def normalize(img, min_bound, max_bound):
    img = (img - min_bound) / (max_bound - min_bound)
    img[img > 1] = 0
    img[img < 0] = 0
    c = (img - np.min(img))
    d = (np.max(img) - np.min(img))
    img = np.divide(c, d, np.zeros_like(c), where=d != 0)
    return img


def calculate_area(labels, label, pixel_spacing):
    mask = np.copy(labels)
    mask[mask != label] = 0
    mask[mask == label] = 1
    area = np.sum(mask) * (pixel_spacing[0] * pixel_spacing[1]) / 100.0
    return area


def calculate_mean_radiation_attenuation(image, label, labels):
    mask = np.copy(labels)
    mask[mask != label] = 0
    mask[mask == label] = 1
    subtracted = image * mask
    mask_sum = np.sum(mask)
    if mask_sum > 0.0:
        mean_ra = np.sum(subtracted) / np.sum(mask)
    else:
        print('Sum of mask pixels is zero, return zero radiation attenuation')
        mean_ra = 0.0
    return mean_ra


# def convert_labels_to_123(ground_truth):
#     new_ground_truth = np.copy(ground_truth)
#     new_ground_truth[new_ground_truth == 1] = 1
#     new_ground_truth[new_ground_truth == 5] = 2
#     new_ground_truth[new_ground_truth == 7] = 3
#     return new_ground_truth


def convert_labels_to_157(prediction):
    new_prediction = np.copy(prediction)
    new_prediction[new_prediction == 1] = 1
    new_prediction[new_prediction == 2] = 5
    new_prediction[new_prediction == 3] = 7
    return new_prediction


def calculate_dice_score(ground_truth, prediction, label):
    numerator = prediction[ground_truth == label]
    numerator[numerator != label] = 0
    n = ground_truth[prediction == label]
    n[n != label] = 0
    if np.sum(numerator) != np.sum(n):
        raise RuntimeError('Mismatch in Dice score calculation!')
    denominator = (np.sum(prediction[prediction == label]) + np.sum(ground_truth[ground_truth == label]))
    dice_score = np.sum(numerator) * 2.0 / denominator
    return dice_score


def update_labels(pixels, file_name):
    # http://www.tomovision.com/Sarcopenia_Help/index.htm
    labels_to_keep = [0, 1, 5, 7]
    labels_to_remove = [2, 12, 14]
    for label in np.unique(pixels):
        if label in labels_to_remove:
            pixels[pixels == label] = 0
    for label in np.unique(pixels):
        if label not in labels_to_keep:
            return None
    if len(np.unique(pixels)) != 4:
        print('[{}] Incorrect nr. of labels: {}'.format(file_name, len(np.unique(pixels))))
        return None
    return pixels


def get_tag_file_pixels(tag_file_path, shape):
    converter = tag2npy.Tag2Numpy(tag_file_path, shape)
    pixels = converter.execute()
    return update_labels(pixels, os.path.split(tag_file_path)[1])


def predict_contour(contour_model, src_img, params):
    ct = np.copy(src_img)
    ct = normalize(
        ct, params['min_bound_contour'], params['max_bound_contour'])
    img2 = np.expand_dims(ct, 0)
    img2 = np.expand_dims(img2, -1)
    pred = contour_model.predict([img2])
    pred_squeeze = np.squeeze(pred)
    pred_max = pred_squeeze.argmax(axis=-1)
    mask = np.uint8(pred_max)
    return mask


def load_model(file_path_model):
    import tensorflow as tf
    with zipfile.ZipFile(file_path_model.path) as zip_obj:
        zip_obj.extractall(path=file_path_model.dataset.data_dir)
    return tf.keras.models.load_model(file_path_model.dataset.data_dir, compile=False)


def load_params(file_path_model):
    with open(file_path_model.path) as f:
        return json.load(f)


def load_model_files(file_path_models):
    # model = load_model('/data/tensorflow/model.zip')
    # contour_model = load_model('/data/tensorflow/contour_model.zip')
    # params = load_params('/data/tensorflow/params.json')
    model, contour_model, params = None, None, None
    for file_path_model in file_path_models:
        file_name = os.path.split(file_path_model.path)[1]
        if file_name == 'model.zip':
            model = load_model(file_path_model)
        elif file_name == 'contour_model.zip':
            contour_model = load_model(file_path_model)
        elif file_name == 'params.json':
            params = load_params(file_path_model)
        else:
            raise RuntimeError(f'Unknown model file {file_name}')
    return model, contour_model, params


def get_l3_tag_file_pairs(file_path_models):
    file_pairs = []
    for file_path_model in file_path_models:
        if is_dicom_file(file_path_model.path):
            dcm_file = file_path_model.path
            tag_file = get_tag_file_for_dicom(dcm_file)
            if tag_file is None:
                logger.warning(f'TAG file for DICOM {dcm_file} not found')
                continue
            file_pairs.append((dcm_file, tag_file))
    return file_pairs
