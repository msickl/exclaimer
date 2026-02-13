# Run this script always as Administrator
[CMDLetBinding()]
param(
    [Switch]$fullsync = $false
)

$configPath = Join-Path -Path $PSScriptRoot -ChildPath 'config.json'
$config = Get-Content -Path $configPath -Raw | ConvertFrom-Json

function main()
{
    if($fullsync)
    {
        Write-Host "INFO: FullSync enabled" -ForegroundColor Gray
    } else {
        Write-Host "INFO: FullSync disabled" -ForegroundColor Gray
    }

    Write-Host "DOWNLOAD: Data from ActiveDirectory"

    $users = @()
    Get-ADUser -Filter * -Properties * | % {
        
        # Convert the Current User Sid to MD5 Hash
        $md5 = [System.Security.Cryptography.MD5]::Create()
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($_.SID)
        $hash = $md5.ComputeHash($bytes)
        $md5sid = [BitConverter]::ToString($hash) -replace "-", ""

        $user = @{
            "objectsid" = $md5sid
            "samaccountname" = $_.sAMAccountName
	        "firstname" = $_.GivenName
	        "lastname" = $_.sn
		    "company" = $_.Company
		    "officephone" = $_.telephoneNumber
		    "mobilephone" = $_.mobile
		    "email" = $_.mail
		    "website" = $_.HomePage
		    "city" = $_.City
		    "postalcode" = $_.PostalCode
		    "fax" = $_.facsimileTelephoneNumber
		    "title" = $_.Initials
		    "position" = $_.Title
	        "department" = $_.Department
		    "street" = $_.StreetAddress
		    "country" = $_.Country
		    "region" = $_.State
            "usnchanged" = $_.usnChanged
            "modifiedon" = $_.whenChanged.ToString("yyyy-MM-ddTHH:mm:ssZ")
            "enabled" = $_.Enabled
            "employeeid" = $_.employeeNumber
            "suffixtitle" = $_.suffixTitle
            "prefixtitle" = $_.prefixTitle
        }

        $users += $user
    }

    $data = $users | ConvertTo-Json -Compress
	
    $headers = @{
        "Authorization" = "Bearer: $($config.token)"
    }

    Write-Host "INFO: Upload ActiveDirectory" -ForegroundColor Magenta
    try {
        $url = "$($config.protocol)://$($config.server):$($config.port)/api/users?fullsync=$($fullsync)"
        Write-Host "UPLOAD: Data to $($url)"

        $res = Invoke-WebRequest -Headers $headers -Uri $url -ContentType "application/json; charset=utf-8" -Method POST -Body $data -TimeoutSec 5 -ErrorAction Stop
		if($res)
        {
            Write-Host "SUCCESS: Upload complete." -ForegroundColor Green
        }
    } 
    catch
    {
        Write-Host "ERROR: An error occurred: $_" -ForegroundColor Red
        send-mail -body "$($_)" -from $config.smtp.from -to $config.smtp.to -subject "ERROR: Agent OnPremise ActiveDirectory to Exclaimer synchronisation failed"
    }
}

function send-mail
{
    [CMDLetBinding()]
    param ( 
        [Parameter(Mandatory=$true)]
        [System.String]$body,
        [Parameter(Mandatory=$true)]
        [System.String]$from,
        [Parameter(Mandatory=$true)]
        [System.Object]$to,
        [Parameter(Mandatory=$true)]
        [System.String]$subject
    )

    $srv = $config.smtp.server
    $client = new-object Net.Mail.SmtpClient($srv)
    $msg = new-object Net.Mail.MailMessage

    $msg.From = $from

    foreach($rec in $to)
    {
        $msg.To.Add($rec.toString())
        write-host "Sent Email to $($rec.ToString())"
    }
    
    $msg.Subject = $subject
    $msg.IsBodyHtml = $true
    $msg.Body = $body

    $client.Send($msg)
    
}

main