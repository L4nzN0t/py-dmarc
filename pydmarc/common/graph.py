from configparser import SectionProxy
from azure.identity.aio import ClientSecretCredential
from msgraph.graph_service_client import GraphServiceClient
from msgraph.generated.users.item.messages.messages_request_builder import MessagesRequestBuilder
from msgraph.generated.users.item.mail_folders.mail_folders_request_builder import MailFoldersRequestBuilder
from kiota_abstractions.api_error import APIError
from datetime import datetime, timedelta, timezone
from pydmarc.common import ATTACHMENTS_FOLDER
import requests


class Graph:
    settings: SectionProxy
    client_credential: ClientSecretCredential
    app_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        client_secret = self.settings['clientSecret']
        self.userid = self.settings['mailboxUser']
        
        self.client_credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        self.app_client = GraphServiceClient(self.client_credential)
        

    async def get_app_only_token(self):
        graph_scope = "https://graph.microsoft.com/.default"
        access_token = await self.client_credential.get_token(graph_scope)
        return access_token.token
    
    
    async def get_dmarc_folder_id(self):
        query_params = MailFoldersRequestBuilder.MailFoldersRequestBuilderGetQueryParameters(
            include_hidden_folders = "true",
            filter = "displayName eq 'DMARC'"
        )
        request_configuration = MailFoldersRequestBuilder.MailFoldersRequestBuilderGetRequestConfiguration(
            query_parameters = query_params,
        )
        dmarc_folder_options = await self.app_client.users.by_user_id(self.userid).mail_folders.get(request_configuration=request_configuration)
        
        if dmarc_folder_options.value[0].display_name == "DMARC":
            dmarc_folder = {
                "folder_name": dmarc_folder_options.value[0].display_name,
                "folder_id": dmarc_folder_options.value[0].id,
                "folder_messages_total": dmarc_folder_options.value[0].total_item_count
            }
        return dmarc_folder
    
    async def get_custom_messages_from_folder(self, idfolder, hours):
        try:
            last_day = datetime.now() - timedelta(hours=hours)
            last_day_utc = last_day.replace(tzinfo=(timezone.utc))
            last_day_utc = last_day_utc.strftime("%Y-%m-%dT%H:%M:%SZ") # Tipo DateTimeOffSet de acordo com a documentação OData https://docs.oasis-open.org/odata/odata/v4.0/errata02/os/complete/part3-csdl/odata-v4.0-errata02-os-part3-csdl-complete.html#_Toc406398065
            
            query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                top = 999,
                filter="receivedDateTime ge {}".format(last_day_utc),
                select = ["id", "createdDateTime", "receivedDateTime", "hasAttachments", "subject", "sender"]                
            )
            request_configuration = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                query_parameters = query_params
            )
            
            client_messages = await self.app_client.users.by_user_id(self.userid).mail_folders.by_mail_folder_id(idfolder).messages.get(request_configuration=request_configuration)
            message_id = {}
            i = 0
            for message in client_messages.value:
                message_id[i] = message.id
                i += 1
            return message_id
        except APIError as e:
            print("Error: {}".format(e))
    
    async def _internal_get_custom_messages_from_folder(self, idfolder, week, messages_length):
        message_id = {}
        try:
            last_day = datetime.now() - timedelta(weeks=week)
            last_day_utc = last_day.replace(tzinfo=(timezone.utc))
            last_day_utc = last_day_utc.strftime("%Y-%m-%dT%H:%M:%SZ") # Tipo DateTimeOffSet de acordo com a documentação OData https://docs.oasis-open.org/odata/odata/v4.0/errata02/os/complete/part3-csdl/odata-v4.0-errata02-os-part3-csdl-complete.html#_Toc406398065
            
            query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                top = 999,
                filter="receivedDateTime gt {}".format(last_day_utc),
                select = ["id", "createdDateTime", "receivedDateTime", "hasAttachments", "subject", "sender"]                
            )
            request_configuration = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                query_parameters = query_params
            )
            client_messages = await self.app_client.users.by_user_id(self.userid).mail_folders.by_mail_folder_id(idfolder).messages.get(request_configuration=request_configuration)
            
            i = 0
            for message in client_messages.value:
                message_id[i] = message.id
                i += 1
            
            condition = True
            while condition:
                if len(client_messages.value) < messages_length:
                    date_now = last_day.replace(tzinfo=(timezone.utc))
                    date_now = date_now.strftime("%Y-%m-%dT%H:%M:%SZ")
                    last_day = last_day - timedelta(weeks=week)
                    last_day_utc = last_day.replace(tzinfo=(timezone.utc))
                    last_day_utc = last_day_utc.strftime("%Y-%m-%dT%H:%M:%SZ") # Tipo DateTimeOffSet de acordo com a documentação OData https://docs.oasis-open.org/odata/odata/v4.0/errata02/os/complete/part3-csdl/odata-v4.0-errata02-os-part3-csdl-complete.html#_Toc406398065
                    
                    query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                        top = 999,
                        filter="receivedDateTime gt {} and receivedDateTime lt {}".format(last_day_utc, date_now),
                        select = ["id", "createdDateTime", "receivedDateTime", "hasAttachments", "subject", "sender"]                
                    )
                    request_configuration = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                        query_parameters = query_params
                    )
                    
                    client_messages = await self.app_client.users.by_user_id(self.userid).mail_folders.by_mail_folder_id(idfolder).messages.get(request_configuration=request_configuration)

                    i = len(message_id)
                    for message in client_messages.value:
                        message_id[i] = message.id
                        i += 1
                
                if len(message_id) >= messages_length:
                    condition = False
                    

            return message_id
        except APIError as e:
            print("Error: {}".format(e))
    
    async def get_all_list_messages_from_folder(self, idfolder):
        try:            
            query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                top = 999,
                select = ["id", "createdDateTime", "receivedDateTime", "hasAttachments", "subject", "sender"]                
            )
            request_configuration = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                query_parameters = query_params
            )
            
            client_messages = await self.app_client.users.by_user_id(self.userid).mail_folders.by_mail_folder_id(idfolder).messages.get(request_configuration=request_configuration)
            message_id = {}
            i = 0
            for message in client_messages.value:
                message_id[i] = message.id
                i += 1
            return message_id
        except APIError as e:
            print("Error: {}".format(e))
                 
    async def get_attachments(self, idmessages, token):           
        try:
            
            for i in idmessages:
                attachments = await self.app_client.users.by_user_id(self.userid).messages.by_message_id(idmessages[i]).attachments.get()
                if len(attachments.value) < 1:
                    request_info = self.app_client.users.by_user_id(self.userid).messages.by_message_id(idmessages[i]).attachments.by_attachment_id(attachments.value[0].id).to_get_request_information()
                else:
                    for x in range(len(attachments.value)):
                        info = await self.app_client.users.by_user_id(self.userid).messages.by_message_id(idmessages[i]).attachments.by_attachment_id(attachments.value[x].id).get()
                        if info.content_type.startswith('application'):
                            request_info = self.app_client.users.by_user_id(self.userid).messages.by_message_id(idmessages[i]).attachments.by_attachment_id(attachments.value[x].id).to_get_request_information()
                            break
                
                request = "https://graph.microsoft.com/v1.0" + request_info.url + "/$value"
                headers = { "Authorization": token }
                stream = requests.get(url=request, headers=headers)
                attach_full_name = ATTACHMENTS_FOLDER + attachments.value[0].name
                with open(attach_full_name, mode="wb") as file:
                    file.write(stream.content)  
                    
                i += 1
                
        except Exception as e:
            print("Error: {}".format(e))
    
