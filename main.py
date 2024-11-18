#!/usr/bin/env python
import sys
from stock.crew import stockCrew


def run():
    """
    Run the crew.
    """
    # Solicita o ticker ao usuário
    ticker = input("Qual ticker você quer que eu analise? ")
    
    inputs = {
        'ticker': ticker
    }
    
    # Cria a crew e configura o ticker antes de executar
    crew_instance = stockCrew().set_ticker(ticker)
    crew_instance.crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    run()