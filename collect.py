import argparse
import csv
from datetime import datetime
from datetime import timedelta
import pandas as pd
import re
import requests
import requests_cache
from scrapy.selector import Selector


"""
POST to http://www.tcm.ba.gov.br/portal-da-cidadania/pessoal/
?tipo=xls&entidades=129&ano=2017&mes=1&tipoRegime=1&receitaLiquidaMensal=0,00
&receitaLiquidaAte=0,00&receitaLiquidaPeriodo="Janeiro de 2016 até Janeiro de 2017"
"""

expire_after = timedelta(days=1)
requests_cache.install_cache("salaries_cache", expire_after=expire_after)

entities = {
    129: {"name": "Prefeitura Municipal de FEIRA DE SANTANA", "slug": "city-hall"},
    544: {"name": "Camara Municipal de FEIRA DE SANTANA", "slug": "concilman"},
    880: {
        "name": "Instituto de Previdência de Feira de Santana",
        "slug": "pension-institute",
    },
    892: {
        "name": "Fundação Hospitalar de Feira de Santana",
        "slug": "hospital-foundation",
    },
    984: {
        "name": "Superintendência Municipal de Trânsito",
        "slug": "superintendence-of-traffic",
    },
    1008: {
        "name": "Fundação Cultural Municipal Egberto Tavares Costa",
        "slug": "egberto-tavares-costa",
    },
    1032: {
        "name": "Superintendência Municipal de Proteção e Defesa do Consumidor",
        "slug": "procon",
    },
    1033: {"name": "Agência Reguladora de Feira de Santana", "slug": "arfes"},
    1104: {
        "name": "Consórcio Público Interfederativo De Saúde Da Região de Feira de Santana",
        "slug": "portal-do-sertao",
    },
}


class ContentNotFound(Exception):
    def __init__(self, message, data):
        super().__init__(message)
        self.data = data


def get_data(entity_id, entity_slug, month, year):
    params = {
        "tipo": "pdf",
        "entidades": entity_id,
        "ano": year,
        "mes": month,
        "tipoRegime": 1,  # all
        "receitaLiquidaMensal": "0,00",  # from this point, useless but required fields
        "receitaLiquidaAte": "0,00",
        "receitaLiquidaPeriodo": "Janeiro de 2016 até Janeiro de 2017",
    }

    response = requests.post(
        "https://www.tcm.ba.gov.br/Webservice/index.php/exportar/pessoal",
        allow_redirects=True,
        params=params,
    )
    if response.status_code == 200:
        return response
    else:
        raise ContentNotFound(f"Content not found: {response.status_code}", params)


def parse_currency(raw_salary):
    """
    Parser salary with the following pattern:
    - R$ 788,00
    - R$ 2.109,74
    - R$ 0,00
    To:
    - 788.00
    - 2109.74
    - 0.00
    """
    raw_salary = re.sub(r"R[$]\s+", "", raw_salary)
    raw_salary = raw_salary.replace(".", "").replace(",", ".")
    return float(raw_salary)


def extract_data(response, entity_slug, month, year):
    rows = Selector(response=response).xpath('//*[@id="table"]/tr')
    extracted_data = []
    for row in rows:
        raw_data = row.xpath("td/text()").extract()
        if raw_data:
            try:
                data = {
                    "entidade": entity_slug,
                    "mes": month,
                    "ano": year,
                    "nome": raw_data[0],
                    "matricula": raw_data[1],
                    "tipo": raw_data[2],
                    "cargo": raw_data[3],
                    "salario": parse_currency(raw_data[4]),
                    "vantagens": parse_currency(raw_data[5]),
                    "gratificacao": parse_currency(raw_data[6]),
                    "carga_horaria": raw_data[7],
                    "situacao": raw_data[8],
                }
                if len(raw_data) > 9:
                    data["data_de_admissao"] = raw_data[9]
                extracted_data.append(data)
            except Exception as e:
                print(f"Error ({e}): {raw_data}")
    return extracted_data


def all_salaries(years):
    months = range(1, 13)
    not_found = []
    salaries = []
    now = datetime.now()

    print("Iniciando a coleta...")
    for year in years:
        if year > now.year:
            break
        for month in months:
            if now.year == year and now.month == month:
                break
            for entity_id, entity_data in entities.items():
                try:
                    response = get_data(entity_id, entity_data["slug"], month, year)
                    print(f"{year}-{month}-{entity_data['slug']}")
                except ContentNotFound as e:
                    not_found.append(e.data)
                    print(f"{year}-{month}-{entity_data['slug']} (não encontrado)")
                else:
                    month_salaries = extract_data(
                        response, entity_data["slug"], month, year
                    )
                    salaries.extend(month_salaries)

    return salaries, not_found


def export_not_found(not_found, label):
    with open(f"nao-encontrados-{label}.csv", "w", newline="") as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(["entidade", "mes", "ano"])

        for request in not_found:
            spamwriter.writerow(
                [entities[request["entidades"]]["name"], request["mes"], request["ano"]]
            )


def run(years):
    data, not_found = all_salaries(years)
    years_label = f"{years[0]}" if len(years) == 1 else f"{years[0]}-{years[-1]}"

    df = pd.DataFrame(data)
    df.to_csv(f"todos-os-salarios-{years_label}.csv", index=False)

    export_not_found(not_found, years_label)


def main():
    description = "Exporta todos os salários de servidores de Feira de Santana"
    parser = argparse.ArgumentParser(description=description)
    help = "Intervalo em anos"
    parser.add_argument("years", metavar="N", type=int, nargs="+", help=help)

    args = parser.parse_args()
    if len(args.years) > 1:
        years = range(args.years[0], args.years[1] + 1)
    else:
        years = range(args.years[0], args.years[0] + 1)
    run(years)


if __name__ == "__main__":
    main()
