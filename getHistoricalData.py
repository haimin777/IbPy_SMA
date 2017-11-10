
import tradingWithPython as twp
import datetime
# ---check for correct version
print('twp version', twp.__version__)

from tradingWithPython.lib.interactiveBrokers import histData, createContract

dataLoader = histData.Downloader(debug=True)  # historic data downloader class
cur_time = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S") +str(" GMT") #запрашиваем текущее время в нужном формате
contract = createContract('EUR',"CASH","IDEALPRO","USD")
data = dataLoader.requestData(contract, cur_time, '1 D','5 mins',)  # запрашиваем данные

#data.to_csv('EUR.csv')  # write data to csv
print(data.info())
print('Done')
print(data.close.values)