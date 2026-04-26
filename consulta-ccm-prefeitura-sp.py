
#get image from url https://ccm.prefeitura.sp.gov.br/Captcha/GerarCaptcha?v=6d44ae6c27284fb08a2bd1d408434af0
import base64
from logging import config
import os
from anticaptchaofficial.imagecaptcha import *
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import chrome
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.support.ui import Select
from dotenv import load_dotenv
from pathlib import Path 
import pdfkit

def write_resultado_to_csv(date_today: list, resultado: dict):
    with open(f'{date_today}-resultados_consultas.csv', mode='a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['cpf', 'codigos_de_tributos_encontrados', 'encontrou_codigo_isento']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writerow({
            'cpf': resultado['cpf'],
            'codigos_de_tributos_encontrados': ";".join(map(str, resultado['codigos_de_tributos_encontrados'])),
            'encontrou_codigo_isento': resultado['encontrou_codigo_isento']
        })

def get_select_options(driver: WebDriver) -> Select:
    # 1. Locate the <select> element
    select_element = driver.find_element(By.ID, "ddlCcm") # Use your locator (ID, Name, XPath, etc.)

    # 2. Create a Select object
    return Select(select_element)

def check_fdc_ccm(driver: WebDriver, pdf_output_path: str):
    # 1. Find the shadow host element first
    child_element = driver.find_element(By.XPATH, "//span[normalize-space()='Código(s) de tributo(s)']")
    while True:
        # Navigate up one level from the <tr> (might be a <tbody> or <thead>)
        parent_element = child_element.find_element(By.XPATH, "..")

        if parent_element is None:
            break
        # Check the tag name of the parent to determine if it's the table
        if parent_element.tag_name == "table":
            parent_table = parent_element
            print("Found the parent table directly.")
            break
        else:
            child_element = parent_element
            print(f"Navigating up, current tag: {child_element.tag_name}")
    
    
    if parent_table is None:
        print("Could not find the parent table.")
        # continue
        return
    
    # 2. Iterate through rows and columns using Selenium locators
    # This method is more robust for dynamic or complex tables where you need
    # to interact with elements inside cells (like links or buttons)
    table_data = []
    # Find all rows (tr elements) within the table body (tbody)
    rows = parent_table.find_elements(By.TAG_NAME, "tr")

    for row in rows:
        # Find all data cells (td elements) or header cells (th elements) in the current row
        cells = row.find_elements(By.TAG_NAME, "td")
        if not cells: # Check for header rows if needed
            cells = row.find_elements(By.TAG_NAME, "th")
            
        row_data = [cell.text for cell in cells]
        table_data.append(row_data)

    codigos_de_tributos_encontrados = []
    for row in table_data:
        if len(row) > 0 and row[0].strip() != "":
            if (row[0].strip().isdigit()):
                codigos_de_tributos_encontrados.append(int(row[0].strip()))

    # Print or process the extracted data
    print("Extraindo Códigos de Tributos:")
    for codigo in codigos_de_tributos_encontrados:
        print(codigo)

    codigos_servicos_isentos = [5720,3980,3166,2836,5754,5311]

    encontrou_codigo_isento = False
    # boolean_isento = any(codigo in codigos_de_tributos for codigo in codigos_servicos_isentos)
    for codigo in codigos_de_tributos_encontrados:
        if codigo in codigos_servicos_isentos:
            print(f"Código de tributo {codigo} encontra-se isento.")
            encontrou_codigo_isento = True
        else:
            print(f"Código de tributo {codigo} não encontra-se isento.")

    print_page_and_append_result(driver, 
                                codigos_de_tributos_encontrados, 
                                encontrou_codigo_isento, 
                                pdf_output_path)

