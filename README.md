# VaciIA — Protótipo de controle e acompanhamento da vacinação

Aplicação web demonstrativa feita com Python, Streamlit e SQLite.

## Funcionalidades
- Cadastro de pessoas
- Registro de vacinas e doses aplicadas
- Histórico de vacinação
- Classificação auxiliar de datas previstas
- Geração de lembretes personalizados por modelos de texto
- Painel com indicadores

## Executar localmente

1. Instale Python 3.10 ou superior.
2. Abra o terminal na pasta do projeto.
3. Crie e ative um ambiente virtual (opcional, mas recomendado).
4. Instale as dependências:

```bash
pip install -r requirements.txt
```

5. Inicie:

```bash
streamlit run app.py
```

O banco `vacia.db` será criado automaticamente na primeira execução.

## Limites importantes
Este é um protótipo acadêmico. Use dados fictícios. As datas de próximas doses são informadas manualmente e não são calculadas a partir de um calendário vacinal. O sistema não substitui o PNI, a caderneta de vacinação nem a orientação de profissionais de saúde. Não envia SMS ou WhatsApp.

## Publicação no Streamlit Community Cloud
Envie os arquivos `app.py`, `database.py`, `intelligence.py` e `requirements.txt` para um repositório GitHub e conecte o repositório ao Streamlit Community Cloud.
