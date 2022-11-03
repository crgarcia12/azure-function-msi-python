import logging
import os
import azure.functions as func

# Sql driver
import pyodbc

def main(req: func.HttpRequest) -> func.HttpResponse:

    version = 'V17'
    try:
        logging.info(f"[{version}] Python HTTP trigger function processed a request.")
  
        # Connecting to Azure SQl the standard way
        server = os.environ['SERVERNAME'] #crgar-paas-pythonmsi-sqlserver.database.windows.net'
        authentication = os.environ['AUTHENTICATION'] #ActiveDirectoryMsi
        database =  os.environ['DATABASENAME']
        driver = '{ODBC Driver 17 for SQL Server}'

        connectionString = (
            "Driver=" + driver
            + ";Server=tcp:" + server
            + ";PORT=1433;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=10"
            + ";Database=" + database
            + ";Authentication=" + authentication
        )

        logging.info('Authentication: ' + authentication)
        logging.info('Server: ' + server)
        logging.info('Database: ' + database)
        logging.info('ConnectionString: ' + connectionString)

        with pyodbc.connect(connectionString) as conn:
            logging.info("Successful connection to database")

            with conn.cursor() as cursor:
                #Sample select query
                cursor.execute("SELECT TOP 3 [Name] FROM [dbo].[people]") 

                peopleNames = ''
                row = cursor.fetchone() 
                while row: 
                    peopleNames += str(row[0]).strip() + " " 
                    row = cursor.fetchone()

                return func.HttpResponse(f"[{version}] Hello {peopleNames}!")
    except Exception as e:
        return func.HttpResponse(f"[{version}] " + str(e) + f" | connection string: {connectionString}")
