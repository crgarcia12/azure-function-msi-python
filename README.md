# Connecting Python Azure Functions to Azure SQL with Managed Identities (MSI)
This repo is an example on how you can connect your Python 3.9 Azure Function to Azure Sql using System Managed Identities instead of Username&Password.

For that you need to create an Azure Function with runtime Python 3.9, a SQL DB with the demo DB, and then execute the following steps


## 1. Enable MSI in your AzFunction:
This is really simple to do. Rememeber the Object ID (number 4) as we will need it later
<img src="docs/1-function-enable-msi.png" width="70%" height="70%">

## 2. Enable AAD in your DB:
We need to do two things:
1. Enable AAD admin in the server
1. Add the Function MSI User to the specific DB

### 2.1 Enable AAD admin in the server
In here you need to add your user (for example, the one you are using to access the portal) as an admin of the DB
This has two purposes: Add AAD integration to the DB, and set the user that will grant permissions to the MSI inside the DB
![db-aad-integration](docs/2-db-aad-integration.png)


### 2.2 Add the Function MSI User to the specific DB

First we need the MSI identity user display name.
That value is usually the Azure Function name, but if you are not sure you can get it by using PowerShell:

```PowerShell
Install-Module AzureAD
Connect-AzureAD

# Take object Id from the first image of this tutorial 
Get-AzureADObjectByObjectId -ObjectIds "<object-id>"

# You will get a result like this one:
ObjectId AppId DisplayName
-------- ----- -----------
...      ...   <MSI user display name> # <- you will need it in the next step

```

Now, we need to connect to the DB using the AAD Admin we have set before:

<img src="docs/3-sql-login-using-aad-part1.png" width="50%" height="50%">
<img src="docs/4-sql-login-using-aad-part2.png" width="50%" height="50%">

We are ready to add the MSI user to the DB. For that we run this query

```sql
CREATE USER "<MSI user display name>" FROM EXTERNAL PROVIDER;
ALTER ROLE db_datareader ADD MEMBER "<MSI user display name>" -- grant permission to read to database
ALTER ROLE db_datawriter ADD MEMBER "<MSI user display name>" -- grant permission to write to database

```

We are ready to go! Check out the source code of the demo function: https://github.com/crgarcia12/azure-function-msi-python/blob/master/listnames/__init__.py