def print_page_and_append_result(driver: WebDriver, codigos_de_tributos_encontrados: list, encontrou_codigo_isento: bool, pdf_output_path: str):
     # JavaScript to find all 'img' tags and remove them
    js_script = """
    const images = document.querySelectorAll('img');
    images.forEach(img => img.remove());
    """

    # Execute the script
    driver.execute_script(js_script)
    
    #salva html da página como pdf usando selenium
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "container"))
    )
    
    html_content = element.get_attribute('outerHTML').replace('\n', '').replace('\r', '')

    pdfkit.from_string(html_content, pdf_output_path, configuration=config, options=options)
    
    resuldado = {
        "cpf": formatted_cpf,
        "codigos_de_tributos_encontrados": codigos_de_tributos_encontrados,
        "encontrou_codigo_isento": encontrou_codigo_isento
    }
    write_resultado_to_csv(date_today, resuldado)

# Load .env file
load_dotenv()

PDF_OUTPUT_DIR = os.getenv('PDF_OUTPUT_DIR')
Path(PDF_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Define paths (adjust for your installation and file locations)
PATH_WKHTMLTOPDF = r'.\\wkhtmltox\\bin\\wkhtmltopdf.exe' # Use a raw string for path

# Create a configuration object pointing to the wkhtmltopdf executable
config = pdfkit.configuration(wkhtmltopdf=PATH_WKHTMLTOPDF)


# --- PDF generation options (explicitly set encoding) ---
options = {
    'encoding': 'UTF-8',
    'enable-local-file-access': True # Needed for local CSS/images if using from_string or from_file
}


def check_if_element_exists(driver: WebDriver | ShadowRoot, by, value):
    try:
        driver.find_element(by, value)
        return True
    except Exception as e:
        return False


api_key =  os.getenv("ANTI_CAPTCHA_API_KEY")
from selenium.webdriver.common.by import By

driver: WebDriver = WebDriver()
driver.get("https://ccm.prefeitura.sp.gov.br/login/contribuinte?tipo=F")
assert "Acesso ao Sistema" in driver.title
# elem = driver.find_element(By.CSS_SELECTOR, "input.cc__button__autorizacao--all")

# 1. Find the shadow host element first
shadow_host = driver.find_element(By.CSS_SELECTOR, "prodamsp-componente-consentimento")

# 2. Get the shadow root
# Use the shadow_root property in Python (or get_shadow_root() method in other languages)
shadow_root: ShadowRoot = shadow_host.shadow_root 

# wait for the button to be present in the shadow DOM
wait = WebDriverWait(driver, 10)
#wait "input[type='button'].cc__button__autorizacao--all"
try:
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='button'].cc__button__autorizacao--all")))
except TimeoutException:
    print("Button not found in shadow DOM after waiting.")
    pass

if check_if_element_exists(shadow_root, By.CSS_SELECTOR, "input[type='button'].cc__button__autorizacao--all"):
    shadow_root.find_element(By.CSS_SELECTOR, "input[type='button'].cc__button__autorizacao--all").click()

