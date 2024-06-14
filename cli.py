import argparse
import asyncio
import pydmarc.common
from pydmarc.common.main import middleware
from pydmarc.common.graph import Graph
from pydmarc.common.log import logger
import os

__version__ = '1.0.0'

logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
logger.info("py_dmarc started")
logger.info("py_dmarc v{}".format(__version__))

async def _main():
    parser = argparse.ArgumentParser(description="Just a example", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--download", action='store_true', required=False, help="Download Dmarc attachments from Graph API. Up to 999 messages")
    parser.add_argument("-t", "--time", required=False, help="Get attachments of mail folder from Graph API during the specific time (hours). Use '--all' to get all messages")
    parser.add_argument("--all", action='store_true',required=False, help="Get all attachments of mail folder from Graph API. Use '--all' to get all messages")
    parser.add_argument("-o", "--output", required=False, help="Export the result. Default format: csv")
    parser.add_argument("-idb", "--insert-database", action='store_true', required=False, help="Write data into database. Config file needed")
    parser.add_argument("-c", "--config", required=False, help="Write data into database. Config file needed")
    args = parser.parse_args()

    try:
        if pydmarc.common._check_config_file_present():
            pydmarc.common.CONFIG_FILE = '{}\\config.cfg'.format(pydmarc.common.WORKSPACE)
            logger.info("Configuration file set - {}".format(pydmarc.common.CONFIG_FILE))
        else:
            if args.config:
                if os.path.isfile(args.config) and args.config.endswith('\\config.cfg'):
                    pydmarc.common.CONFIG_FILE = args.config
                    logger.info("Configuration file set - {}".format(pydmarc.common.CONFIG_FILE))
                else:
                    raise Exception("No configuration file found.\nCheck if name is 'config.cfg'.")
            else:
                raise Exception("No configuration file found.\nUse --config.")
    except Exception as e:
        print(e)
        logger.error(e)
        exit()
    
    
    try:
        pydmarc.common.config.read(pydmarc.common.CONFIG_FILE)
        azure_settings = pydmarc.common.config['Azure']
        
        # Inicia a classe Graph
        graph: Graph = Graph(azure_settings)
    except Exception as e:
        logger.error(e)
    
    
    async def folder_details():
        folder_info = await middleware._display_folder_options(graph)
        logger.info("Dmarc Folder options - {}".format(folder_info))
        return folder_info
    
    try:
        if args.time and args.all:
            raise Exception("You can't use parameters --all and --time together.\nFor more explanation type --help.")
        if args.insert_database:
            if args.time or args.all or args.download or args.output:
                raise Exception("Parameter --insert-database must be used alone.")
            else:
                await middleware._write_sql_database()
        elif args.download or args.output:
            if args.time and args.all:
                raise Exception("You can't use parameters --all and --time together.\nFor more explanation type --help.")
            elif args.time or args.all:
                if args.time:
                    if int(args.time) < 169:
                        if args.download:
                            folder_info = await folder_details()
                            await middleware._download_custom_time_attachments(graph, int(args.time), folder_info['folder_id'])
                        elif args.output:
                            open(args.output, 'w').close()
                            folder_info = await folder_details()
                            await middleware._download_custom_time_attachments(graph, int(args.time), folder_info['folder_id'])
                            await middleware._write_to_csv(args.output)
                        else:
                            raise Exception("The path isn't valid.")
                    else:
                        raise Exception("Time period can't be greater than 168 hours")
                elif args.all:
                    if args.download:
                        folder_info = await folder_details()
                        await middleware._download_attachments(graph, folder_info['folder_id'], folder_info['folder_messages_total'])
                    elif args.output:
                        if args.output.endswith('.csv'):
                            open(args.output, 'w').close()
                            folder_info = await folder_details()
                            await middleware._download_attachments(graph, folder_info['folder_id'], folder_info['folder_messages_total'])
                            await middleware._write_to_csv(args.output)
                        else:
                            raise Exception("The path isn't valid.")
            else:
                raise Exception("You must specifiy a time period. (e.g '--time 24' or '--all')")
        else:
            raise Exception("You must specifiy an action. (e.g --output or --download or --insert-database)")
    except Exception as e:
        logger.error(e)
        print(e)
   
        

if __name__ == '__main__':
    asyncio.run(_main())