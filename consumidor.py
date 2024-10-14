import asyncio
import re
import zipfile
import os
from playwright.async_api import Playwright, async_playwright

async def run(playwright: Playwright) -> None:
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"

    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(user_agent=user_agent)
    page = await context.new_page()

    # Vai para a página de download
    await page.goto("https://consumidor.gov.br/pages/dadosabertos/externo/")
    await page.locator("[name='publicacoesDT_length']").select_option("50", timeout=60000)
    
    # Define o caminho para salvar o arquivo .zip
    download_path = "C:/Users/Rogerio/Documents/consumidor_glassdoor_playwright/downloads/finalizadas_2024-01.zip"  # Caminho onde o arquivo zip será salvo
    extract_path = "C:/Users/Rogerio/Documents/consumidor_glassdoor_playwright/dados/"  # Pasta para onde os arquivos serão extraídos

    # Garante que o diretório de extração exista
    os.makedirs(extract_path, exist_ok=True)
    
    async with page.expect_download(timeout=60000) as download_info:
        async with page.expect_popup() as page1_info:
            await page.get_by_title("Download 'finalizadas_2024-01").click(timeout=60000)
        page1 = await page1_info.value

    # Captura o download e salva o arquivo .zip no local especificado
    download = await download_info.value
    await download.save_as(download_path)  # Salva o arquivo .zip no caminho especificado

    # Fecha o popup
    await page1.close()

    # Fecha o navegador
    await context.close()
    await browser.close()

    # Descompactar o arquivo .zip
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)  # Extrai todos os arquivos para a pasta de destino
    
    print(f"Arquivo descompactado com sucesso em: {extract_path}")

async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)

# Executa o código principal
asyncio.run(main())