#read csv file with csv and get the first cpf value
cpf_list = []
import csv
with open('cpfs.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        #remove non-numeric characters from the cpf value
        cleaned_cpf = row[0].strip().replace('.', '').replace('-', '')
        cpf_list.append(cleaned_cpf)


date_time_now_with_hours = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
date_today = datetime.now().strftime("%Y-%m-%d")

# read the list of already processed cpfs from a file and skip them
processed_cpfs = set()
if os.path.exists(f'{date_today}_processed_cpfs.txt'):
    with open(f'{date_today}_processed_cpfs.txt', 'r') as f:
        for line in f:
            processed_cpfs.add(line.strip())

total_cpfs = len(cpf_list)
counter_cpfs_checked = 0
for cpf in cpf_list:
    counter_cpfs_checked += 1
    if cpf in processed_cpfs:
        print(f"Skipping ({counter_cpfs_checked}/{total_cpfs}) CPF: {cpf}")
        continue
    
    print(f"Processing ({counter_cpfs_checked}/{total_cpfs}) CPF: {cpf}")
    while True:

        # get image from img tag with id "imgCaptcha"
        img_element = driver.find_element(By.CSS_SELECTOR, "#imgCaptcha")
        # Get the screenshot as a Base64 string
        base64_image_string = img_element.screenshot_as_base64
        #save the image to a file
        image_path = "captcha_image.png"
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(base64_image_string))

        solver = imagecaptcha()
        solver.set_verbose(1)
        solver.set_key(api_key)
        captcha_text: str = solver.solve_and_return_solution(image_path)
        print(f"Solved Captcha: {captcha_text}")
        
        if len(str(captcha_text)) != 4:
            print("Captcha solution is not 4 characters long, retrying...")
            driver.get("https://ccm.prefeitura.sp.gov.br/login/contribuinte?tipo=F")
            continue

        # Wait for the alert to be present
        wait = WebDriverWait(driver, 3)
    
        driver.find_element(By.CSS_SELECTOR, "#input-usuario").send_keys(cpf)
        driver.find_element(By.CSS_SELECTOR, "#input-captcha").send_keys(captcha_text.lower())
        driver.find_element(By.CSS_SELECTOR, "#btnEntrar").click()
        try:
            alert = wait.until(EC.alert_is_present())
            alert.accept()
        except TimeoutException:
            pass

        if check_if_element_exists(driver, By.XPATH, "//div[@class='form-group has-error']//span[@class='input-group-addon']"):
            continue
        else:
            break

    wait.until
    (
        EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='Emissão da Ficha de Dados Cadastrais - FDC']")) or 
        EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='Protocolos devolvidos, recusados ou cancelados']"))
    )

    if check_if_element_exists(driver, By.XPATH, "//span[normalize-space()='Emissão da Ficha de Dados Cadastrais - FDC']"):
        print("Login successful, FDC option is available.")
    elif check_if_element_exists(driver, By.XPATH,"//span[normalize-space()='Protocolos devolvidos, recusados ou cancelados']") and \
    check_if_element_exists(driver, By.XPATH,"//a[normalize-space()='Prosseguir']"):
        driver.find_element(By.XPATH, "//a[normalize-space()='Prosseguir']").click()

        
    # //span[normalize-space()='Código(s) de tributo(s)']
    formatted_cpf = cpf[:3] + "." + cpf[3:6] + "." + cpf[6:9] + "-" + cpf[9:]
    if check_if_element_exists(driver, By.XPATH, "//p[contains(text(),'A Prefeitura do Município de São Paulo (PMSP) info')]") and \
    check_if_element_exists(driver, By.XPATH, "//p[contains(text(),'não consta da base de dados do Cadastro de Contribuintes Mobiliários (CCM)')]"):
        print("Login successful, but the taxpayer is not registered in the CCM database.")
    elif check_if_element_exists(driver, By.XPATH,"//td[contains(text(),'Protocolo de inscrição extinto:')]") and \
    check_if_element_exists(driver, By.XPATH,"//a[normalize-space()='Prosseguir']"):
        print("Login successful, and the taxpayer is registered in the CCM database.")
        driver.find_element(By.XPATH, "//a[normalize-space()='Prosseguir']").click()
    elif check_if_element_exists(driver, By.XPATH,"//b[normalize-space()='Prefeitura do Município de São Paulo']") and \
        check_if_element_exists(driver, By.XPATH,"//span[normalize-space()='Secretaria Municipal da Fazenda']") and \
        check_if_element_exists(driver, By.XPATH,"//span[normalize-space()='Departamento de Cadastros']") and \
        check_if_element_exists(driver, By.XPATH,f"//span[normalize-space()='CPF: {formatted_cpf}']") and \
        check_if_element_exists(driver, By.XPATH,"//span[normalize-space()='Código(s) de tributo(s)']"): 

        try:
            check_fdc_ccm(driver, f'{PDF_OUTPUT_DIR}/{date_today}_{counter_cpfs_checked}_{cpf}.pdf')
        except Exception as e:
            print(f"Could not find the table: {e}")
            continue
        
        
    elif ((
            check_if_element_exists(driver, By.XPATH  ,"//b[normalize-space()='Prefeitura do Município de São Paulo']") and \
            check_if_element_exists(driver, By.XPATH  ,"//p[contains(text(),'FDC - Ficha de dados cadastrais')]") and \
            check_if_element_exists(driver, By.CSS_SELECTOR,"#btmImprimiFdc")
        ) or \
        check_if_element_exists(driver, By.CSS_SELECTOR,"#btnImprimiPessoaNotFind")):
        
        print(f"Login successful, CPF: {formatted_cpf}")
        print_page_and_append_result(driver, 
                                     [], 
                                     False, 
                                     f'{PDF_OUTPUT_DIR}/{date_today}_{counter_cpfs_checked}_{cpf}.pdf')
    
    elif check_if_element_exists(driver, By.XPATH,"//span[normalize-space()='Escolha o número do CCM:']") and \
        check_if_element_exists(driver, By.XPATH,"//button[@id='btnEmitirCcm']") and \
        check_if_element_exists(driver, By.XPATH,"//select[@id='ddlCcm']"):
        
        select = get_select_options(driver)

        # 3. Get all options and print their visible text
        all_options = select.options
        options_text_and_values = [(option.text, option.get_attribute('value')) for option in all_options[1:]]  # Skip the first option if it's a placeholder
        
        print("All available options:")
        for (option_text, option_value) in options_text_and_values:
            print(f"Text: {option_text}, Value: {option_value}")
            if "- Cancelado - " not in option_text.strip():
                select.select_by_value(option_value)
                driver.find_element(By.ID, "btnEmitirCcm").click()
                
                try:
                    check_fdc_ccm(driver, f'{PDF_OUTPUT_DIR}/{date_today}_{counter_cpfs_checked}-{option_value}-{cpf}.pdf')
                    driver.find_element(By.XPATH, "//a[normalize-space()='Voltar']").click()
                    #re-select the select element after going back to the previous page
                    select = get_select_options(driver)
                    
                except Exception as e:
                    print(f"Could not find the table: {e}")
                    continue
    
    else:
        
        print("Login NOT successful, but the taxpayer's registration status is unclear.")    
        resuldado = {
            "cpf": formatted_cpf,
            "codigos_de_tributos_encontrados": [],
            "encontrou_codigo_isento": False
        }
        write_resultado_to_csv(date_today, resuldado)
        # resuldado_consultas.append(resuldado)
    
    # add checked cpf to a list of processed cpfs and save it to a file
    with open(f'{date_today}_processed_cpfs.txt', 'a') as f:
        f.write(cpf + '\n')
        
    driver.get("https://ccm.prefeitura.sp.gov.br/login/contribuinte?tipo=F")


