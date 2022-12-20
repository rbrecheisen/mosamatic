import os.path
import shutil
import pandas as pd
import pydicom
import pydicom.errors
import logging

from barbell2.imaging.utils import get_pixels
from barbell2.imaging import npy2png, npy2dcm, dcm2npy
from .. import TaskJob, TaskForm
from .utils import *


logger = logging.getLogger(__name__)


class PredictBodyCompositionTaskForm(TaskForm):
    pass


class PredictBodyCompositionTaskJob(TaskJob):

    def get_form(self):
        return PredictBodyCompositionTaskForm(self.task)

    def execute(self):

        self.task_job_begin()

        model, contour_model, params = load_model_files(self.get_files(self.task.parameters['tensorflow_model_files']))
        l3_images = self.get_input_dataset(self.task.parameters['l3_images'])
        output_dataset = self.create_output_dataset(name=self.task.parameters['output_dataset_name'])

        scores = {
            'file_name': [],
            'smra': [],
            'muscle_area': [],
            'vat_ra': [],
            'vat_area': [],
            'sat_ra': [],
            'sat_area': [],
        }

        for file_path_model in self.get_files(l3_images):

            dcm_file_path = file_path_model.path
            if not is_dicom_file(dcm_file_path):
                logger.warning(f'File {dcm_file_path} is not valid DICOM file')
                continue
            else:
                # It's a DICOM file but check that it's extension is either '' or '.dcm'
                extension = os.path.splitext(dcm_file_path)[1]
                if extension != '' and extension != '.dcm':
                    logger.warning(f'File {dcm_file_path} is DICOM but has illegal extension "{extension}"')
                    continue

            p = pydicom.dcmread(dcm_file_path)
            logger.info(f'Loaded DICOM file {dcm_file_path}...')

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
            # Pass in already loaded DICOM object
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
            # Pass in already loaded DICOM object
            d2n = dcm2npy.Dicom2Numpy(dcm_file_path)
            d2n.set_window((400, 50))
            arr = d2n.execute()
            n2p = npy2png.Numpy2Png(arr)
            n2p.set_output_dir(output_dataset.data_dir)
            n2p.set_png_file_name(os.path.split(dcm_file_path)[1] + '.png')
            n2p.execute()
            self.create_output_file(n2p.png_file_name, output_dataset)

            # Calculate scores
            pixel_spacing = p.PixelSpacing
            image = get_pixels(p, normalize=True)

            file_name = os.path.split(dcm_file_path)[1]
            smra = calculate_mean_radiation_attenuation(image, MUSCLE, pred_max)
            muscle_area = calculate_area(pred_max, MUSCLE, pixel_spacing)
            vat_ra = calculate_mean_radiation_attenuation(image, VAT, pred_max)
            vat_area = calculate_area(pred_max, VAT, pixel_spacing)
            sat_ra = calculate_mean_radiation_attenuation(image, SAT, pred_max)
            sat_area = calculate_area(pred_max, SAT, pixel_spacing)

            logger.info('[OK] file_name: {}'.format(file_name))
            logger.info('     - smra: {}'.format(smra))
            logger.info('     - muscle_area: {}'.format(muscle_area))
            logger.info('     - vat_ra: {}'.format(vat_ra))
            logger.info('     - vat_area: {}'.format(vat_area))
            logger.info('     - sat_ra: {}'.format(sat_ra))
            logger.info('     - sat_area: {}'.format(sat_area))

            scores['file_name'].append(file_name)
            scores['smra'].append(smra)
            scores['muscle_area'].append(muscle_area)
            scores['vat_ra'].append(vat_ra)
            scores['vat_area'].append(vat_area)
            scores['sat_ra'].append(sat_ra)
            scores['sat_area'].append(sat_area)

        # Build CSV for body composition scores and add to output dataset
        csv_name = 'scores.csv'
        csv_path = os.path.join(output_dataset.data_dir, csv_name)
        df_scores = pd.DataFrame(data=scores)
        df_scores.to_csv(csv_path)
        self.create_output_file(csv_name, output_dataset)
        logger.info(f'[OK] csv_path: {csv_path}')

        self.task_job_end()
