
#### powershell.exe -ExecutionPolicy Bypass -File .\agentWindows.ps1

$SRV_PROTOCLE="http"
$SRV_IP="172.16.3.20"
$SRV_PORT="80"


$OSInfo = Get-WmiObject Win32_OperatingSystem | Select-Object Caption, Version, CSName

$NomOS=$OSInfo.Caption
$VersionOs=$OSInfo.Version
$Hostname=$OSInfo.CSName

## Recup ip info 
$interfaceID=(Get-NetRoute | Where-Object -FilterScript {$_.NextHop -Ne "::"} | Where-Object -FilterScript { $_.NextHop -Ne "0.0.0.0" } | Where-Object -FilterScript { ($_.NextHop.SubString(0,6) -Ne "fe80::") } | Get-NetAdapter).ifIndex


$IP=(Get-NetIPAddress -InterfaceIndex $interfaceID -AddressFamily IPv4).IPAddress
$MAC=(Get-NetAdapter -ifIndex $interfaceID).MacAddress

$stringAsStream = [System.IO.MemoryStream]::new()
$writer = [System.IO.StreamWriter]::new($stringAsStream)
$writer.write($Hostname+"."+$MAC+"."+$IDENTIFIER)
$writer.Flush()
$stringAsStream.Position = 0
$IDENTIFIER=(Get-FileHash -InputStream $stringAsStream -Algorithm MD5).Hash
$ID_INFRA={{infra_id}}

$template='
{
  "id_infrastructure" : "'+$ID_INFRA+'",
  "IDENTIFIER" : "'+$IDENTIFIER+'",
  "IP" : "'+$IP+'",
  "Hostname" : "'+$Hostname+'",
  "OS" : {
    "Nom_OS" : "'+$NomOS+'",
    "VersionOS" : "'+$versionOS+'"
  },
  "Application" :
        [
            {
            "Nom_Application" : "",
            "Version_Application" : ""
            }'

## Récupération plus complète (M2I)
# Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |  Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | sort-object -property DisplayName | Format-Table –AutoSize
# Get-ItemProperty HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* |  Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | sort-object -property DisplayName | Format-Table –AutoSize


Get-WmiObject win32_product  | Select-Object Name,Version |  sort-object -property Name | ForEach-Object -Process {
    $nameAPP = $_.Name
    $VersionAPP = $_.Version
    
    $template = $template + ',{
            "Nom_Application" : "'+$nameApp+'",
            "Version_Application" : "'+$versionApp+'"
        }'
}
$template=$template+"]}"

$template

Invoke-WebRequest -Uri $SRV_PROTOCLE"://"$SRV_IP":"$SRV_PORT"/api/v1/update" -Method Post -Body $template -ContentType "application/json; charset=utf-8"
