from fastapi import FastAPI,Request,Response
from fastapi.responses import HTMLResponse
from yfinance import Ticker
from pydantic import BaseModel
import matplotlib.pyplot as plt
import io

app = FastAPI() #Initialize FastAPI 


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
    pass


    

@app.get("/stockDetails/{stockName}")
async def getStockResults(stockName:str,request:Request):
    data = readStockData(stockName.companyName)
    return data 
    pass 

@app.get("/stockGraph/{stockName}",response_class=HTMLResponse)
async def getStockGraph(stockName:str,request:Request):
    ticker = Ticker(stockName)
    data = ticker.history(period="1mo")

    # Plot the data using matplotlib
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label='Close Price')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f'{stockName} Closing Prices (1 Month)')
    plt.legend()

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Close the plot to release memory
    plt.close()

    # Return the PNG image as a response
    return Response(content=buf.getvalue(), media_type="image/png")




