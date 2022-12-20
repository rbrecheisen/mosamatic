import os
import math
import shutil
import logging
import pandas as pd

from datetime import datetime
from .. import TaskJob, TaskForm

logger = logging.getLogger(__name__)


# TODO: Move to utils.py
def to_dd_mm_yyyy(df_data, date_columns):
    for date_column in date_columns:
        date_values = df_data[date_column].values
        new_date_values = []
        for date_value in date_values:
            if isinstance(date_value, float) and pd.isna(date_value):
                new_date_values.append(pd.NaT)
            else:
                date_str = date_value.split(' ')[0]
                items = date_str.split('/')
                if len(items) != 3:
                    new_date_values.append(pd.NaT)
                else:
                    new_date_values.append(f'{items[0]}-{items[1]}-{items[2]}')
        df_data[date_column] = new_date_values
    return df_data


# TODO: Move to utils.py
def to_yyyymmdd(date_values):
    new_date_values = []
    for date_value in date_values:
        if isinstance(date_value, float) and pd.isna(date_value):
            new_date_values.append(pd.NaT)
        else:
            items = date_value.split('-')
            if len(items) == 3:
                new_date_values.append(f'{items[2]}{items[1]}{items[0]}')
            else:
                new_date_values.append(pd.NaT)
    return new_date_values


class DicaExportNewToOldFormatConverter:

    def __init__(self):
        self.df_p = None
        self.df_t = None
        self.df_c = None
        self.columns_to_skip = [
            'uri',
            'patient_uri',
            'is_valid',
            'organisation_uri',
            'created',
            'updated'
        ]

    def load_data(
            self,
            export_excel_file,
            sheet_name_patients='patient',
            sheet_name_treatments='verrichting',
            sheet_name_comorbidities='comorbiditeiten',
    ):
        self.df_p = pd.read_excel(export_excel_file, dtype=str, sheet_name=sheet_name_patients, engine='openpyxl')
        self.df_t = pd.read_excel(export_excel_file, dtype=str, sheet_name=sheet_name_treatments, engine='openpyxl')
        self.df_c = pd.read_excel(export_excel_file, dtype=str, sheet_name=sheet_name_comorbidities, engine='openpyxl')

    def init_data(self):
        data = {}
        for c in self.df_t.columns:
            if c not in self.columns_to_skip:
                data[c] = []
        for c in self.df_p.columns:
            if c not in self.columns_to_skip:
                data[c] = []
        for c in self.df_c.columns:
            if c not in self.columns_to_skip:
                data[c] = []
        return data

    def get_treatment_values(self, row):
        new_row = {}
        for c in self.df_t.columns:
            if c not in self.columns_to_skip:
                if isinstance(row[c], str):
                    new_row[c] = row[c]
                else:
                    new_row[c] = ''
        return new_row

    def get_patient_values(self, patient_uri):
        new_row = {}
        for idx, row in self.df_p.iterrows():
            if row['uri'] == patient_uri:
                for c in self.df_p.columns:
                    if c not in self.columns_to_skip:
                        if isinstance(row[c], str):
                            new_row[c] = row[c]
                        else:
                            new_row[c] = ''
                break
        return new_row

    def get_comorbidity_values(self, patient_uri):
        new_row = {}
        for idx, row in self.df_c.iterrows():
            if row['patient_uri'] == patient_uri:
                for c in self.df_c.columns:
                    if c not in self.columns_to_skip:
                        if isinstance(row[c], str):
                            new_row[c] = row[c]
                        else:
                            new_row[c] = ''
        return new_row

    @staticmethod
    def add_row(data, treatment_values, patient_values, comorbidity_values):
        all_keys = list(treatment_values.keys()) + list(patient_values.keys()) + list(comorbidity_values.keys())
        for k in data.keys():
            if k not in all_keys:
                data[k].append('')
        for k in treatment_values.keys():
            data[k].append(treatment_values[k])
        for k in patient_values.keys():
            data[k].append(patient_values[k])
        for k in comorbidity_values.keys():
            data[k].append(comorbidity_values[k])
        return data

    def execute(self):
        data = self.init_data()
        for idx, row in self.df_t.iterrows():
            values_t = self.get_treatment_values(row)
            values_p = self.get_patient_values(row['patient_uri'])
            values_c = self.get_comorbidity_values(row['patient_uri'])
            data = self.add_row(
                data,
                values_t,
                values_p,
                values_c
            )
        return pd.DataFrame(data=data)


class ConvertDpcaExportToCastorImportTaskForm(TaskForm):
    pass


class ConvertDpcaExportToCastorImportTaskJob(TaskJob):

    def get_form(self):
        return ConvertDpcaExportToCastorImportTaskForm(self.task)

    def execute(self):
        self.task_job_begin()

        # Get form field inputs
        castor_export = self.get_input_dataset(self.get_str('castor_dpca_export_file'))
        castor_export_file = self.get_files(castor_export)[0]
        logger.info(f'Found Castor export file: {castor_export_file.path}')
        dpca_export = self.get_input_dataset(self.get_str('dpca_export_file'))
        dpca_export_file = self.get_files(dpca_export)[0]
        logger.info(f'Found DPCA export file: {dpca_export_file.path}')
        date_columns = self.get_list('date_columns')
        logger.info(f'Found date columns: {date_columns}')
        starting_record_nr = self.get_int('starting_record_nr')
        logger.info('Starting record ID: T{:04d}'.format(starting_record_nr))
        output_dataset = self.create_output_dataset(name=self.get_str('output_dataset_name'))
        logger.info(f'Created output dataset: {output_dataset.data_dir}')

        # Load Castor data
        logger.info('Loading Castor export file...')
        df_cast = pd.read_excel(castor_export_file.path, dtype=str, sheet_name='Study results', engine='openpyxl')
        df_cast = df_cast.dropna(subset=['dpca_datok'])
        df_cast.insert(0, 'datok_sortable', to_yyyymmdd(df_cast['dpca_datok'].values))

        # Load DPCA data
        logger.info('Loading DPCA export file...')
        converter = DicaExportNewToOldFormatConverter()
        converter.load_data(dpca_export_file.path)
        df_dpca = converter.execute()
        df_dpca = df_dpca.dropna(subset=['datok'])
        df_dpca.insert(0, 'datok_sortable', to_yyyymmdd(df_dpca['datok'].values))

        # castor_export_file_name = os.path.split(castor_export_file.path)[1]
        # shutil.copy(
        #     castor_export_file.path,
        #     os.path.join(output_dataset.data_dir, castor_export_file_name)
        # )
        # self.create_output_file(castor_export_file_name, output_dataset)

        self.task_job_end()
