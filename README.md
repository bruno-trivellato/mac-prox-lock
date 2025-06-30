# Mac Proximity Lock

🔒 Bloqueia automaticamente seu MacBook quando seu smartphone Android se afasta dele.

## Como Funciona

O sistema monitora continuamente a conexão Bluetooth com seu dispositivo Android (Samsung A53). Quando o smartphone se afasta por mais de 30 segundos (configurável), o MacBook é automaticamente bloqueado.

## Requisitos

- macOS (testado no M4)
- Python 3.6+
- Dispositivo Android pareado via Bluetooth
- Permissões para executar comandos do sistema

## Pré-requisitos: Conectar seu Android no Mac via Bluetooth

Antes de instalar o sistema, você precisa parear seu Samsung A53 com o MacBook:

### 1. No seu Android (Samsung A53):
1. Vá em **Configurações** → **Conexões** → **Bluetooth**
2. Certifique-se que o Bluetooth está **ligado**
3. Toque em **Tornar dispositivo detectável** ou similar
4. Mantenha a tela aberta nesta seção

### 2. No seu MacBook:
1. Clique no ícone da **Apple** → **Configurações do Sistema**
2. Vá em **Bluetooth** na barra lateral
3. Certifique-se que o Bluetooth está **ligado**
4. Você deve ver seu "SM-A536B" (ou similar) na lista de dispositivos próximos
5. Clique em **Conectar** ao lado do seu dispositivo
6. Confirme o código que aparece nas duas telas (se solicitado)

### 3. Verificar a conexão:
1. No Mac: O dispositivo deve aparecer como "Conectado" na lista
2. No Android: Deve mostrar "Conectado ao [Nome do seu Mac]"

### 4. Teste rápido:
```bash
# Clone o projeto primeiro, depois execute:
python3 main.py --list-devices
```

Você deve ver seu Samsung A53 listado como um dispositivo conectado.

## Instalação Rápida

1. **Clone e instale:**
```bash
git clone <repository-url>
cd mac-prox-lock
chmod +x install.sh
./install.sh
```

2. **Configure seu dispositivo:**
```bash
python3 main.py --setup
```

3. **Teste o funcionamento:**
```bash
python3 main.py
```

## Uso

### Configuração Inicial

Execute o setup interativo para configurar seu dispositivo Android:
```bash
python3 main.py --setup
```

O script irá:
- Escanear dispositivos Bluetooth pareados
- Permitir selecionar seu Samsung A53
- Configurar timeout e intervalo de verificação

### Executar Manualmente

Para testar o sistema manualmente:
```bash
python3 main.py
```

### Executar como Serviço em Background

Para que o sistema funcione automaticamente sempre que você ligar o Mac:

**Iniciar serviço:**
```bash
launchctl load ~/Library/LaunchAgents/com.proximity.lock.plist
```

**Parar serviço:**
```bash
launchctl unload ~/Library/LaunchAgents/com.proximity.lock.plist
```

### Comandos Úteis

**Listar dispositivos Bluetooth:**
```bash
python3 main.py --list-devices
```

**Ver logs:**
```bash
tail -f proximity_lock.log
```

**Ajuda com Bluetooth:**
```bash
# Verificar status do Bluetooth
./bluetooth_helper.sh status

# Conectar manualmente ao dispositivo
./bluetooth_helper.sh connect 60:68:4E:E1:61:71

# Resetar Bluetooth se tiver problemas
./bluetooth_helper.sh reset
```

## Configuração

O arquivo `config.json` é criado automaticamente com as seguintes opções:

```json
{
  "device_name": "SM-A536B",
  "device_mac": "AA:BB:CC:DD:EE:FF", 
  "timeout_seconds": 30,
  "scan_interval": 5,
  "log_level": "INFO",
  "lock_command": "pmset displaysleepnow"
}
```

### Parâmetros Configuráveis

- **device_name**: Nome do seu dispositivo Android
- **device_mac**: Endereço MAC do dispositivo (mais confiável)
- **timeout_seconds**: Segundos para bloquear após perder conexão (padrão: 30)
- **scan_interval**: Intervalo entre verificações em segundos (padrão: 5)
- **log_level**: Nível de log (DEBUG, INFO, WARNING, ERROR)
- **lock_command**: Comando para bloquear a tela
- **auto_reconnect**: Tentar reconectar automaticamente (padrão: true)
- **max_reconnect_attempts**: Tentativas de reconexão antes de desistir (padrão: 3)
- **reconnect_delay**: Delay entre tentativas em segundos (padrão: 2)

## Troubleshooting

### Problemas de Bluetooth

