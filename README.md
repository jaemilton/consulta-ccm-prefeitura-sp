# Consulta CCM Prefeitura SP

Este projeto é uma ferramenta automatizada para consultar informações do Cadastro de Contribuintes Mobiliários (CCM) da Prefeitura de São Paulo. Utiliza Selenium para automação web, resolução de CAPTCHA via API do Anti-Captcha, e gera relatórios em PDF e CSV sobre códigos de tributos e isenções.

## Descrição

O script `consulta-ccm-prefeitura-sp.py` lê uma lista de CPFs de um arquivo CSV, acessa o sistema CCM da Prefeitura de SP, resolve CAPTCHAs automaticamente, verifica códigos de tributos associados a cada CPF e determina se há isenções aplicáveis. Os resultados são salvos em arquivos CSV e PDFs individuais para cada consulta.

### Funcionalidades Principais

- **Processamento em Lote**: Processa múltiplos CPFs de um arquivo CSV.
- **Resolução Automática de CAPTCHA**: Utiliza a API do Anti-Captcha para resolver CAPTCHAs de imagem.
- **Verificação de Tributos**: Extrai códigos de tributos e verifica isenções específicas (5720, 3980, 3166, 2836, 5754, 5311).
- **Geração de Relatórios**: Cria PDFs das fichas de dados cadastrais e um CSV consolidado com resultados.
- **Tratamento de Cenários Diversos**: Lida com contribuintes registrados, não registrados, múltiplos CCMs, etc.
- **Continuação de Processamento**: Mantém um registro de CPFs já processados para retomar execuções interrompidas.

## Pré-requisitos

- **Python 3.8+**: Certifique-se de ter o Python instalado.
- **Google Chrome**: O script utiliza o ChromeDriver para automação.
- **Conta Anti-Captcha**: Necessária para resolução de CAPTCHAs. Obtenha uma chave API em [anti-captcha.com](https://anti-captcha.com/).
- **wkhtmltopdf**: Incluído no projeto (pasta `wkhtmltox`), mas certifique-se de que está acessível.

## Instalação

1. **Clone ou Baixe o Repositório**:
   ```
   git clone https://github.com/seu-usuario/consulta-ccm-prefeitura-sp.git
   cd consulta-ccm-prefeitura-sp
   ```

2. **Crie um Ambiente Virtual** (Recomendado):
   ```
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as Dependências**:
   ```
   pip install -r requirements.txt
   ```

4. **Configure o ChromeDriver**:
   - Baixe a versão compatível com seu Chrome em [chromedriver.chromium.org](https://chromedriver.chromium.org/downloads).
   - Coloque o `chromedriver.exe` no PATH do sistema ou na pasta do projeto.

5. **Configure Variáveis de Ambiente**:
   - Crie um arquivo `.env` na raiz do projeto com:
     ```
     ANTI_CAPTCHA_API_KEY=sua_chave_api_aqui
     PDF_OUTPUT_DIR=./pdfs
     ```
   - Substitua `sua_chave_api_aqui` pela sua chave da API Anti-Captcha.

## Configuração

- **Arquivo de CPFs**: Prepare um arquivo `cpfs.csv` com uma coluna de CPFs (somente números, sem formatação). Exemplo:
  ```
  12345678901
  98765432100
  ```

- **Diretório de Saída**: Configure `PDF_OUTPUT_DIR` no `.env` para onde salvar os PDFs (padrão: `./pdfs`).

- **Códigos de Isenção**: Os códigos isentos são hardcoded no script: `[5720, 3980, 3166, 2836, 5754, 5311]`. Modifique se necessário.

## Uso

1. **Prepare os Arquivos**:
   - Certifique-se de que `cpfs.csv` está na raiz do projeto.
   - Configure o `.env` conforme descrito.

2. **Execute o Script**:
   ```
   python consulta-ccm-prefeitura-sp.py
   ```

3. **Monitoramento**:
   - O script exibirá o progresso no console, incluindo status de login, resolução de CAPTCHA e extração de dados.
   - Em caso de erro ou CAPTCHA inválido, o script tentará novamente automaticamente.

4. **Interrupção e Retomada**:
   - O script cria um arquivo `{data}_processed_cpfs.txt` para rastrear CPFs processados.
   - Se interrompido, execute novamente para continuar do ponto onde parou.

## Saída

- **CSV de Resultados**: `{data}-resultados_consultas.csv` com colunas:
  - `cpf`: CPF formatado.
  - `codigos_de_tributos_encontrados`: Lista de códigos separados por `;`.
  - `encontrou_codigo_isento`: `True` se encontrou código isento, senão `False`.

- **PDFs Individuais**: Um PDF por CPF em `{PDF_OUTPUT_DIR}`, contendo a ficha de dados cadastrais.

- **Log de Processados**: `{data}_processed_cpfs.txt` com lista de CPFs já consultados.

## Troubleshooting

- **Erro de ChromeDriver**: Certifique-se de que a versão do ChromeDriver corresponde à do seu Chrome. Atualize se necessário.

- **CAPTCHA Não Resolvido**: Verifique sua chave API Anti-Captcha e saldo. O script tenta novamente em caso de falha.

- **Elemento Não Encontrado**: O site pode ter mudado. Verifique seletores XPath/CSS no código e atualize conforme necessário.

- **Erro de PDF**: Certifique-se de que `wkhtmltopdf.exe` está no PATH ou no local especificado no script.

- **Timeout**: Aumente timeouts no código se a conexão for lenta.

- **Múltiplas Execuções**: O script pula CPFs já processados, mas certifique-se de não executar simultaneamente.

## Segurança e Ética

- Este script é para fins educacionais e de automação pessoal. Não use para atividades ilegais ou sobrecarga de servidores públicos.
- Respeite os termos de serviço do site da Prefeitura de SP e da API Anti-Captcha.
- Mantenha suas chaves API seguras e não as compartilhe.

## Contribuição

Contribuições são bem-vindas! Abra issues para bugs ou sugestões, e pull requests para melhorias.

## Licença

Este projeto é distribuído sob a licença MIT. Veja `LICENSE` para detalhes.</content>
<parameter name="filePath">README.md