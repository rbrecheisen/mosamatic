import os
import math
import logging
import pandas as pd

from datetime import datetime
from .. import TaskJob, TaskForm

logger = logging.getLogger(__name__)


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


class ConvertDpcaExportToCastorImportTaskForm(TaskForm):
    pass


class ConvertDpcaExportToCastorImportTaskJob(TaskJob):

    def get_form(self):
        return ConvertDpcaExportToCastorImportTaskForm(self.task)

    def execute(self):

        self.task_job_begin()

        dpca_export = self.get_input_dataset(self.task.parameters['dpca_export_file'])
        dpca_export_file = self.get_files(dpca_export)[0]
        castor_export = self.get_input_dataset(self.task.parameters['castor_dpca_export_file'])
        castor_export_file = self.get_files(castor_export)[0]
        output_dataset = self.create_output_dataset(name=self.task.parameters['output_dataset_name'])
        date_columns = self.get_list('date_columns')
        logger.info(f'Found date columns: {date_columns}')

        logger.info(f'Loading Castor CSV file {castor_export_file.path}')
        # df_cast = pd.read_csv(castor_export_file.path, delimiter=';', dtype=str)
        df_cast = pd.read_excel(castor_export_file.path, dtype=str, sheet_name='Study results')
        logger.info('Dropping records with null (NA) surgery date (dpca_datok)')
        df_cast = df_cast.dropna(subset=['dpca_datok'])
        logger.info('Inserting new column sortable surgery date (datok_sortable)')
        df_cast.insert(0, 'datok_sortable', to_yyyymmdd(df_cast['dpca_datok'].values))
        logger.info('Inserting new column combining sortable surgery date and hospital ID (dpca_idcode)')
        new_values = []
        for idx, row in df_cast.iterrows():
            new_values.append('{}_{}'.format(row['datok_sortable'], row['dpca_idcode']))
        df_cast.insert(0, 'datok_idcode', new_values)

        # Get last record number
        last_record = df_cast.iloc[-1]
        last_record_id = last_record['Record Id']
        logger.info(f'Last record ID: {last_record_id}')
        first_new_record_nr = int(last_record_id[1:]) + 1
        logger.info(f'First new record number: {first_new_record_nr}')

        logger.info(f'Loading DPCA CSV file {dpca_export_file.path}')
        df_dpca = pd.read_csv(dpca_export_file.path, delimiter=';', dtype=str)
        logger.info(f'Nr. records: {len(df_dpca.index)}')
        logger.info('Dropping records with null (NA) surgery date (datok)')
        df_dpca = df_dpca.dropna(subset=['datok'])
        logger.info(f'Nr. records: {len(df_dpca.index)}')
        logger.info('Converting date columns to dd-mm-yyyy format')
        df_dpca = to_dd_mm_yyyy(df_dpca, date_columns)
        logger.info('Inserting new column sortable surgery date (datok_sortable)')
        df_dpca.insert(0, 'datok_sortable', to_yyyymmdd(df_dpca['datok'].values))
        logger.info('Removing records where datok != datcom')
        record_indexes_to_delete = []
        for idx, row in df_dpca.iterrows():
            if row['datok'] != row['datcom']:
                record_indexes_to_delete.append(idx)
        df_dpca = df_dpca.drop(record_indexes_to_delete, axis=0)
        logger.info('Inserting new column combining sortable surgery date and hospital ID (idcode)')
        new_values = []
        for idx, row in df_dpca.iterrows():
            new_values.append('{}_{}'.format(row['datok_sortable'], row['upn']))
        df_dpca.insert(0, 'datok_idcode', new_values)
        logger.info('Extracting only new records from DCPA')
        new_record_indexes = []
        for idx, row in df_dpca.iterrows():
            datok_idcode = row['datok_idcode']
            if datok_idcode not in df_cast['datok_idcode'].values:
                new_record_indexes.append(idx)
        df_dpca = df_dpca.loc[new_record_indexes]

        f = 'dpca_file_new_records.csv'
        df_dpca.to_csv(os.path.join(output_dataset.data_dir, f))
        self.create_output_file(f, output_dataset)

        df_cast.drop(['datok_sortable', 'datok_idcode'], axis=1, inplace=True)
        df_dpca.drop(['datok_sortable', 'datok_idcode'], axis=1, inplace=True)

        data = {}
        date_today = datetime.today().strftime('%d-%m-%Y')
        record_nr = first_new_record_nr
        for column in df_cast.columns:
            data[column] = []
        for idx, row in df_dpca.iterrows():
            for column_cast in df_cast.columns:
                column_dpca = column_cast[5:]
                if column_dpca in df_dpca.columns:
                    if column_dpca == 'idcode':   # Reading verrichting_upn variable instead, because idcode is [ENC]
                        data[column_cast].append(row['verrichting_upn'])
                    else:
                        data[column_cast].append(row[column_dpca])
                else:
                    if column_cast == 'Record Id':
                        data['Record Id'].append(f'T{str(record_nr).zfill(4)}')
                        record_nr += 1
                    elif column_cast == 'Record Status':
                        data['Record Status'].append('Not Set')
                    elif column_cast == 'Institute Abbreviation':
                        data['Institute Abbreviation'].append('MUMC')
                    elif column_cast == 'Record Creation Date':
                        data['Record Creation Date'].append(date_today)
                    else:
                        data[column_cast].append('')

        index = True
        df_cast_new = pd.DataFrame(data=data)
        f = 'castor_dpca_file_new_records_all.csv'
        df_cast_new.to_csv(os.path.join(output_dataset.data_dir, f), index=index)
        self.create_output_file(f, output_dataset)

        # Create multiple CSV files if main CSV file contains >25000 data points
        logger.info('Writing output CSV files')
        nr_rows = len(df_cast_new.index)
        nr_cols = len(df_cast_new.columns)
        nr_data_points = nr_rows * nr_cols
        logger.info(f'Nr. rows: {nr_rows}, nr. cols: {nr_cols}, nr.data points: {nr_data_points}')

        if nr_data_points > 25000:
            logger.info('Nr. data points > 25000')
            max_nr_rows = int(math.floor(25000.0 / len(df_cast_new.columns)))
            logger.info(f'Max. nr. rows allowed: {max_nr_rows}')
            nr_files = int(math.floor(nr_rows / float(max_nr_rows)))
            logger.info(f'Nr. CSV files required: {nr_files}')
            nr_remaining_rows = nr_rows - (nr_files * max_nr_rows)
            logger.info(f'Nr. remaining rows: {nr_remaining_rows}')

            start = 0
            end = max_nr_rows
            for i in range(nr_files):
                f = 'castor_dpca_file_new_records_{:02d}.csv'.format(i)
                df_cast_new_chunk = df_cast_new[start:end]
                df_cast_new_chunk.to_csv(os.path.join(output_dataset.data_dir, f), index=index)
                self.create_output_file(f, output_dataset)
                logger.info(f'Written CSV: {f}, start = {start}, end = {end}')
                if i < nr_files - 1:
                    start = end
                    end += max_nr_rows

            if nr_remaining_rows > 0:
                start = end
                end += nr_remaining_rows
                f = 'castor_dpca_file_new_records_{:02d}.csv'.format(nr_files)
                df_cast_new_chunk = df_cast_new[start:end]
                df_cast_new_chunk.to_csv(os.path.join(output_dataset.data_dir, f), index=index)
                self.create_output_file(f, output_dataset)
                logger.info(f'Written remaining rows: {f}, start = {start}, end = {end}')

        self.task_job_end()
