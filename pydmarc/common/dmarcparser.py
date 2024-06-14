import xml.etree.ElementTree as ET
from datetime import datetime

class DmarcParser:

    def get_meta(self, content):
        list_meta_records = []
        
        # get the root element
        xml = ET.fromstring(content)
        
        # '<report_metadata>' tag 
        report_metadata = xml.findall("report_metadata")[0]
        org_name = (report_metadata.findtext("org_name", 'NULL'))
        email = (report_metadata.findtext("email", 'NULL')).replace("<", "").replace(">", "")
        extra_contact_info = (report_metadata.findtext("extra_contact_info", 'NULL'))
        report_id = (report_metadata.findtext("report_id", 'NULL'))
        date_range_begin = (report_metadata.findtext("date_range/begin", 'NULL'))
        if date_range_begin != 'NULL':
            date_range_begin = datetime.fromtimestamp(int(date_range_begin))
        date_range_end = (report_metadata.findtext("date_range/end", 'NULL'))
        if date_range_end != 'NULL':
            date_range_end = datetime.fromtimestamp(int(date_range_end))
        
        
        # '<policy_published>' tag 
        policy_published = xml.findall("policy_published")[0]
        domain = policy_published.findtext("domain", 'NULL')
        adkim = policy_published.findtext("adkim", 'NULL')
        aspf = policy_published.findtext("aspf", 'NULL')
        p = policy_published.findtext("p", 'NULL')
        pct = policy_published.findtext("pct", 'NULL')
            
        dict_meta = {'org_name': org_name, 'email': email, 'extra_contact_info': extra_contact_info, 'report_id': report_id, \
                'date_range_begin': date_range_begin, 'date_range_end': date_range_end, 'domain': domain, 'adkim': adkim, 'aspf': aspf, \
                'p': p, 'pct': pct, 'status_spf': 'NULL', 'dns_name': 'NULL' }
        
        # '<record>' tag 
        record = xml.findall("record")
        if len(record) > 1:
            for i in range(len(record)):
                source_ip = record[i].findtext("row/source_ip", 'NULL')
                dkim = record[i].findtext("auth_results/dkim/result", 'NULL')
                dkim_domain_result = record[i].findtext("auth_results/dkim/domain", 'NULL')
                spf = record[i].findtext("auth_results/spf/result", 'NULL')
                spf_domain_result = record[i].findtext("auth_results/spf/domain", 'NULL')
                envelop_from = record[i].findtext("identifiers/envelope_from", 'NULL')
                header_from = record[i].findtext("identifiers/header_from", 'NULL')
                dkim_alignment = record[0].findtext("row/policy_evaluated/dkim")
                spf_alignment = record[0].findtext("row/policy_evaluated/spf")
                
                dict_meta.update({'source_ip': source_ip, 'dkim': dkim, 'dkim_domain_result': dkim_domain_result, 'spf': spf, \
                    'spf_domain_result': spf_domain_result, 'envelop_from': envelop_from, 'header_from': header_from, \
                        'dkim_alignment': dkim_alignment, 'spf_alignment': spf_alignment, 'dmarc_result': 'NULL'})
                
                list_meta_records.append(dict_meta)
                i = i + 1
        else:
            source_ip = record[0].findtext("row/source_ip", 'NULL')
            dkim = record[0].findtext("auth_results/dkim/result", 'NULL')
            dkim_domain_result = record[0].findtext("auth_results/dkim/domain", 'NULL')
            spf = record[0].findtext("auth_results/spf/result", 'NULL')
            spf_domain_result = record[0].findtext("auth_results/spf/domain", 'NULL')
            envelop_from = record[0].findtext("identifiers/envelope_from", 'NULL')
            header_from = record[0].findtext("identifiers/header_from", 'NULL')
            dkim_alignment = record[0].findtext("row/policy_evaluated/dkim")
            spf_alignment = record[0].findtext("row/policy_evaluated/spf")
            
            dict_meta.update({'source_ip': source_ip, 'dkim': dkim, 'dkim_domain_result': dkim_domain_result, 'spf': spf, \
                    'spf_domain_result': spf_domain_result, 'envelop_from': envelop_from, 'header_from': header_from, \
                        'dkim_alignment': dkim_alignment, 'spf_alignment': spf_alignment, 'dmarc_result': 'NULL'})
            
            list_meta_records.append(dict_meta)
                
        return list_meta_records