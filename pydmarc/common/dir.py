import zipfile
import gzip
import os
import pandas as pd
from pydmarc.common.dmarcparser import DmarcParser
from pydmarc.common.log import logger
from pydmarc.common import ATTACHMENTS_FOLDER

dmarcparser: DmarcParser = DmarcParser()

directory_compressed_files = ATTACHMENTS_FOLDER
METADATA = []
METADATA.clear()

def _check_existence_dir():
    if os.path.isdir(directory_compressed_files):
        return True
    else:
        return False


def extract_xml_files():
    if _check_existence_dir():
        compressed_files = os.listdir(directory_compressed_files)
        logger.info("{} Files encountered".format(len(compressed_files)))
    else:
        logger.debug("There's no folder to save attachments")
        try:
            os.mkdir(directory_compressed_files)
            logger.debug("{} - Folder created".format(directory_compressed_files))
            compressed_files = os.listdir(directory_compressed_files)
            logger.info("{} Files encountered".format(len(compressed_files)))
        except Exception as e:
            logger.error("Folder wasn't created")
            logger.error(e)
    
    for file in compressed_files:
        file_path = directory_compressed_files + file
        try: 
            if file.lower().endswith(".zip"):
                with zipfile.ZipFile(file_path, 'r') as archive:
                    byte_stream = archive.read(archive.namelist()[0])
                    content = byte_stream.decode('utf-8')
                    meta = dmarcparser.get_meta(content)
                    if type(meta) is list:
                        for m in meta:
                            METADATA.append(m)
                    elif type(meta) is dict:
                        if meta is None:
                            continue
                        if (len(meta)) < 1:
                            METADATA.append(meta)    
                        else:
                            for i_meta in range(len(meta)):
                                METADATA.append(meta[i_meta])
                    logger.info("Parsed dmarc file - {}".format(file))
                        
            elif file.lower().endswith(".gz"):
                with gzip.GzipFile(file_path, 'r') as archive:
                    byte_stream = archive.read()
                    content = byte_stream.decode('utf-8')
                    meta = dmarcparser.get_meta(content)
                    if type(meta) is list:
                        for m in meta:
                            METADATA.append(m)
                    elif type(meta) is dict:
                        if meta is None:
                            continue
                        if (len(meta)) < 1:
                            METADATA.append(meta)    
                        else:
                            for i_meta in range(len(meta)):
                                METADATA.append(meta[i_meta])
                        logger.info("Parsed dmarc file - {}".format(file))
        except zipfile.BadZipFile as ez:
            logger.critical(ez)
            continue
    return _clean_metadata(METADATA)


def _clean_metadata(_metadata):
    try:
        df = pd.DataFrame(_metadata[0], index=[0])
        for i in range(len(_metadata)):
            df = pd.concat([df, pd.DataFrame(_metadata[i], index=[i])])
        logger.info("Total rows = {}".format(len(df)))
        logger.info("Removing duplicate entries...")
        df_unique = df.drop_duplicates(subset=['org_name', 'email', 'report_id', 'source_ip', 'envelop_from', 'header_from'], keep='first', inplace=False, ignore_index=False)
        logger.info("Total unique rows = {}".format(len(df_unique)))
        _new_metadata = []
        for i in df_unique.index:
            _new_metadata.append(df_unique.loc[i].to_dict())
    except Exception as e:
        logger.critical(e)
        print(e)
        
    return _new_metadata
    
        
def remove_attachments():
    if _check_existence_dir():
        compressed_files = os.listdir(directory_compressed_files)

    for f in compressed_files:
        try:
            full_file_path = os.path.join(directory_compressed_files,f)
            if os.path.isfile(full_file_path):
                os.remove(full_file_path)
                logger.debug("{} - File removed".format(full_file_path))
        except Exception as e:
            logger.error(e)
            print(e)