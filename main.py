from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from yfinance import Ticker
import yfinance as yf
from pydantic import BaseModel
import matplotlib.pyplot as plt
import io
import requests
import google.generativeai as genai 
import os 
from dotenv import load_dotenv
load_dotenv() 

def findStockSymbol(companyName: str):
    """
    Finds the stock symbol for a given company name.
    
    Args:
        companyName: The name of the company.
        
    Returns:
        A dictionary containing the company name, stock symbol, and a success status.
    """
    try:
        # Use yfinance to get a list of tickers
        tickers = yf.Tickers()  # Get all tickers
        matching_symbols = []

        # Search for the company name in the tickers
        for symbol in tickers.tickers:
            stock_info = tickers.tickers[symbol].info
            if 'longName' in stock_info and companyName.lower() in stock_info['longName'].lower():
                matching_symbols.append({
                    "symbol": symbol,
                    "name": stock_info['longName']
                })

        if matching_symbols:
            return {"dataFound": True, "matches": matching_symbols}
        else:
            return {"dataFound": False, "message": "No matching stock symbol found."}
    except Exception as e:
        return {"dataFound": False, "error": str(e)}
    
def getHistoricalPrices(stockSymbol: str, startDate: str, endDate: str):
    """
    Returns historical stock prices for the specified date range.
    
    Args:
        stockSymbol: Stock symbol of the company.
        startDate: Start date in 'YYYY-MM-DD' format.
        endDate: End date in 'YYYY-MM-DD' format.
        
    Returns:
        A DataFrame containing historical price data.
    """
    try:
        stockData = yf.download(stockSymbol, start=startDate, end=endDate)
        if stockData.empty:
            return {"dataFound": False, "message": "No historical data found."}
        return {"dataFound": True, "data": stockData.to_dict(orient='records')}
    except Exception as e:
        return {"dataFound": False, "error": str(e)}
    
def getCurrentPrice(stockSymbol: str):
    """
    Returns the current price of the specified stock.
    
    Args:
        stockSymbol: Stock symbol of the company.
        
    Returns:
        A dictionary containing the current price and relevant information.
    """
    try:
        stock = yf.Ticker(stockSymbol)
        currentPrice = stock.history(period='1d')['Close'].iloc[-1]
        return {"dataFound": True, "currentPrice": currentPrice}
    except Exception as e:
        return {"dataFound": False, "error": str(e)}
    
def readStockData(stockSymbol:str):
    """
        returns data related to that particular stockSymbol
        Args: 
            stockSymbol: stock symbol of the stock of a company.
        Returns:
            A dictionary containing all the information of that particular stock.
    """
    data = False
    try:
        companyInfo = Ticker(stockSymbol)
    except: 
        return {"dataFound": False}

    returnData = {"dataFound": True}  # Fixed key
    for key,value in companyInfo.info.items():
        returnData[key] = value

    return returnData

app = FastAPI() #Initialize FastAPI 

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

genai.configure(api_key=os.environ["geminiAPI"])
model = genai.GenerativeModel("gemini-1.5-flash",
                              system_instruction="""You are a finance chatbot, your job is to respond to user's queries only if it relates to finance, if a comapny name is provided by the user, use the companies stock symbol to gain info using the function s
                               The following dict contains the company name along with the stockSymbol use it to match
                                 {
    "Apple Inc": "AAPL",
    "Microsoft Corporation": "MSFT",
    "Alphabet Inc (Google)": "GOOGL",
    "Amazon.com Inc": "AMZN",
    "Meta Platforms Inc (Facebook)": "META",
    "NVIDIA Corporation": "NVDA",
    "Tesla, Inc": "TSLA",
    "Berkshire Hathaway Inc": "BRK.B",
    "Adobe Inc": "ADBE",
    "Salesforce, Inc": "CRM",
    "IBM Corporation": "IBM",
    "Intel Corporation": "INTC",
    "PayPal Holdings, Inc": "PYPL",
    "Netflix, Inc": "NFLX",
    "Cisco Systems, Inc": "CSCO",
    "Qualcomm Incorporated": "QCOM",
    "AMD (Advanced Micro Devices)": "AMD",
    "ServiceNow, Inc": "NOW",
    "Square, Inc (Block, Inc)": "SQ",
    "Zoom Video Communications, Inc": "ZM",
    "Palantir Technologies Inc": "PLTR",
    "Shopify Inc": "SHOP",
    "Salesforce.com Inc": "CRM",
    "Snowflake Inc": "SNOW",
    "Datadog, Inc": "DDOG",
    "Dropbox, Inc": "DBX",
    "Pinterest, Inc": "PINS",
    "Electronic Arts Inc": "EA",
    "Intuit Inc": "INTU",
    "Slack Technologies, Inc": "WORK",
    "Spotify Technology S.A.": "SPOT",
    "Roku, Inc": "ROKU",
    "Twilio Inc": "TWLO",
    "Lyft, Inc": "LYFT",
    "Snap Inc": "SNAP",
    "Nokia Corporation": "NOK",
    "ServiceNow, Inc": "NOW",
    "Zillow Group, Inc": "Z",
    "Uber Technologies, Inc": "UBER",
    "Atlassian Corporation Plc": "TEAM",
    "Nutanix, Inc": "NTNX",
    "RingCentral, Inc": "RNG",
    "CrowdStrike Holdings, Inc": "CRWD",
    "Okta, Inc": "OKTA",
    "Coinbase Global, Inc": "COIN",
    "MercadoLibre, Inc": "MELI",
    "Roku, Inc": "ROKU",
    "RingCentral, Inc": "RNG",
    "5N Plus Inc": "VNP.TO",
    "Kaltura, Inc": "KLTR",
    "Chegg, Inc": "CHGG",
}
""",
                              tools=[getHistoricalPrices,getCurrentPrice])
chat = model.start_chat(history=[],enable_automatic_function_calling=True)

def transform_history(history):
    new_history = []
    for chat in history:
        if chat["sender"] == "user":
            new_history.append({"parts": [{"text": chat["content"]}], "role": "user"})
        elif chat["sender"] == "bot":
            new_history.append({"parts": [{"text": chat["content"]}], "role": "model"})
    return new_history

@app.get("/stockDetails/{stockSymbol}")
async def getStockResults(stockSymbol: str, request: Request):
    data = readStockData(stockSymbol)
    return data 

@app.get("/stockGraph/{stockSymbol}", response_class=HTMLResponse)
async def getStockGraph(stockSymbol: str, request: Request):
    ticker = Ticker(stockSymbol)
    data = ticker.history(period="1mo")

    # Plot the data using matplotlib
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label='Close Price')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f'{stockSymbol} Closing Prices (1 Month)')
    plt.legend()

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Close the plot to release memory
    plt.close()

    # Return the PNG image as a response
    return Response(content=buf.getvalue(), media_type="image/png")

@app.post("/chat")
async def chatbot(request: Request):
    data = await request.json()  # Await the request to get the data
    message = data["message"]
    history = data.get("history", [])  # Get the history from the request, default to empty list if not provided

    # Convert the history to the format expected by your model
    transformed_history = transform_history(history)

    global chat
    chat.history = transformed_history  # Update the chat history
    response = chat.send_message(message)
    print(response.to_dict())
    return response.to_dict()
