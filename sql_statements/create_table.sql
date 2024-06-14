USE DMARC;

CREATE TABLE DmarcRecords (
	id int identity(1,1) not null primary key,
	org_name varchar(50),
	email varchar(100),
	extra_contact_info varchar(500),
	report_id varchar(500),
	date_range_begin date,
	date_range_end date,
	domain varchar(50),
	adkim varchar(5),
	aspf varchar(5),
	p varchar(5),
	pct varchar(10),
	status_spf varchar(20),
	dns_name varchar(250),
	source_ip varchar(50),
	dkim varchar(10),
	dkim_domain_result varchar(100),
	spf varchar(10),
	spf_domain_result varchar(100),
	envelop_from varchar(100),
	header_from varchar(100),
	dkim_aligment varchar(20),
	spf_aligment varchar(20),
	dmarc_result varchar(10)
);
GO;