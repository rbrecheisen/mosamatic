import typer
from core import controller


app = typer.Typer()


@app.command()
def check_dicom(image_dir: str = typer.Argument(help='Directory containing the DICOM images')):
    """
    Checks whether the DICOM images are 512 by 512 pixels. If not, a new directory will be 
    created (inside image_dir) that contains the images that are not 512 by 512 pixels. These
    images you will have to rescale using the rescale_dicom command (see cli.py rescale_dicom --help)
    """
    controller.check_dicom()


@app.command()
def rescale_dicom(image_dir: str = typer.Argument(help='Directory containing the DICOM images')):
    """
    Rescales the DICOM images to 512 by 512 pixels. This may cause the anatomy visible on the image
    to be reduced in size causing some loss of resolution (detail). For further processing (segmentation
    of muscle and fat regions and calculation of body composition metrics) this may only have a small 
    effect.
    """
    controller.rescale_dicom()


@app.command()
def segment_muscle_and_fat(
    image_dir: str = typer.Argument(help='Directory containing the DICOM images'),
    save_to_png: bool = typer.Argument(True, help='Whether to save each segmentation to a PNG image')
    ):
    """
    Automatically annotates muscle and fat regions in the DICOM image and (optionally) saves the 
    annotation to a PNG image for easy visual checking.
    """
    controller.segment_muscle_and_fat()


@app.command()
def calculate_body_composition_metrics(
    image_dir: str = typer.Argument(help='Directory containing the DICOM images'),
    segmentation_dir: str = typer.Argument(help='Directory containing the muscle and fat segmentations'),
    heights_file: str = typer.Argument(None, help='CSV file containing patient heights in mm^2')
    ):
    """
    Calculates body composition metrics for all images in image_dir. The segmenations in segmentation_dir
    are used to limit the calculation to only muscle and fat regions. Optionally, a CSV file can be 
    specified containing patient heights in mm^2. The format should be <file name>, <height>.
    """
    controller.calculate_body_composition_metrics()


if __name__ == '__main__':
    app()