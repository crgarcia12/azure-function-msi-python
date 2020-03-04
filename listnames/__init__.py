import logging

import azure.functions as func

# Managed Service Identity (MSI) packages
from msrestazure.azure_active_directory import MSIAuthentication
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient

# Sql driver
import pyodbc

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    
    # server = '<server>.database.windows.net'
    # database = '<database>'
    # username = '<username>'
    # password = '<password>'
    # driver= '{ODBC Driver 17 for SQL Server}'
    # 'DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password
    connectionString = 'Driver={ODBC Driver 13 for SQL Server};Server=tcp:crgar-paas-msi-python-server.database.windows.net,1433;Database=crgar-paas-msi-python-db;Uid=sqladminuser;Pwd=P@ssword123123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    cnxn = pyodbc.connect(connectionString)
    cursor = cnxn.curso
    r()
    cursor.execute("Select * From Names")
    row = cursor.fetchone()

    allNames=""
    while row:
        allNames += str(row[0]) + ", "
        row = cursor.fetchone()

    return func.HttpResponse(f"Hello {allNames}!")



# token = b"eyJ0eXAiOi...";
# exptoken = b"";
# for i in token:
#     exptoken += bytes({i});
#     exptoken += bytes(1);
# tokenstruct = struct.pack("=i", len(exptoken)) + exptoken;
# conn = pyodbc.connect(connstr, attrs_before = { 1256:tokenstruct });