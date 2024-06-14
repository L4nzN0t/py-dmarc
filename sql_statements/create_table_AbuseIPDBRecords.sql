USE DMARC;

CREATE TABLE AbuseIPDBRecords (
    id int identity(1,1) not null primary key,
    ipAddress VARCHAR(60),
    ipPublic VARCHAR(10),
    ipVersion int,
    isWhiteListed VARCHAR(10),
    abuseConfidenceScore int,
    countryCode VARCHAR(10),
    usageType VARCHAR(100),
    isp varchar(200),
    domain VARCHAR(70),
    hostnames VARCHAR(150),
    isTor VARCHAR(10),    
    totalReports int,
    numDistinctUsers int,
    lastReportedAt date
);