**Dispositivo não aparece na lista:**
1. Certifique-se que o Bluetooth está ligado no Mac e no Android
2. No Android: Vá em Bluetooth → **Avançado** → marque "Tornar detectável"
3. No Mac: Tente remover e parear novamente o dispositivo
4. Reinicie o Bluetooth nos dois dispositivos
5. Execute `python3 main.py --list-devices` para verificar

**Dispositivo pareado mas não conecta:**
1. No Android: Vá em Bluetooth → encontre seu Mac → **Desparear**
2. No Mac: Bluetooth → encontre seu Android → **Remover**  
3. Refaça o processo de pareamento do zero
4. Alguns Androids precisam que você aceite todas as permissões de compartilhamento

**Conexão instável:**
1. Mantenha os dispositivos próximos (< 2 metros) durante o teste
2. Evite interferências (outros dispositivos Bluetooth, Wi-Fi 2.4GHz)
3. No Android: Desative "Otimização de bateria" para Bluetooth
4. Ajuste o `scan_interval` no config para valores maiores (ex: 10 segundos)

**Mac não reconecta automaticamente ao Android:**
1. **Use o helper script**: `./bluetooth_helper.sh connect 60:68:4E:E1:61:71`
2. **Reset do Bluetooth**: `./bluetooth_helper.sh reset` (pode precisar de sudo)
3. **Configuração do Android**:
   - Vá em Bluetooth → Configurações Avançadas
   - Habilite "Conectar automaticamente a dispositivos conhecidos"
   - Desative "Timeout de conexão"
4. **No macOS**: 
   - Preferências → Bluetooth → Opções Avançadas
   - Habilite "Allow Bluetooth devices to wake this computer"
5. **O sistema agora tem reconexão automática integrada** - ele tentará reconectar até 3 vezes

### Dispositivo não encontrado pelo script
1. Certifique-se que o dispositivo está **conectado** (não apenas pareado)
2. Execute `python3 main.py --list-devices` para ver todos os dispositivos
3. Verifique se o nome/MAC address no config.json está correto
4. Tente usar o MAC address em vez do nome do dispositivo

### Não está bloqueando
1. Verifique os logs: `tail -f proximity_lock.log`
2. Teste o comando de bloqueio manualmente: `pmset displaysleepnow`
3. Ajuste o timeout se necessário

### Serviço não inicia automaticamente
1. Verifique se o arquivo plist foi criado: `ls ~/Library/LaunchAgents/com.proximity.lock.plist`
2. Recarregue o serviço: `launchctl unload` seguido de `launchctl load`

## Segurança

- O sistema usa apenas APIs públicas do macOS
- Não coleta ou transmite dados pessoais
- Funciona completamente offline
- Logs são armazenados localmente

## Desinstalação

Para remover completamente o sistema:

```bash
# Parar o serviço
launchctl unload ~/Library/LaunchAgents/com.proximity.lock.plist

# Remover arquivos
rm ~/Library/LaunchAgents/com.proximity.lock.plist
rm -rf ~/path/to/mac-prox-lock
```

## Contribuição

Sinta-se à vontade para reportar bugs, sugerir melhorias ou contribuir com código!

## Resumo: Fluxo Completo do Zero

Aqui está o passo a passo completo para configurar tudo do zero:

### 1. Preparar o Bluetooth (PRIMEIRO PASSO!)
- Android: Configurações → Bluetooth → Ligar → Tornar detectável
- Mac: Configurações → Bluetooth → Ligar → Conectar ao seu Samsung A53
- Confirmar que aparece "Conectado" nos dois dispositivos

### 2. Instalar o Sistema
```bash
# Clonar o projeto
git clone <repository-url>
cd mac-prox-lock

# Executar instalação
./install.sh
```

### 3. Configurar o Dispositivo
```bash
# Executar setup interativo
python3 main.py --setup

# Escolher seu Samsung A53 da lista
# Definir timeout (recomendado: 30 segundos)
```

### 4. Testar o Funcionamento
```bash
# Testar manualmente
python3 main.py

# Afastar o celular e ver se bloqueia após 30s
# Ctrl+C para parar
```

### 5. Ativar o Serviço Automático
```bash
# Iniciar serviço em background
./start_service.sh

# Verificar logs
tail -f proximity_lock.log
```

### 6. Pronto! 🎉
Agora sempre que seu Samsung A53 se afastar do MacBook por mais de 30 segundos, a tela será bloqueada automaticamente.

**Para parar:** `./stop_service.sh`  
**Para desinstalar:** `./uninstall.sh`

## TODO

- [ ] **Fix import e get dando erro de linter** - Resolver warnings do PyObjC import e None.get()
- [ ] **Refatorar script Python com melhor arquitetura** - Separar em classes/módulos menores, melhorar organização

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.