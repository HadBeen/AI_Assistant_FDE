docker run `
  -e "ACCEPT_EULA=Y" `
  -e "MSSQL_SA_PASSWORD=$env:SQL_ADMIN_PASSWORD" `
  -p 1433:1433 `
  --name legacy-mssql `
  -v mssql_data:/var/opt/mssql `
  -d mcr.microsoft.com/mssql/server:2022-latest