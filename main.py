from fastapi import FastAPI,Request,Response
from fastapi.responses import HTMLResponse
from yfinance import Ticker
from pydantic import BaseModel
import matplotlib.pyplot as plt
import io
import requests
import google.generativeai as genai 
import os 
from dotenv import load_dotenv
load_dotenv() 


app = FastAPI() #Initialize FastAPI 
genai.configure(api_key=os.environ["geminiAPI"])

def readStockData(stockSymbol):
    data = False
    try:
        companyInfo = Ticker(stockSymbol)
    except: 
        data= False
        return {"dataFound":data}

    returnData = {"data":True}
    for key,value in companyInfo.info.items():
        returnData[key]=value

    return returnData


functions = [
    {
        "name": "get_stock_details",
        "description": "Get details about a stock",
        "parameters": {
            "type": "object",
            "properties": {
                "stockSymbol": {
                    "type": "string",
                    "description": "Stock market notation of that company"
                }
            },
            "required": ["stock_name"]
        }
    },
    {
        "name": "get_stock_graph",
        "description": "Get a graph of a stock's performance",
        "parameters": {
            "type": "object",
            "properties": {
                "stockSymbol": {
                    "type": "string",
                    "description": "Stock Market notation of that comapany"
                }
            },
            "required": ["stockSymbol"]
        }
    }
]


@app.get("/stockDetails/{stockSymbol}")
async def getStockResults(stockSymbol:str,request:Request):
    data = readStockData(stockSymbol)
    return data 
     

@app.get("/stockGraph/{stockSymbol}",response_class=HTMLResponse)
async def getStockGraph(stockSymbol:str,request:Request):
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
async def chat(request: Request):
    data = await request.json()
    user_message = data["message"]
    user_id = request.client.host # using user's IP as a unique identifier
     
    # Initialize chat history for the user if not present
    if user_id not in chat_history:
        chat_history[user_id] = []
    # Add user message to chat history
    chat_history[user_id].append({"role": "user", "content": user_message})
    response = genai.chat(
        model="gemini-pro",
        messages=chat_history[user_id],
        functions=functions
    )
    if response.function_call:
        function_name = response.function_call.name
        function_args = response.function_call.arguments
        function_map = {
            "get_stock_details": get_stock_details,
            "get_stock_graph": get_stock_graph,
        }
        if function_name in function_map:
            function_to_call = function_map[function_name]
            function_result = function_to_call(**function_args)
            # Add function call and result to chat history
            chat_history[user_id].append({"role": "function", "name": function_name, "content": function_result})
            return {"message": function_result}
        else:
            return {"message": f"Error: Unknown function '{function_name}'"}
    # Add model response to chat history
    chat_history[user_id].append({"role": "assistant", "content": response.text})
    return {"message": response.text}


"""
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("The opposite of hot is")
print(response.text)"""

