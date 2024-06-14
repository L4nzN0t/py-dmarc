import dns.resolver
import socket
from pydmarc.abuseipdb.abuseipdb import AbuseIPDB

class Intel:
    metadata: dict
    size_meta: int
    resolver = dns.resolver.Resolver()
    spf_sef = []
    
    def __init__(self, metadata):
        self.metadata = metadata
        result = self.resolver.query("fazenda.mg.gov.br", 'TXT')
        for txt_record in result:
            if txt_record.strings and txt_record.strings[0].startswith(b"v=spf1"):
                txt = txt_record.strings[0].decode('utf-8').split(" ")
                for record in txt:
                    if 'ip4' in record and '200.198' in record:
                        self.spf_sef.append(record.split(":")[1])
                    elif 'spf.' in record:
                        self.spf_sef.append(record.split('spf', 1)[-1].strip('.'))
                
    def check_spf_and_dmarc_status(self):
        for meta in self.metadata:
            try:
                fqdn = socket.gethostbyaddr(meta['source_ip'])
                temp_spf = meta['spf']
                temp_dkim = meta['dkim']
                temp_dkim_alignment = meta['dkim_alignment']
                temp_spf_alignment = meta['spf_alignment']
                
                if fqdn[0]:
                    meta['dns_name'] = fqdn[0]
                    if meta['dns_name'] == 'NULL':
                        print(meta['dns_name'])
                    if (temp_spf == 'pass' and temp_spf_alignment == 'pass') or (temp_dkim == 'pass' and temp_dkim_alignment == 'pass'):
                        meta['dmarc_result'] = 'pass'
                    else:
                        meta['dmarc_result'] = 'fail'

                    if temp_spf == 'pass':
                        if any(substring in fqdn[0] for substring in self.spf_sef) or any(subs in meta['source_ip'] for subs in self.spf_sef):
                            meta['status_spf'] = 'OK' # Tudo OK
                        else:
                            meta['status_spf'] = 'Warning' # SPF valido para IP não autorizado. Possível Fraude
                    elif temp_spf == 'fail':
                        if any(substring in fqdn[0] for substring in self.spf_sef) or any(subs in meta['source_ip'] for subs in self.spf_sef):
                            meta['status_spf'] = 'Attention' # Existe um problema com a validação
                        else:
                            meta['status_spf'] = 'OK' # Tudo OK
                    else:
                        meta['status_spf'] = temp_spf
                else:
                    meta['dns_name'] = 'Unknown'
            except Exception as e:
                meta['dns_name'] = 'Unknown'
        