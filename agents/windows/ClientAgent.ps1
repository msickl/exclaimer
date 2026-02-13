$config = @{
    'hostname' = 'intra.zimmer-austria.com'
    'port' = '443'
    'domain' = 'zimmer-austria.com'
}

# Global variables
$srv = "intra.zimmer-austria.com"
$port = 443
$domain = "zimmer-austria.com"
$settings = "HKCU:\Software\Microsoft\Office\16.0\Common\MailSettings"
$profiles = "HKCU:\Software\Microsoft\Office\16.0\Outlook\Profiles"
$signatures = "$($env:APPDATA)\Microsoft\Signatures"
$templatename = "Default"

function main()
{
    # Get User SID from Current User
    $sid = ([System.Security.Principal.WindowsIdentity]::GetCurrent()).User.Value

    # Convert the Current User Sid to MD5 Hash
    $md5 = [System.Security.Cryptography.MD5]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($sid)
    $hash = $md5.ComputeHash($bytes)
    $hashString = [BitConverter]::ToString($hash) -replace "-", ""

    # Convert the MD5 Hash to Base64 String
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($hashString)
    $base64String = [Convert]::ToBase64String($bytes)

    

    $url = "https://$($srv)/ex/template?u=" + $base64String
    
    Write-Host "Request Template $($url)"
    $req = Invoke-WebRequest -Uri $url

    if($req.StatusCode -eq 200)
    {
        # Set Default Signature
        $keys = Get-ChildItem -Recurse -Path "$($profiles)\Outlook"
        foreach($key in $keys)
        {
            $accounts = Get-ItemProperty -Path $key.PSPath -Name "Account Name" -ErrorAction SilentlyContinue
            foreach($account in $accounts)
            {
                if(($account."Account Name").ToLower() -eq "$(($env:USERNAME).ToLower())@$($domain)")
                {
                    Set-ItemProperty -Path $account.PSPath -Name "New Signature" -Value $templatename -Force
                    Set-ItemProperty -Path $account.PSPath -Name "Reply-Forward Signature" -Value $templatename -Force
                }
            }
        }

        # Force Default Signature
        Set-ItemProperty -Path $settings -Name "NewSignature" -Value $templatename -Force
        Set-ItemProperty -Path $settings -Name "ReplySignature" -Value $templatename -Force

        if(-not(Test-Path $signatures))
        {
            New-Item -Path $signatures -ItemType Directory
        }

        $content = Convert-UmlautToHTMLEntity -inputText $req.Content
        Write-Host "Install Template $($templatename)" -ForegroundColor Green
        Set-Content -PassThru "$($signatures)\$($templatename).htm" -Value $content -Force -Encoding UTF8 | Out-Null
    } else {
        Write-Host "Error getting the Template"
    }
}

function FirstRun()
{

}

function Convert-UmlautToHTMLEntity {
    param (
        [string]$inputText
    )
    
    $umlautMap = @{
        [char]0x00E4 = '&auml;'   # ä
        [char]0x00C4 = '&Auml;'   # Ä
        [char]0x00F6 = '&ouml;'   # ö
        [char]0x00D6 = '&Ouml;'   # Ö
        [char]0x00FC = '&uuml;'   # ü
        [char]0x00DC = '&Uuml;'   # Ü
        [char]0x00DF = '&szlig;'  # ß
    }

    foreach ($umlaut in $umlautMap.Keys) {
        $inputText = $inputText -replace [regex]::Escape($umlaut), $umlautMap[$umlaut]
    }
    
    return $inputText
}

main