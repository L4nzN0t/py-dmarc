import pyodbc
import base64
import pandas as pd
import sqlalchemy
from urllib import parse
import pydmarc.common
from pydmarc.common.log import logger
from pydmarc.abuseipdb.abuseipdb import AbuseIPDB

class SQLDriver:
    engine: sqlalchemy
    
    def __init__(self):
        try:
            pydmarc.common.config.read(pydmarc.common.CONFIG_FILE)
            sql_settings = pydmarc.common.config['SQL']

            server = sql_settings['server']
            db = sql_settings['database']
            username = sql_settings['username']
            token = sql_settings['token']
            port = sql_settings['port']
            encryption = sql_settings['encryption']
            trustcert = sql_settings['TrustServerCertificate']
            timeout = sql_settings['timeout']

            # melhorar
            token_bytes = token.encode("ascii")
            passw = base64.b64decode(token_bytes)
            passw = passw.decode('utf-8')
            # melhorar 

            params = parse.quote_plus \
            ('Driver={ODBC Driver 18 for SQL Server};Server='+server+','+port+';Database='+db+';Uid='+username+';Pwd='+passw+';Encrypt='+encryption+ \
                ';TrustServerCertificate='+trustcert+';Connection Timeout='+timeout+';')
            conn_str="mssql+pyodbc:///?odbc_connect={}".format(params)
            self.engine = sqlalchemy.create_engine(conn_str,echo=True)
            logger.info("SQL Connection Engine created")
        except pyodbc.Error as ex:
            logger.critical(ex)
            print(ex)
        except Exception as e:
            logger.critical(e)
            print(e)
        
    def write_sql_database_dmarc(self,meta):
        try:
            df = pd.DataFrame(meta)
            result = df.to_sql("DmarcRecords", con=self.engine, schema='dbo', if_exists='append',index=False)
            logger.info("Records saved in SQL Database (DmarcRecords)")
            logger.debug(result)
        except Exception as e:
            logger.critical(e)
            print(e)
    
    def write_sql_database_abuseipdb(self,meta):
        try:
            df = pd.DataFrame(meta)
            result = df.to_sql("AbuseIPDBRecords", con=self.engine, schema='dbo', if_exists='append',index=False)
            logger.info("Records saved in SQL Database (AbuseIPDBRecords)")
            logger.debug(result)
        except Exception as e:
            logger.critical(e)
            print(e)

    def write_csv_report(meta, *dirs):
        try:
            if dirs[0]:
                filename = dirs[0]
            df = pd.DataFrame(meta)
            df.to_csv(filename, index=False, encoding="UTF-8")
            logger.info("Csv Report saved in {}".format(filename))
        except Exception as e:
            logger.error(e)
            print(e)

            