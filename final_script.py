"""
Script om NDVI waardes van gebied Voedselbos Schijndel te berekenen door Sentinel2 Data en een csv + een grafiek te maken van de ontwikkeling hiervan.

Gemaakt door Sjoerd Wolbert.
HAS Hogeschool.
20-01-2024

Input:
    - DATA_FOLDER: 
        String.
        Folder waar de Sentinel2 banden worden opgeslagen.
    - OUTPUT_FOLDER: 
        String.
        Folder waar de NDVI grafiek wordt opgeslagen.
    - SCIHUB_USERNAME:
        String.
        Username voor scihub.copernicus.eu om sentinel2 banden te downloaden.
    - SCIHUB_PW:
        String. 
        Password voor scihub.copernicus.eu om sentinel2 banden te downloaden.
    - FROM_DATE:
        String.
        Begindatum van tijdsinterval.
        Formaat: yyyymmdd.
    - TO_DATE: 
        String. 
        Einddatum van tijdsinterval.
        Formaat: yyyymmdd.
    - MAX_CLOUD_COVER:
        Int/Float tussen 0 en 100.
        Maximum toegestaande hoeveelheid bewolking in procent.
 
Algorithme:
    - Download Sentinel2 banden van dagen met geschikte cloudcover
    - Vind alle .tif files die band 4 zijn in data folder
    - Voor elke band 4 file:
        - Vind de band 8 file voor hetzelfde dag
        - Maak een NDVI kaart voor het hele beeld
        - Bereken de NDVI waarde van gebied voedselbos
        - Voeg NDVI waarde toe aan lijst van NDVI waardes
    - Maak csv met formaat 'datum;NDVI' en sla op
    - Maak een grafiek met op de x-as alle dagen binnen de tijdsinterval, en op de y-as de NDVI waarde
    - Sla grafiek op

Helpers:
    - def get_band4_and_band8_files(dict_path):
        Gets band 4 and band8 files from dict.
        Input: Path to dictionary containing sattelite data
        Output: 2 lists containing band4 files and band8 files respectively

    - def get_NDVI_beelden(list_band4, list_band8):
        Creates NDVI images from band4 and band8 files.
        Input: 2 lists containing band4 files and band8 files respectively
        Output: A list containing paths to files of NDVI images made from band4 and band8
        Side effect: Creates NDVI images in data folder
    
    - def get_NDVI_waardes(list_NDVI_images):
        Gets NDVI value within specific coordinates from NDVI_image.
        Input: List of NDVI image files
        Output: A list containing NDVI values for each NDVI image

    - def get_datum_from_file(file):
        Gets the date from a file.
        Input: File in format <ID van tile\>_<ID van orbit\>_<datum tijd\>_<nummer van band\>_<locatie\>.tif
        Output: String of datum

    - def get_NDVI_datums(list_NDVI_images):
        Gets the dates from NDVI files.
        Input: list of NDVI files
        Output: list of dates in format yyyymmdd

    - def write_to_csv(list_NDVI_waardes, list_datums, output_folder):
        Writes data to csv file.
        input: A list containing NDVI waardes, A list containing date's of NDVI recording, folder to put csv in
        Output: Nothing
        Side effect: Writes values to csv in the format 'datum;NDVI'

    - def create_graph(list_NDVI_waardes, list_datums, folder_path):
        Creates a graph using pyplot of NDVI Waardes and NDVI datums.
        Input: A list containing NDVI waardes, A list containing date's of NDVI recording
        Output: Nothing
        Side effect: Creates the graph, saves graph to folder_path
"""
#Import modules
from datetime import datetime as time
import voedselbos_functies as voedselb
import os
import csv
from matplotlib import pyplot as plt

#Inputs:
DATA_FOLDER = r"D:\Desktop\Studie AGIS\AGIS - Jaar 2\Blok 2\Python-script\Final script\Data"
OUTPUT_FOLDER = r"D:\Desktop\Studie AGIS\AGIS - Jaar 2\Blok 2\Python-script\Final script\Output"
SCIHUB_USERNAME = 'Sjoerd'
SCIHUB_PW = ''
FROM_DATE = ''
TO_DATE = ''
MAX_CLOUD_COVER = 10

os.chdir(DATA_FOLDER)

#Functies/Helpers:
def get_band4_and_band8_files(dict_path):
    """
    Gets band 4 and band8 files from dict.

    Input: Path to dictionary containing sattelite data.

    Output: 2 lists containing band4 files and band8 files respectively.
    """
    band4_files = []
    band8_files = []
    folder_inhoud = os.listdir(dict_path)

    for bestand in folder_inhoud:
        if os.path.splitext(bestand)[1] == '.tif':
            tif_file_metadata = bestand.split('_') 
            if tif_file_metadata[2] == 'B04':
                band4 = bestand
                band8 = bestand.replace('B04', 'B08')
                band4_files.append(band4)
                band8_files.append(band8)
    return band4_files, band8_files


