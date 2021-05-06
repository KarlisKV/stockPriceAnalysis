# -*- coding: utf-8 -*-
"""
Created on Sat May  1 18:03:44 2021

@author: karli
"""
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np
#Define companyTag, name and the sector they are working in
companyTag = []
companyName = []
companySector = []
companySubSector = []
marketCap = []
openingPrice = []
closingPrice = []

date = []

#Spread in %
spreadTemp = 0
spread = spreadTemp*0.01/2

#TODO: fix the swapList so that the first and last element are also swapped and I can remove the .pop()'s
#Function to swap lists since the excel files with the data are from newest to oldest
def swapList(newList):
    size = len(newList)
      
    # Swapping 
    temp = newList[0]
    newList[0] = newList[size - 1]
    newList[size - 1] = temp
      
    return newList


with open('SP500.csv') as csvFile:
    csvReader = csv.reader(csvFile)
    for row in csvReader:
        companyTag.append(row[0])
        companyName.append(row[1])
        companySector.append(row[2])
        companySubSector.append(row[5])
        marketCap.append(row[6])
#Fixes names for the companies that aren't correctly read in the file
companyTag[70] = "BRK-B"
companyTag[60] = "BF-B"



#Web scraper function using Selenium, accepts the terms and conditions and then clicks the 
#download button to get the stock prices from the past 5 years for each of the SMP 500 companies
def downloadDataFromYahoo():
    for i in range(len(companyTag)):
        driver = webdriver.Chrome()
        driver.get("https://finance.yahoo.com/quote/"+companyTag[i]+"/history?period1=1462060800&"+
           "period2=1619827200&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true")
    
        driver.find_element_by_name("agree").click()
        time.sleep(2)
        WebDriverWait(driver, 4500).until(EC.presence_of_element_located((By.XPATH, '//*[@id="render-target-default"]')))    
        path= '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]/a'
        button = driver.find_element_by_xpath(path)
        button.click()
        time.sleep(5)
        driver.close()

#Opens one of the data sheets and gets the stock prices 
def getStockPrices(iteration):
     with open(companyTag[iteration] + '.csv') as csvFile:
        next(csvFile)
        csvReader = csv.reader(csvFile)
        for row in csvReader:
            date.append(row[0])
            openingPrice.append(row[1])
            closingPrice.append(row[4])
            
     swapList(openingPrice)
     swapList(closingPrice)
     swapList(date)
     


            
#calculates return on investment using market hours trading method
def getOnMarketROI():
    
    returnOnInvestment = []
   
    
    for i in range(len(companyTag)):
         startingCapital = 100.00
         capital = 100.00
         getStockPrices(i)
         openingPrice.pop(0)
         closingPrice.pop(0)
         date.pop(0)         
         openingPrice.pop(-1)
         closingPrice.pop(-1)
         date.pop(-1)    
         
         for j in range(len(date)):
            
             capital = capital*(1-spread)*float(closingPrice[j])/float(openingPrice[j])
            
    
         returnOnInvestment.append(round((capital/startingCapital - 1)*100, 2))
         
         openingPrice.clear()
         closingPrice.clear()
         date.clear()
         
    return returnOnInvestment

#calculates return on investment using off market hour trading method
def getOffMarketROI():
    
    returnOnInvestment = []
    
    
    for i in range(len(companyTag)):
         startingCapital = 100.00
         capital = 100.00
             
         getStockPrices(i)
         openingPrice.pop(0)
         closingPrice.pop(0)
         date.pop(0)
         openingPrice.pop(-1)
         closingPrice.pop(-1)
         date.pop(-1)    
         for j in range(1, len(date)):
            
             capital = capital*(1-spread)*float(openingPrice[j])/float(closingPrice[j-1])
            
    
         returnOnInvestment.append(round((capital/startingCapital - 1)*100, 2))
         
         openingPrice.clear()
         closingPrice.clear()
         date.clear()
         
    return returnOnInvestment

def get5YearReturn():
    returnOnInvestment = []
    for i in range(len(companyTag)):
        getStockPrices(i)        
        openingPrice.pop(0)
        closingPrice.pop(0)
        date.pop(0)
        openingPrice.pop(-1)
        closingPrice.pop(-1)
        date.pop(-1)      
        returnOnInvestment.append(round((float(
                closingPrice[-1])/float(openingPrice[0])- 1)*100, 2))
        openingPrice.clear()
        closingPrice.clear()
        date.clear()
    return returnOnInvestment  


marketReturns = getOnMarketROI()     
offMarketReturns = getOffMarketROI()       
fiveYearReturns = get5YearReturn()

returnArray = np.array([companyTag, companySector, companySubSector, marketCap, marketReturns, offMarketReturns, fiveYearReturns])
with open('investmentReturns.csv', 'w', newline='') as file:
    mywriter = csv.writer(file, delimiter=',')
    mywriter.writerows(zip(*returnArray))