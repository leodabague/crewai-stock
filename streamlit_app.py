import streamlit as st
from src.stock.crew import stockCrew
import requests
import json
from datetime import datetime
import re

def obter_cotacao_atual():
    url = 'https://economia.awesomeapi.com.br/json/last/USD-BRL,BTC-USD'
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            dolar = float(data['USDBRL']['bid'])
            btc = float(data['BTCUSD']['bid'])
            return dolar, btc
        else:
            print(f"A requisição de cotação atual falhou com o código de status {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Ocorreu um erro na cotação atual: {str(e)}")
        return None, None

def obter_historico_cotacoes():
    urls = {
        'USD-BRL': 'https://economia.awesomeapi.com.br/USD-BRL/1?start_date=20240115&end_date=20240130',
        'BTC-USD': 'https://economia.awesomeapi.com.br/BTC-USD/1?start_date=20240115&end_date=20240130'
    }
    
    resultados = {}
    
    try:
        for moeda, url in urls.items():
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data:  # Verifica se há dados
                    # Pegamos apenas o último valor do período
                    ultimo_valor = float(data[0]['bid'])
                    resultados[moeda] = ultimo_valor
            else:
                print(f"A requisição do histórico de {moeda} falhou com o código de status {response.status_code}")
                resultados[moeda] = None
                
        return resultados
    except Exception as e:
        print(f"Ocorreu um erro ao obter histórico: {str(e)}")
        return None

def calcular_variacao_percentual(valor_atual, valor_anterior):
    """Calcula a variação percentual entre dois valores"""
    if valor_atual and valor_anterior and valor_anterior != 0:
        variacao = ((valor_atual - valor_anterior) / valor_anterior) * 100
        return variacao
    return None

def get_market_context():
    # Obtendo dados atuais e históricos
    cotacao_dolar_atual, cotacao_btc_atual = obter_cotacao_atual()
    historico = obter_historico_cotacoes()
    
    data_atual = datetime.now().strftime('%d/%m/%Y')
    
    context = {
        'data_atual': data_atual,
        'dolar': {
            'atual': cotacao_dolar_atual,
            'anterior': historico.get('USD-BRL') if historico else None,
            'variacao': None
        },
        'bitcoin': {
            'atual': cotacao_btc_atual,
            'anterior': historico.get('BTC-USD') if historico else None,
            'variacao': None
        }
    }
    
    # Calculando variações
    if context['dolar']['atual'] and context['dolar']['anterior']:
        context['dolar']['variacao'] = calcular_variacao_percentual(
            context['dolar']['atual'], 
            context['dolar']['anterior']
        )
    
    if context['bitcoin']['atual'] and context['bitcoin']['anterior']:
        context['bitcoin']['variacao'] = calcular_variacao_percentual(
            context['bitcoin']['atual'], 
            context['bitcoin']['anterior']
        )
    
    return context

def format_currency_text(text):
    """
    Formata o texto para lidar corretamente com símbolos monetários e markdown.
    """
    if not isinstance(text, str):
        return str(text)

    # Primeiro preserva os headers markdown
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.startswith('#'):
            # Preserva headers markdown
            formatted_lines.append(line)
        else:
            # Processa o texto normal
            # Substitui padrões de valor monetário em reais
            line = re.sub(r'R\$?\s*(\d+[.,]\d+)', r'R$ \1', line)
            line = re.sub(r'R\$?(\d+)', r'R$ \1', line)
            
            # Substitui padrões de valor monetário em dólares
            line = re.sub(r'\$\s*(\d+[.,]\d+)', r'US$ \1', line)
            line = re.sub(r'\$(\d+)', r'US$ \1', line)
            
            # Remove espaços extras
            line = re.sub(r'\s+', ' ', line)
            
            # Corrige espaçamentos após pontuação
            line = re.sub(r'([.,!?])\s*', r'\1 ', line)
            
            formatted_lines.append(line)
    
    # Junta as linhas novamente
    text = '\n'.join(formatted_lines)
    
    # Corrige espaços após a formatação
    text = text.replace('R$ ', 'R$ ')
    text = text.replace('US$ ', 'US$ ')
    
    # Remove espaços extras entre palavras
    text = re.sub(r'\s+', ' ', text)
    
    return text

def main():
    # Configuração da página
    st.set_page_config(
        page_title="Stock Analysis Crew",
        page_icon="📈",
        layout="centered"
    )
    
    # Título e descrição
    st.title("📊 Análise de Ações")
    st.markdown("""
    Esta aplicação utiliza AI para analisar ações e fornecer insights valiosos.
    Digite o ticker da ação que você deseja analisar abaixo.
    """)
    
    # Input do ticker com validação
    ticker = st.text_input(
        "Digite o ticker da ação",
        help="Por exemplo: WEGE3, LWSA3, SBFG3",
    ).strip().upper()
    
    # Botão de análise
    if st.button("Analisar", type="primary"):
        if not ticker:
            st.error("Por favor, insira um ticker válido.")
            return
        
        try:
            with st.spinner(f"Analisando {ticker}... Isso pode levar alguns minutos."):
                # Obtém o contexto de mercado
                market_context = get_market_context()
                
                # Configuração e execução da crew
                inputs = {
                    'ticker': ticker,
                    'market_context': market_context
                }
                
                crew_instance = stockCrew().set_ticker(ticker)
                result = crew_instance.crew().kickoff(inputs=inputs)
                
                if result:
                    # Formata o resultado para corrigir símbolos monetários
                    formatted_result = format_currency_text(result)
                    
                    # Exibição dos resultados
                    st.success("Análise concluída!")
                    
                    # Processamento especial para markdown
                    sections = re.split(r'(#+\s+[^\n]+)', formatted_result)
                    
                    for section in sections:
                        if section.strip():
                            # Se é um cabeçalho (começa com #)
                            if re.match(r'#+\s+', section):
                                st.markdown(section.strip())
                            else:
                                # Para conteúdo normal, divide em parágrafos
                                paragraphs = section.split('\n\n')
                                for paragraph in paragraphs:
                                    if paragraph.strip():
                                        st.markdown(paragraph.strip(), unsafe_allow_html=True)
                                        st.write("")  # Espaço entre parágrafos
                else:
                    st.error("Não foi possível obter resultados da análise.")
                
        except Exception as e:
            st.error(f"Ocorreu um erro durante a análise: {str(e)}")
            st.exception(e)

if __name__ == "__main__":
    main()
