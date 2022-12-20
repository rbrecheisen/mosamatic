import os
import shutil
import pydicom
import logging
import pandas as pd

from .. import TaskJob, TaskForm
from .utils import *
from barbell2.imaging import npy2png, npy2dcm, dcm2npy, tag2npy, tag2dcm
from barbell2.imaging.utils import get_pixels, get_tag_pixels

logger = logging.getLogger(__name__)


class ValidateModelTaskForm(TaskForm):
    pass


class ValidateModelTaskJob(TaskJob):
    """ TODO: Add SAT attenuation and VAT attenuation !"""
    def get_form(self):
        return ValidateModelTaskForm(self.task)

    def execute(self):

        self.task_job_begin()

        model, contour_model, params = load_model_files(self.get_files(self.task.parameters['tensorflow_model_files']))
        l3_images_and_tag_files = self.get_input_dataset(self.task.parameters['l3_images_and_tag_files'])
        output_dataset = self.create_output_dataset(name=self.task.parameters['output_dataset_name'])

        scores = {
            'file_name': [],
            'smra_pred': [],
            'smra_true': [],
            'muscle_area_pred': [],
            'muscle_area_true': [],
            'vat_ra_pred': [],
            'vat_ra_true': [],
            'vat_area_pred': [],
            'vat_area_true': [],
            'sat_ra_pred': [],
            'sat_ra_true': [],
            'sat_area_pred': [],
            'sat_area_true': [],
            'dice_muscle': [],
            'dice_vat': [],
            'dice_sat': [],
        }

        for l3_tag_file_pair in get_l3_tag_file_pairs(self.get_files(l3_images_and_tag_files)):
            # Load DICOM pixel data
            dcm_file_path = l3_tag_file_pair[0]
            logger.info(f'[OK] Processing {dcm_file_path}...')
            p = pydicom.dcmread(dcm_file_path)
            img1 = get_pixels(p, normalize=True)

            # Apply contour detection model if available
            if contour_model is not None:
                mask = predict_contour(contour_model, img1, params)
                img1 = normalize(img1, params['min_bound'], params['max_bound'])
                img1 = img1 * mask
            else:
                img1 = normalize(img1, params['min_bound'], params['max_bound'])

            img1 = img1.astype(np.float32)
            img2 = np.expand_dims(img1, 0)
            img2 = np.expand_dims(img2, -1)
            pred = model.predict([img2])
            pred_squeeze = np.squeeze(pred)
            pred_max = pred_squeeze.argmax(axis=-1)
            pred_max = convert_labels_to_157(pred_max)
            pred_file_name = os.path.split(dcm_file_path)[1]
            pred_file_name = os.path.splitext(pred_file_name)[0] + '_seg.npy'
            pred_file_path = os.path.join(output_dataset.data_dir, pred_file_name)

            # Save segmentation output and add to output dataset
            np.save(pred_file_path, pred_max)
            self.create_output_file(pred_file_name, output_dataset)

            # Copy original DICOM file to output dataset
            shutil.copy(dcm_file_path, output_dataset.data_dir)
            self.create_output_file(os.path.split(dcm_file_path)[1], output_dataset)

            # Convert segmentation output to DICOM format and add to output dataset
            n2d = npy2dcm.Numpy2Dicom(pred_file_path, dcm_file_path)
            n2d.set_output_dir(output_dataset.data_dir)
            n2d.set_npy_dcm_file_name(os.path.split(pred_file_path)[1] + '.dcm')
            n2d.execute()
            self.create_output_file(n2d.npy_dcm_file_name, output_dataset)

            # Create PNG from segmentation output and add to output dataset
            n2p = npy2png.Numpy2Png(pred_file_path)
            n2p.set_output_dir(output_dataset.data_dir)
            n2p.set_color_map('alberta')
            n2p.set_png_file_name(os.path.split(pred_file_path)[1] + '.png')
            n2p.execute()
            self.create_output_file(n2p.png_file_name, output_dataset)

            # Create PNG of original DICOM and add to output dataset
            d2n = dcm2npy.Dicom2Numpy(dcm_file_path)
            d2n.set_window((400, 50))
            n2p = npy2png.Numpy2Png(d2n.execute())
            n2p.set_output_dir(output_dataset.data_dir)
            n2p.set_png_file_name(os.path.split(dcm_file_path)[1] + '.png')
            n2p.execute()
            self.create_output_file(n2p.png_file_name, output_dataset)

            # Add TAG file to output dataset
            tag_file_path = l3_tag_file_pair[1]
            shutil.copy(tag_file_path, output_dataset.data_dir)

            # Create DICOM of TAG file and add to output dataset
            t2d = tag2dcm.Tag2Dicom(tag_file_path, dcm_file_path)
            t2d.set_output_dir(output_dataset.data_dir)
            t2d.execute()
            self.create_output_file(t2d.tag_dcm_file_name, output_dataset)

            # Create PNG of TAG file and add to output dataset
            t2n = tag2npy.Tag2Numpy(tag_file_path, shape=(p.Rows, p.Columns))
            n2p = npy2png.Numpy2Png(t2n.execute())
            n2p.set_color_map('alberta')
            n2p.set_output_dir(output_dataset.data_dir)
            n2p.set_png_file_name(os.path.split(tag_file_path)[1] + '.png')
            n2p.execute()
            self.create_output_file(n2p.png_file_name, output_dataset)

            # Calculate scores
            pixel_spacing = p.PixelSpacing
            image_pixels = get_pixels(p, normalize=True)
            tag_pixels = get_tag_file_pixels(tag_file_path, shape=(p.Rows, p.Columns))

            file_name = os.path.split(dcm_file_path)[1]

            if tag_pixels is not None:
                smra_pred = calculate_mean_radiation_attenuation(image_pixels, MUSCLE, pred_max)
                smra_true = calculate_mean_radiation_attenuation(image_pixels, MUSCLE, tag_pixels)
                muscle_area_pred = calculate_area(pred_max, MUSCLE, pixel_spacing)
                muscle_area_true = calculate_area(tag_pixels, MUSCLE, pixel_spacing)
                vat_ra_pred = calculate_mean_radiation_attenuation(image_pixels, VAT, pred_max)
                vat_ra_true = calculate_mean_radiation_attenuation(image_pixels, VAT, tag_pixels)
                vat_area_pred = calculate_area(pred_max, VAT, pixel_spacing)
                vat_area_true = calculate_area(tag_pixels, VAT, pixel_spacing)
                sat_ra_pred = calculate_mean_radiation_attenuation(image_pixels, SAT, pred_max)
                sat_ra_true = calculate_mean_radiation_attenuation(image_pixels, SAT, tag_pixels)
                sat_area_pred = calculate_area(pred_max, SAT, pixel_spacing)
                sat_area_true = calculate_area(tag_pixels, SAT, pixel_spacing)
                dice_muscle = calculate_dice_score(tag_pixels, pred_max, label=MUSCLE)
                dice_vat = calculate_dice_score(tag_pixels, pred_max, label=VAT)
                dice_sat = calculate_dice_score(tag_pixels, pred_max, label=SAT)

            else:
                logger.warning('[WARNING] TAG pixels is None, setting scores to zero')

                smra_pred = 0
                smra_true = 0
                muscle_area_pred = 0
                muscle_area_true = 0
                vat_ra_pred = 0
                vat_ra_true = 0
                vat_area_pred = 0
                vat_area_true = 0
                sat_ra_pred = 0
                sat_ra_true = 0
                sat_area_pred = 0
                sat_area_true = 0
                dice_muscle = 0
                dice_vat = 0
                dice_sat = 0

            logger.info('     - smra_pred: {}'.format(smra_pred))
            logger.info('     - smra_true: {}'.format(smra_true))
            logger.info('     - muscle_area_pred: {}'.format(muscle_area_pred))
            logger.info('     - muscle_area_true: {}'.format(muscle_area_true))
            logger.info('     - vat_ra_pred: {}'.format(vat_ra_pred))
            logger.info('     - vat_ra_true: {}'.format(vat_ra_true))
            logger.info('     - vat_area_pred: {}'.format(vat_area_pred))
            logger.info('     - vat_area_true: {}'.format(vat_area_true))
            logger.info('     - sat_ra_pred: {}'.format(sat_ra_pred))
            logger.info('     - sat_ra_true: {}'.format(sat_ra_true))
            logger.info('     - sat_area_pred: {}'.format(sat_area_pred))
            logger.info('     - sat_area_true: {}'.format(sat_area_true))
            logger.info('     - dice_muscle: {}'.format(dice_muscle))
            logger.info('     - dice_vat: {}'.format(dice_vat))
            logger.info('     - dice_sat: {}'.format(dice_sat))

            scores['file_name'].append(file_name)
            scores['smra_pred'].append(smra_pred)
            scores['smra_true'].append(smra_true)
            scores['muscle_area_pred'].append(muscle_area_pred)
            scores['muscle_area_true'].append(muscle_area_true)
            scores['vat_ra_pred'].append(vat_ra_pred)
            scores['vat_ra_true'].append(vat_ra_true)
            scores['vat_area_pred'].append(vat_area_pred)
            scores['vat_area_true'].append(vat_area_true)
            scores['sat_ra_pred'].append(sat_ra_pred)
            scores['sat_ra_true'].append(sat_ra_true)
            scores['sat_area_pred'].append(sat_area_pred)
            scores['sat_area_true'].append(sat_area_true)
            scores['dice_muscle'].append(dice_muscle)
            scores['dice_vat'].append(dice_vat)
            scores['dice_sat'].append(dice_sat)

        # Build CSV for body composition scores and add to output dataset
        csv_name = 'scores.csv'
        csv_path = os.path.join(output_dataset.data_dir, csv_name)
        df_scores = pd.DataFrame(data=scores)
        df_scores.to_csv(csv_path)
        self.create_output_file(csv_name, output_dataset)
        logger.info('[OK] csv_path: {}'.format(csv_path))

        self.task_job_end()
