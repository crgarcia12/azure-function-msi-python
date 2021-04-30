import logging
import azure.functions as func

# Sql driver
import pyodbc

def main(req: func.HttpRequest) -> func.HttpResponse:

    try:

        logging.info('Python HTTP trigger function processed a request.')

        # Connecting to Azure SQl the standard way
        server = 'tcp:crgar-paas-msi-python-sqlserver.database.windows.net' 
        database = 'crgar-paas-msi-python-db' 
        driver = '{ODBC Driver 17 for SQL Server}'

        with pyodbc.connect(
            "Driver="
            + driver
            + ";Server="
            + server
            + ";PORT=1433;Database="
            + database
            + ";Authentication=ActiveDirectoryMsi",
        ) as conn:

            logging.info("Successful connection to database")

            with conn.cursor() as cursor:
                #Sample select query
                cursor.execute("SELECT Name FROM People;") 

                peopleNames = ''
                row = cursor.fetchone() 
                while row: 
                    peopleNames += str(row[0]).strip() + " " 
                    row = cursor.fetchone()

                return func.HttpResponse(f"Hello {peopleNames}!")
    except Exception as e:
        return func.HttpResponse(str(e))
