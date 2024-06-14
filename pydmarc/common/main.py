from pydmarc.common.graph import Graph
import pydmarc.common.dir as dir
from pydmarc.data.db import SQLDriver
from pydmarc.common.intel import Intel
from pydmarc.common.log import logger
from pydmarc.abuseipdb.abuseipdb import AbuseIPDB

class middleware:
    ## cli.py
    async def _display_folder_options(graph: Graph):
        dmarc_folder = await graph.get_dmarc_folder_id()
        logger.info("Dmarc Folder Options")
        logger.info("Folder Name - {}".format(dmarc_folder['folder_name']))
        logger.info("Emails - {}".format(dmarc_folder['folder_messages_total']))
        return dmarc_folder
    
    ## cli.py
    async def _download_attachments(graph: Graph, idfolder, messages_length):
        if (messages_length < 999):
            token = await graph.get_app_only_token()
            messages = await graph.get_all_list_messages_from_folder(idfolder)
            await graph.get_attachments(messages,token)
        if (messages_length > 999 and messages_length < 2000):
            week = 2
            messages = await graph._internal_get_custom_messages_from_folder(idfolder, week, messages_length)
            token = await graph.get_app_only_token()
            await graph.get_attachments(messages,token)
        
    ## cli.py 
    async def _download_custom_time_attachments(graph: Graph, hours, idfolder):
        messages = await graph.get_custom_messages_from_folder(idfolder,hours=hours)
        logger.info("Messages Info")
        logger.info("Time selected - {}".format(hours))
        logger.info("Messages count - {}".format(len(messages)))
        token = await graph.get_app_only_token()
        await graph.get_attachments(messages,token)


    async def _write_sql_database():
        # Extrai os arquivos xml 
        logger.info("Preparing to extract files")
        meta = dir.extract_xml_files()
        
        # Algoritmo sobre DMARC
        intel: Intel = Intel(meta)
        logger.info("Verifing compliance rules about SPF, DKIM and DMARC")
        intel.check_spf_and_dmarc_status()
        
        # Verifica se IP está no AbuseIPDB
        # abuseIPDB: AbuseIPDB = AbuseIPDB(meta)
        # logger.info("Verifing if ip Address is in AbuseIPDB database")
        # meta_abuseIPDB = await abuseIPDB.consult_abuse_ipdb_database()
        
        # Escreve no banco de dados o relatorio de Dmarc
        sql: SQLDriver = SQLDriver()
        logger.info("Preparing to write data in DmarcRecords database")
        sql.write_sql_database_dmarc(meta)
        
        # Escreve no banco de dados os relatório do AbuseIPDB
        # logger.info("Preparing to write data in AbuseIPDBRecords database")
        # sql.write_sql_database_abuseipdb(meta_abuseIPDB)
        
        # Remove os arquivos baixados
        logger.info("Removing all attachments")
        dir.remove_attachments()
        
    async def _write_to_csv(output_file):
        # Extrai os arquivos xml 
        meta = dir.extract_xml_files()
        
        # Algoritmo sobre DMARC
        intel: Intel = Intel(meta)
        intel.check_spf_and_dmarc_status()
        
        # Escreve no banco de dados
        sql: SQLDriver = SQLDriver()
        sql.write_csv_report(meta,output_file)
        
        # Remove os arquivos baixados
        dir.remove_attachments()