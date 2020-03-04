import os
import tempfile
import datetime
import sys
from zeep import Client

client = Client('https://webservices.netsuite.com/wsdl/v2014_2_0/netsuite.wsdl')

FileSearch = client.get_type('ns11:FileSearch')
FileSearchBasic = client.get_type('ns5:FileSearchBasic')
SearchStringField = client.get_type('ns0:SearchStringField')
Record = client.get_type('ns0:RecordRef')
Passport = client.get_type('ns0:Passport')

remote = None
localfile = sys.argv[1]
email = sys.argv[2]
password = sys.argv[3]
account = sys.argv[4]

credentials = Passport(email=email,password=password.replace('"',''),account=account, role="3")
filesearch = FileSearch(basic=FileSearchBasic(name=SearchStringField(searchValue=localfile.split('\\')[-1], operator='is')))

client.service.login(passport=credentials)
response = client.service.search(searchRecord=filesearch)

if response.body.searchResult.status.isSuccess:
    if response.body.searchResult.recordList is not None:
        remote = [{'internalid': file.internalId, 'name':file.name, 'parent':file.folder.name.replace(' : ',os.path.sep)} for file in response.body.searchResult.recordList.record if os.path.join(file.folder.name.replace(' : ',os.path.sep),file.name) == sys.argv[1]]

if len(remote) > 0:
    record = Record(name= remote[0]['name'], internalId=remote[0]['internalid'], type='file')
    response = client.service.get(baseRef=record)
    tmpfile = remote[0]['name']
    with open(os.path.join(tempfile.gettempdir(),tmpfile),'wb+') as  file:
        file.write(response.body.readResponse.record.content)
    file.close()
    print("Temp file:")
    print(os.path.join(tempfile.gettempdir(),tmpfile))