resuldado_consultas = []
#load resultados das consultas from csv file
with open(f'{date_today}-resultados_consultas.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        resuldado_consultas.append({
            "cpf": row['cpf'],
            "codigos_de_tributos_encontrados": row['codigos_de_tributos_encontrados'].split(";") if row['codigos_de_tributos_encontrados'] else [],
            "encontrou_codigo_isento": row['encontrou_codigo_isento'] == 'True'
        })


# Print the results of all consultations
print("\nResultados das Consultas:")    
for resultado in resuldado_consultas:
    print(f"CPF: {resultado['cpf']}")
    print(f"Códigos de Tributos Encontrados: {resultado['codigos_de_tributos_encontrados']}")
    print(f"Encontrou Código Isento: {resultado['encontrou_codigo_isento']}")
    print("-" * 40)
    
#criar csv com os resultados das consultas
# import csv


# with open(f'{date_time_now_with_hours}-resultados_consultas.csv', mode='w', newline='', encoding='utf-8') as csvfile:
#     fieldnames = ['cpf', 'codigos_de_tributos_encontrados', 'encontrou_codigo_isento']
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#     writer.writeheader()
#     for resultado in resuldado_consultas:
#         writer.writerow({
#             'cpf': resultado['cpf'],
#             'codigos_de_tributos_encontrados': ";".join(map(str, resultado['codigos_de_tributos_encontrados'])),
#             'encontrou_codigo_isento': resultado['encontrou_codigo_isento']
#         })

driver.close()


