Set-Location $HOME

# Instala componente para suporte a container no Windows
Install-WindowsFeature -Name Containers

# Faz o download do script de instalação do Docker para Windows Server (https://learn.microsoft.com/en-us/virtualization/windowscontainers/quick-start/set-up-environment?tabs=dockerce#windows-server-1)
Invoke-WebRequest -UseBasicParsing "https://raw.githubusercontent.com/microsoft/Windows-Containers/Main/helpful_tools/Install-DockerCE/install-docker-ce.ps1" -OutFile install-docker-ce.ps1
.\install-docker-ce.ps1

if (-not (Test-Path -Path "$Env:ProgramFiles\Docker\"))
{
    mkdir "$Env:ProgramFiles\Docker"
}
# Faz o download do binario do docker-compose para o Windows
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Start-BitsTransfer -Source "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-windows-x86_64.exe" -Destination $Env:ProgramFiles\Docker\docker-compose.exe

# Verifica se a pasta de instalação do docker-compose foi adicionada no PATH
[System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\scripts", "Machine")
[System.Environment]::GetEnvironmentVariable("Path", "Machine") -split ";"

# Reinicia o computador
shutdown /r /t 300
