import asyncio
import pandas as pd
import os
from playwright.async_api import Playwright, async_playwright

async def run(playwright: Playwright, num_paginas: int) -> None:
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"

    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(user_agent=user_agent)
    page = await context.new_page()

    await page.goto("https://www.glassdoor.com.br/Avalia%C3%A7%C3%B5es/index.htm")

    # Lista para armazenar os dados de todas as páginas
    data = []

    for page_num in range(num_paginas):
        print(f"Coletando dados da página {page_num + 1}")

        # Reavalie os elementos a cada nova página após o carregamento
        await page.wait_for_selector("[data-test='employer-card-single']", timeout=60000)

        # Localiza todos os cartões de empregador na página atual
        employer_cards = page.locator("[data-test='employer-card-single']")

        # Captura o número de cartões na página
        count = await employer_cards.count()
        print(f"Cartões encontrados na página {page_num + 1}: {count}")

        # Itera sobre os cartões da página atual
        for i in range(count):
            card = employer_cards.nth(i)

            # Coleta os dados de cada cartão
            employer = await card.locator("[data-test='employer-short-name']").inner_text()
            rating = await card.locator("[data-test='rating']").inner_text()
            employer_industry = await card.locator("[data-test='employer-industry']").inner_text()

            # Adiciona os dados à lista
            data.append({
                "employer": employer,
                "rating": rating,
                "employer_industry": employer_industry
            })

        # Tenta ir para a próxima página
        try:
            # Verifica se o botão de próxima página está disponível
            next_button = page.locator("[data-test='pagination-next']")
            if await next_button.is_disabled():
                print("Botão 'Próxima' desabilitado. Finalizando a paginação.")
                break

            # Clica no botão "Próxima" e espera a nova página carregar
            await next_button.click()
            await page.wait_for_load_state("load")

            # Adiciona uma espera adicional para garantir que a página foi completamente recarregada
            await asyncio.sleep(2)

        except Exception as e:
            print(f"Erro ao tentar paginar: {e}")
            print("Finalizando a paginação.")
            break

    # Converte os dados para um DataFrame pandas
    new_df = pd.DataFrame(data)

    # Define o caminho para o CSV
    output_path = "dados/empresas_glassdoor.csv"

    # Salva o DataFrame em um arquivo CSV
    new_df.to_csv(output_path, index=False)

    print(f"Dados salvos em {output_path}")

    # Fecha o navegador
    await context.close()
    await browser.close()

async def main() -> None:
    # Defina o número de páginas que você deseja paginar
    num_paginas = 5  # Alterar conforme necessário

    async with async_playwright() as playwright:
        await run(playwright, num_paginas)

# Executa o código principal
asyncio.run(main())
