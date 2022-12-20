import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_DIR = os.environ.get('ROOT_DIR', '/data')
if ROOT_DIR != '/data':
    os.makedirs(ROOT_DIR, exist_ok=True)

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_rq',
    # 'django_jinja',
    'session_security',
    'crispy_forms',
    'crispy_bootstrap5',
    'app',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mosamatic.urls'

TEMPLATES = [
    # {
    #     'BACKEND': 'django_jinja.backend.Jinja2',
    #     'DIRS': [],
    #     'APP_DIRS': True,
    #     'OPTIONS': {
    #         'match_extension': '.html',
    #     },
    # },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mosamatic.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': os.environ.get('POSTGRES_HOST', 'mosamatic_postgres'),
        'PORT': 5432,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

RQ_QUEUES = {
    'default': {
        'HOST': os.environ.get('REDIS_HOST', 'mosamatic_redis'),
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 86400,
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'CET'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(ROOT_DIR, 'static')

MEDIA_URL = '/datasets/'
MEDIA_ROOT = os.path.join(ROOT_DIR, 'datasets')

UPLOAD_ROOT = os.path.join(ROOT_DIR, 'uploads')

SESSION_SECURITY_WARN_AFTER = 840
SESSION_SECURITY_EXPIRE_AFTER = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

TASK_TYPES = [
    {
        'name': 'AnalyzeBodyComposition',
        'display_name': 'Analyze body composition',
        'class_path': 'app.tasks.bodycomposition.predict.PredictBodyCompositionTaskJob',
        'parameters': [
            {
                'name': 'tensorflow_model_files',
                'display_name': 'TensorFlow model files',
                'data_type': 'dataset',
                'required': True,
            },
            {
                'name': 'l3_images',
                'display_name': 'L3 images',
                'data_type': 'dataset',
                'required': True
            },
            {
                'name': 'output_dataset_name',
                'display_name': 'Output dataset name',
                'data_type': 'str',
                'required': False
            },
        ]        
    },
    {
        'name': 'ValidateBodyCompositionPredictionModel',
        'display_name': 'Validate body composition prediction model',
        'class_path': 'app.tasks.bodycomposition.validate.ValidateModelTaskJob',
        'parameters': [
            {
                'name': 'tensorflow_model_files',
                'display_name': 'TensorFlow model files',
                'data_type': 'dataset',
                'required': True,
            },
            {
                'name': 'l3_images_and_tag_files',
                'display_name': 'L3 images and TAG files',
                'data_type': 'dataset',
                'required': True
            },
            {
                'name': 'output_dataset_name',
                'display_name': 'Output dataset name',
                'data_type': 'str',
                'required': False
            },
        ]
    },
    {
        'name': 'CheckDicoms',
        'display_name': 'Check DICOM header properties',
        'class_path': 'app.tasks.bodycomposition.checkdicoms.CheckDicomsTaskJob',
        'parameters': [
            {
                'name': 'input',
                'display_name': 'DICOM files',
                'data_type': 'dataset',
                'required': True,
            },
            {
                'name': 'extensions_to_ignore',
                'display_name': 'Comma-separated list of extensions to ignore, e.g., "txt,png,csv"',
                'data_type': 'list',
                'required': False,
            },
            {
                'name': 'add_ignored_files_to_output',
                'display_name': 'Add ignored files to output',
                'data_type': 'bool',
                'default_value': True,
            },
            {
                'name': 'required_attributes',
                'display_name': 'Comma-separated list of required DICOM attributes',
                'data_type': 'list',
                'required': True,
                'default_value': 'PixelSpacing,Rows,Columns,RescaleSlope,RescaleIntercept,PixelData,BitsStored'
            },
            {
                'name': 'rows',
                'display_name': 'Rows',
                'data_type': 'int',
                'required': True,
                'default_value': 512,
                'min_value': 0,
                'max_value': 1000,
            },
            {
                'name': 'columns',
                'display_name': 'Columns',
                'data_type': 'int',
                'required': True,
                'default_value': 512,
                'min_value': 0,
                'max_value': 1000,
            },
            {
                'name': 'bits_stored',
                'display_name': 'Bits Stored',
                'data_type': 'int',
                'required': True,
                'default_value': 16,
                'min_value': 8,
                'max_value': 64,
            },
            {
                'name': 'output_dataset_name',
                'display_name': 'Output dataset name',
                'data_type': 'str',
                'required': False,
            }
        ]
    },
    {
        'name': 'ConvertDicomToRaw',
        'display_name': 'Convert JPEG-compressed DICOM files to raw format',
        'class_path': 'app.tasks.dcm2raw.task.DicomToRawTaskJob',
        'parameters': [
            {
                'name': 'input',
                'display_name': 'Compressed DICOM files',
                'data_type': 'dataset',
                'required': True,
            },
            {
                'name': 'output_dataset_name',
                'display_name': 'Output dataset name',
                'data_type': 'str',
                'required': False,
            },
        ],
    },
    {
        'name': 'ConvertDicomToPng',
        'display_name': 'Convert DICOM files to PNG images',
        'class_path': 'app.tasks.dcm2png.task.DicomToPngTaskJob',
        'parameters': [
            {
                'name': 'input',
                'display_name': 'DICOM files',
                'data_type': 'dataset',
                'required': True,
            },
            {
                'name': 'normalize_enabled',
                'display_name': 'Enable normalization',
                'data_type': 'bool',
                'required': False,
            },
            {
                'name': 'window_width',
                'display_name': 'Window width',
                'data_type': 'int',
                'required': False,
            },
            {
                'name': 'window_level',
                'display_name': 'Window level',
                'data_type': 'int',
                'required': False,
            },
            {
                'name': 'output_dataset_name',
                'display_name': 'Output dataset name',
                'data_type': 'str',
                'required': False,
            }
        ]
    },
    {
        'name': 'ConvertDicomToNifti',
        'display_name': 'Convert a single DICOM series to single NIFTI',
        'class_path': 'app.tasks.dcm2nifti.task.DicomToNiftiTaskJob',
        'parameters': [
            {
                'name': 'input',
                'display_name': 'DICOM series',
                'data_type': 'dataset',
                'required': True,
            },
            {
                'name': 'series',
                'display_name': 'Treat DICOM files as single series',
                'data_type': 'bool',
                'required': False,
                'default_value': True,
            },
            {
                'name': 'output_dataset_name',
                'display_name': 'Output dataset name',
                'data_type': 'str',
                'required': False,
            }
        ]
    },
    {
        'name': 'ConvertTagToDicom',
        'display_name': 'Convert TAG files to DICOM format',
        'class_path': 'app.tasks.tag2dcm.task.TagToDicomTaskJob',
        'parameters': [
            {
                'name': 'input',
                'display_name': 'DICOM and TAG files',
                'data_type': 'dataset',
                'required': True,
            },
            {
                'name': 'output_dataset_name',
                'display_name': 'Output dataset name',
                'data_type': 'str',
                'required': False,
            },
        ]
    },
    {
        'name': 'TotalSegmentator',
        'display_name': 'Automatically segment 104 structures in a CT scan',
        'class_path': 'app.tasks.totalsegmentator.task.TotalSegmentatorTaskJob',
        'parameters': [
            {
                'name': 'input',
                'display_name': 'Flat file list for single DICOM series or single NIFTI file',
                'data_type': 'dataset',
                'required': True,
            },
            {
                'name': 'fast',
                'display_name': 'Generate low-res segmentations (if no GPU available)',
                'data_type': 'bool',
                'required': False,
            },
            {
                'name': 'statistics',
                'display_name': 'Generate statistics (volume and mean HU)',
                'data_type': 'bool',
                'required': False,
            },
            {
                'name': 'radiomics',
                'display_name': 'Generate radiomics features (requires pyradiomics)',
                'data_type': 'bool',
                'required': False,
            },
            {
                'name': 'output_dataset_name',
                'display_name': 'Output dataset name',
                'data_type': 'str',
                'required': False,
            },
        ]
    },
    {
        'name': 'ConvertDpcaExportToCastorImport',
        'display_name': 'Convert Castor DPCA export to CSVs that can be imported into Castor',
        'class_path': 'app.tasks.castor.dpca_new.ConvertDpcaExportToCastorImportTaskJob',
        'parameters': [
            {
                'name': 'dpca_export_file',
                'display_name': 'DPCA export CSV file',
                'data_type': 'dataset',
                'required': True,
            },
            {
                'name': 'castor_dpca_export_file',
                'display_name': 'Latest Castor export CSV file',
                'data_type': 'dataset',
                'required': True,
            },
            {
                'name': 'date_columns',
                'display_name': 'Date columns',
                'data_type': 'list',
                'required': True,
                'default_value': 'gebdat,behperdat,verwijsdat,beelddat,draindat,cythistdat,datpreopmdo,neoadjdat,datok,reintvdat,datdrainverw,palliadat,adjudat,datont,datcom',
            },
            {
                'name': 'starting_record_nr',
                'display_name': 'Starting record number',
                'data_type': 'int',
                'required': True,
            },
            {
                'name': 'output_dataset_name',
                'display_name': 'Output dataset name',
                'data_type': 'str',
                'required': False,
            }
        ]
    },
]