def get_NDVI_beelden(band4_list, band8_list):
    """
    Creates NDVI images from band4 and band8 files.

    Input: 2 lists containing band4 files and band8 files respectively.

    Output: A list containing paths to files of NDVI images made from band4 and band8.

    Side effect: Creates NDVI images in data folder.
    """
    NDVI_beelden_list = []

    for i in range(len(band4_list)):
        band4_path = os.path.abspath(band4_list[i])
        band8_path = os.path.abspath(band8_list[i])
        NDVI_beeld = voedselb.calculate_ndvi(band4_path, band8_path)
        NDVI_beelden_list.append(NDVI_beeld)
    
    return NDVI_beelden_list

def get_NDVI_waardes(list_NDVI_images):
    """
    Gets NDVI value within specific coordinates from NDVI_image.

    Input: List of NDVI image files.

    Output: A list containing NDVI values for each NDVI image.
    """
    NDVI_waardes = []
    X_COOR = 670323
    Y_COOR = 5722626

    for NDVI_image in list_NDVI_images:
        NDVI = voedselb.get_value_from_raster(NDVI_image, X_COOR, Y_COOR)
        NDVI_waardes.append(NDVI)
    return NDVI_waardes

def get_datum_from_file(input_file):
    """
    Gets the date from a file.

    Input: File in format <ID tile>_<ID van orbit>_<datum tijd>_<nummer van band>_<locatie>.tif

    Output: String of datum in format yyyymmdd.
    """
    file_name = os.path.basename(input_file)
    file_metadata = file_name.split('_')
    file_datum = file_metadata[1].split('T')[0]
    return file_datum

def get_NDVI_datums(list_NDVI_images):
    """
    Gets the dates from NDVI files.

    Input: list of NDVI files.

    Output: list of dates in format yyyymmdd.
    """
    NDVI_datums = []

    for NDVI_image in list_NDVI_images:
        NDVI_datum = get_datum_from_file(NDVI_image)
        NDVI_datums.append(NDVI_datum)
    return NDVI_datums


def write_to_csv(list_NDVI_waardes, list_datums, output_folder):
    """
    Writes data to csv file.

    input: A list containing NDVI waardes, A list containing date's of NDVI recording, folder to put csv in.

    Output: Nothing.

    Side effect: Writes values to csv in the format 'datum;NDVI'.
    """

    CSV = output_folder + '\\NDVI_waardes.csv'

    with open(CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        for i in range(len(list_NDVI_waardes)):
            row = [str(list_datums[i]) + ';' + str(list_NDVI_waardes[i])]
            writer.writerow(row)

def create_graph(list_NDVI_waardes, list_datums, folder_path):
    """
    Creates a graph using pyplot of NDVI Waardes and NDVI datums.

    Input: A list containing NDVI waardes, A list containing date's of NDVI recording, folder to store graph in.

    Output: Nothing.

    Side effect: Creates the graph, saves graph to folder_path.
    """
    #Convert list_datums naar list of datetime objects
    list_datetime = []
    for datum in list_datums:
        datetime_datum = time.strptime(datum, r'%Y%m%d')
        list_datetime.append(datetime_datum)
    #Maak grafiek
    plt.plot(list_datetime, list_NDVI_waardes)
    plt.xlabel('Datum')
    plt.ylabel('NDVI Waarde')
    plt.title('Ontwikkeling NDVI Waarde van Voedselbos Schijndel')
    plt.savefig(OUTPUT_FOLDER + '\\NDVI_Figuur.png')
    plt.show()


if __name__ == '__main__':
    # voedselb.download_images(
    #     SCIHUB_USERNAME,
    #     SCIHUB_PW,
    #     DATA_FOLDER,
    #     FROM_DATE,
    #     TO_DATE,
    #     MAX_CLOUD_COVER
    #     )
    
    band4_list, band8_list = get_band4_and_band8_files(DATA_FOLDER)

    NDVI_beelden = get_NDVI_beelden(band4_list, band8_list)

    NDVI_waardes = get_NDVI_waardes(NDVI_beelden)

    NDVI_datums = get_NDVI_datums(NDVI_beelden)

    write_to_csv(NDVI_waardes, NDVI_datums, OUTPUT_FOLDER)

    create_graph(NDVI_waardes, NDVI_datums, OUTPUT_FOLDER)