from agno.agent import Agent, RunResponse
from agno.models.ollama import Ollama
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools

# agent = Agent(
#     model=Ollama(id="gemma3:12b"),
#     tools=[YFinanceTools(stock_price=True)],
#     instructions="Use tables to display data. Don't include any other text.",
#     markdown=True,
# )

agent = Agent(
    model=Gemini(id="gemini-2.0-flash"),
    tools=[YFinanceTools(stock_price=True)],
    instructions="Use tables to display data. Don't include any other text.",
    markdown=True,
)

agent.print_response("Given today's closing prices, give me the top 10 B3 Stocks", stream=True)




