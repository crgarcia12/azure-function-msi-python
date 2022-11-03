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
        connectionString = os.environ['DBCONNECTIONSTRING'] #crgar-paas-pythonmsi-sqlserver.database.windows.net'
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
