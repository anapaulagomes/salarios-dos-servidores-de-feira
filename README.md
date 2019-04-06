# Salários dos servidores de Feira

Coleta os pagamentos realizados a servidores do munícipio de Feira
de Santana e exporta os dados para um arquivo CSV.

Dados de 2015 e a 2019 extraídos [aqui]() (atualização: 06/04/2019).

Fonte dos dados:

- [Tribunal de Contas dos Municípios do Estado da Bahia](http://www.tcm.ba.gov.br/portal-da-cidadania/pessoal/)

## Uso

Execute o seguinte script com o ano inicial e o ano final:

```
python collect.py 2015 2019
```

Também é possível especificar apenas um ano:

```
python collect.py 2019
```

Você pode escolher um ano a partir do ano 2000 (segundo o site do TCM).
Quando a coleta terminar, o script vai exportar dois CSVs:

- `todos-os-salarios-2015-2019.csv`
- `nao-encontrados-2015-2019.csv`

No arquivo `nao-encontrados-2015-2019.csv` estarão listadas as entidades
que não tem os salários no site do TCM. Caso você encontre um desses casos,
você pode pedir via 
[Lei de Acesso a Informação](http://www.acessoainformacao.gov.br/assuntos/conheca-seu-direito/a-lei-de-acesso-a-informacao)
a inserção desses dados e uma explicação do porquê eles não estão no site.

## Dados

Neste CSV, você encontrará informações das seguintes entidades:

- Prefeitura Municipal de FEIRA DE SANTANA
- Camara Municipal de FEIRA DE SANTANA
- Instituto de Previdência de Feira de Santana
- Fundação Hospitalar de Feira de Santana
- Superintendência Municipal de Trânsito
- Fundação Cultural Municipal Egberto Tavares Costa
- Superintendência Municipal de Proteção e Defesa do Consumidor
- Agência Reguladora de Feira de Santana
- Consórcio Público Interfederativo De Saúde Da Região de Feira de Santana

Campos:

- Data de admissão
- Gratificação
- Entidade
- Matrícula (id)
- Mês
- Nome
- Vantagens
- Cargo
- Salário
- Situação
- Tipo
- Carga horária
- Ano

Esse script é voltado para a cidade de Feira de Santana mas pode
ser adaptado para outras cidades da Bahia também.
