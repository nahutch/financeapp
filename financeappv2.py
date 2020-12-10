import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta

@st.cache
def processStocks(constituents, yesterday, interval = "1d", start = "2020-02-20"):


    betaByCompany = pd.DataFrame(columns = ["Company", "UpBeta", "SimpleBeta", "DownBeta", "Industry"])


    # initialize index
    indexDf = findIndexDf(start = start, end = yesterday, interval = interval)

    indexDf["Change"] = indexDf["Close"] - indexDf["Open"]
    indexDf["Change %"] = (indexDf["Change"] / indexDf["Open"]) * 100

    #Filter into lists where change is positive and negative to calculate Up/Down Betas
    positiveFilter = (indexDf["Change"] >= 0)
    indexPositive = indexDf["Change %"].where(positiveFilter)
    indexPositive.dropna(inplace = True)
    indexNegative = indexDf["Change %"].where(positiveFilter == False)
    indexNegative.dropna(inplace = True)

    #Calculate varience of entire index, and up/down filtered data
    indexVar = indexDf["Change %"].var()
    indexPositiveVar = indexPositive.var()
    indexNegativeVar = indexNegative.var()

    firsttest = True
    #Parse through each company
    for row in constituents.index:

        tickerName = constituents.loc[row]["Symbol"]

        # Grab dataframe data from the tickerName
        tickerData = yf.Ticker(tickerName)
        tickerDf = tickerData.history(start = start, end = yesterday, interval = interval)

        #calculate the change and change percentage for each day
        tickerDf["Change"] = tickerDf["Close"] - tickerDf["Open"]
        tickerDf["Change %"] = (tickerDf["Change"] / tickerDf["Open"]) * 100

        #right now dropping the unused columns.  Adjust this if need to change later
        tickerDf.drop(columns = ["High", "Low", "Volume", "Change"], inplace = True) #["Dividends, "Stock Splits"] do not appear to be on every stock.



        #Filter timeframes where S&P was positive and where it was negative
        tickerPositive = tickerDf["Change %"].where(positiveFilter)
        tickerPositive.dropna(inplace = True)

        tickerNegative = tickerDf["Change %"].where(positiveFilter == False)
        tickerNegative.dropna(inplace = True)



        #calculate simple, up, and down betas
        positiveCovs = tickerPositive.cov(indexPositive)
        negativeCovs = tickerNegative.cov(indexNegative)

        covs = tickerDf["Change %"].cov(indexDf["Change %"])


        betaByCompany = betaByCompany.append({"Company": row,
                                            "UpBeta": positiveCovs/indexPositiveVar,
                                            "SimpleBeta" : covs/indexVar,
                                            "DownBeta": negativeCovs/indexNegativeVar,
                                            "Industry": constituents.loc[row]["Sector"]},
                                            ignore_index = True)

        # if tickerName == "AAL":
        #     st.write(tickerName)
        #     st.write(tickerDf)
        #     st.write("Index Pos:")
        #     st.write(indexPositive)
        #     st.write("Ticker Pos:")
        #     st.write(tickerPositive)
        #     st.write("Index Neg:")
        #     st.write(indexNegative)
        #     st.write("Ticker Neg:")
        #     st.write(tickerNegative)
        #     st.write("Positive Beta:")
        #     st.write(positiveCovs/indexPositiveVar)
        #     firsttest = False

    betaByCompany.dropna(inplace = True)
    # betaByCompany.set_index("Company", inplace = True)
    return betaByCompany

# @st.cache
def findBetas(constituents, yesterday, interval = "60m", start = "2020-02-20", period = "1d"):

    if not st.sidebar.checkbox("Recalculate with today's data? (Most recent Update: 12-04-2020. This may take a few minutes)"):
        try:
            betaByCompany = pd.read_csv("betaByCompany.csv")
            return betaByCompany
        except:
            betaByCompany = pd.DataFrame(columns = ["Company", "UpBeta", "SimpleBeta", "DownBeta", "Industry"])
    else:
        betaByCompany = pd.DataFrame(columns = ["Company", "UpBeta", "SimpleBeta", "DownBeta", "Industry"])


    # initialize index
    indexDf = findIndexDf(start = start, end = yesterday, period = period, interval = interval)
    indexDf["Change"] = indexDf["Close"] - indexDf["Open"]
    indexDf["Change %"] = (indexDf["Change"] / indexDf["Open"]) * 100
    #Filter into lists where change is positive and negative to calculate Up/Down Betas
    positiveFilter = (indexDf["Change"] >= 0)
    indexPositive = indexDf["Change %"].where(positiveFilter)
    indexPositive.dropna(inplace = True)
    indexNegative = indexDf["Change %"].where(positiveFilter == False)
    indexNegative.dropna(inplace = True)
    #Calculate varience of entire index, and up/down filtered data
    indexVar = indexDf["Change %"].var()
    indexPositiveVar = indexPositive.var()
    indexNegativeVar = indexNegative.var()
    firsttest = True
    #Parse through each company
    for row in constituents.index:
        tickerName = constituents.loc[row]["Symbol"]
        # Grab dataframe data from the tickerName
        tickerData = yf.Ticker(tickerName)
        tickerDf = tickerData.history(period = period, interval = interval, start = start, end = yesterday)
        #calculate the change and change percentage for each day
        tickerDf["Change"] = tickerDf["Close"] - tickerDf["Open"]
        tickerDf["Change %"] = (tickerDf["Change"] / tickerDf["Open"]) * 100

        #right now dropping the unused columns.  Adjust this if need to change later
        tickerDf.drop(columns = ["Open", "High", "Low", "Close", "Volume"], inplace = True)

        #Filter timeframes where S&P was positive and where it was negative
        tickerPositive = tickerDf["Change %"].where(positiveFilter)
        tickerPositive.dropna(inplace = True)
        tickerNegative = tickerDf["Change %"].where(positiveFilter == False)
        tickerNegative.dropna(inplace = True)

        #calculate simple, up, and down betas
        positiveCovs = tickerPositive.cov(indexPositive)
        negativeCovs = tickerNegative.cov(indexNegative)
        covs = tickerDf["Change %"].cov(indexDf["Change %"])

        betaByCompany = betaByCompany.append({"Company": row,
                                            "UpBeta": positiveCovs/indexPositiveVar,
                                            "SimpleBeta" : covs/indexVar,
                                            "DownBeta": negativeCovs/indexNegativeVar,
                                            "Industry": constituents.loc[row]["Sector"]},
                                            ignore_index = True)
    betaByCompany.dropna(inplace = True)
    # betaByCompany.set_index("Company", inplace = True)

    betaByCompany.to_csv("betaByCompany.csv")
    return betaByCompany


def findIndexDf(start = "2020-02-20", end = "2020-06-01", interval = "60m", period = "1d"):
    #Gather S&P500 Data
    indexData = yf.Ticker("^GSPC")
    return(indexData.history(start = start, end = end, interval = interval))


def displayHeaderText():
    st.write("# Stock Analysis through Covid-19")
    st.write("On February 19 2020, the US Stock Market had reached at a record high for the S&P500.")
    st.write("However, on February 20 2020 the US Stock Market began to crash and reported some of the largest declines since the 2008 financial crisis.  Impacts around the world were felt, and in March global stocks saw a downturn of at least 25%.")
    st.write("The S&P500 did begin to bounce back in April/May and continued to reach record highs through the last few months of 2020. Needless to say, the stock market has been extremely volitile since February 20 2020. However, certain stocks and certain industries showed more volitily than others.")
    st.write("We will be looking at upside and downside risk of stocks by calculating the upside and downside betas of stocks against the S&P500. Lets use Boeing as an example:")
    st.write("{0} had a Upside Beta of {1:.3f}.  This means that on days where the S&P 500 went up by one point, {0} would go up by an average of {1:.3f} points.".format("Boeing Company", betaByCompanyIndexed["UpBeta"]["Boeing Company"]))
    st.write("{0} had a Downside Beta of {1:.3f}.  This means that on days where the S&P 500 went down by one point, {0} would go down by an average of {1:.3f} points.".format("Boeing Company", betaByCompanyIndexed["DownBeta"]["Boeing Company"]))
    st.write("A higher Upside Beta means on days when the S&P went up, the selected stock would rise up faster.  Stocks and Industries with higher upside beta recovered at an accelerated rate. On the converse side, a higher value of downside beta means on days when the S&P went down, the selected stock would fall faster.  Stocks and Industries with high downside beta crashed the hardest.")


def displayIndustryData(betasByIndustry):
    st.write("# Industry Analysis")
    st.write("Lets take a look at how the various industries were affected:")

    betasByIndustry = betasByIndustry.sort_values("UpBeta", ascending = False)


    plotBarGraph(betasByIndustry, "UpBeta")
    # st.bar_chart(betasByIndustry["UpBeta"])

    st.write("The Industry with the highest positive beta is {}.  This is the industry that has risen at the relatively fastest rate on days where the market was rising.  This correlates to the industry that has been able to bounce back the fastest".format(betasByIndustry.index[0]))
    st.write("The Industry with the lowest positive beta is {}.  This is the industry that has risen at the relatively slowest rate on days where the market was rising.  This correlates to the industry that has had the most trouble bouncing back".format(betasByIndustry.index[-1]))

    plotBarGraph(betasByIndustry, "DownBeta")
    betasByIndustry = betasByIndustry.sort_values("DownBeta", ascending = False)
    st.write("The Industry with the highest negative beta is {}.  This is the industry that has fallen at the relatively fastest rate on days where the market was falling.  This correlates to the industry that was hit the hardest during the market falls".format(betasByIndustry.index[0]))
    st.write("The Industry with the lowest negative beta is {}.  This is the industry that has fallen at the relatively slowest rate on days where the market was falling.  This correlates to the industry that was the least impacted by the market falling".format(betasByIndustry.index[-1]))


@st.cache
def read_csv(name):
    return pd.read_csv(name, delimiter = ",", index_col = "Name")
    # print(constituents.head())

@st.cache
def read_small_csv(name):
    return pd.read_csv(name, delimiter = ",", index_col = "Name")
    #print(constituents.head())

#failed attempt to get matplotlib bar charts- would only show up every few times you reload
def plotBarGraph(betasByIndustry, col, industry = True):
    indexLabel = "Positive Betas"
    color = "g"
    plt.figure(1)

    if col == "DownBeta":
        indexLabel = "Negative Beta"
        color = "r"
        plt.figure(2)

    if industry:
        title = "{} by Industry During Covid-19".format(indexLabel)
    else:
        title = "Top and bottom 5 Stocks by {} During Covid-19".format(indexLabel)


    betasByIndustry = betasByIndustry.round(3)
    betasByIndustry = betasByIndustry.sort_values(col, ascending = False)


    matplotlib.rcParams.update({'font.size': 6})
    labels = betasByIndustry.index
    x = np.arange(len(labels))  # the label locations


    fig, ax = plt.subplots()

    bars = plt.bar(x, betasByIndustry[col] , color = color, label= indexLabel)
    plt.xlabel(indexLabel)
    plt.title(title)
    plt.legend()
    plt.xticks(x, labels)

    betaValueLabels = betasByIndustry[col].reset_index().drop(columns = "Industry")

    # Labeling apprear to be breaking it when it has two graphs
    # rects = ax.patches
    #
    # for rect in rects:
    #     height = rect.get_height()
    #     plt.annotate(rect.get_x() + rect.get_width() / 2, height + 4, test[0], ha='center', va='bottom')
    #
    #
    # for bar in bars:
    #     height = bar.get_height()
    #     plt.annotate(bar.get_x() + bar.get_width() / 2, height + 4, test[0]),
    #     xytext=(0, 3),  # 3 points vertical offset
    #     textcoords="offset points",
    #     ha='center', va='bottom')

    plt.setp(ax.xaxis.get_majorticklabels(), rotation=35, ha="right" )
    plt.tight_layout()

    st.pyplot(fig, clear_figure=True)

    return(betasByIndustry.index[0])

def plotStockBarGraph(betasByIndustry, col):
    indexLabel = "Positive Betas"
    color = "g"
    plt.figure(3)

    if col == "DownBeta":
        indexLabel = "Negative Beta"
        color = "r"
        plt.figure(4)


    title = "Top and bottom 5 Stocks by {} During Covid-19".format(indexLabel)


    betasByIndustry = betasByIndustry.round(3)

    matplotlib.rcParams.update({'font.size': 6})
    labels = betasByIndustry.index
    x = np.arange(len(labels))  # the label locations


    fig, ax = plt.subplots()

    bars = plt.bar(x, betasByIndustry, color = color, label= indexLabel)
    plt.xlabel(indexLabel)
    plt.title(title)
    plt.legend()
    plt.xticks(x, labels)

    plt.setp(ax.xaxis.get_majorticklabels(), rotation=35, ha="right" )
    plt.tight_layout()

    st.pyplot(fig, clear_figure=True)

    return(betasByIndustry.index[0])

if __name__ == "__main__":

    #read the ticker names data
    small_constituents = read_csv("constituents_small.csv")
    constituents = read_small_csv("constituents.csv")

    #Set data gathering parameters
    interval = "60m"
    start = "2020-02-20"
    period = "1d"
    yesterday = datetime.strftime(datetime.now() - timedelta(1), "%Y-%m-%d")    #need to declare "yesterday" outside of function to cache findbetas properly

    # start = time.time()
    betaByCompany = findBetas(constituents, yesterday, interval = interval, start = start)
    # betaByCompany2 = processStocks(constituents, yesterday, interval = interval, start = start)
    # end = time.time()
    # st.write(end - start)
    # st.write(betaByCompany)
    # st.write("BetaByCompany:")
    # st.write(betaByCompany)
    # st.write("BetaByCompany2:")
    # st.write(betaByCompany2)

    #Sidebar selection for full list of shortened list
    if st.sidebar.checkbox('Shortened Stock List'):
        stockListSelection = list(small_constituents.index.values)
    else:
        stockListSelection = list(constituents.index.values)
    tickerName = st.sidebar.selectbox("Select a Stock to view: ", stockListSelection)



    #gather ticker Data and Beta values
    tickerData = yf.Ticker(constituents.loc[tickerName]["Symbol"])
    tickerDf = tickerData.history(period = "1d", start = start, end = yesterday, interval = "1d")
    indexDf = findIndexDf(start = start, end = yesterday, interval = "1d")





    # Manipulate Betas data to get betasByIndustry and betaByCompanyIndexed
    betasByIndustry = pd.DataFrame(columns = ["Industry", "UpBeta", "DownBeta", "SimpleBeta"])

    for industry in betaByCompany["Industry"].unique():
        ups = betaByCompany["UpBeta"].where(betaByCompany["Industry"] == industry)
        downs = betaByCompany["DownBeta"].where(betaByCompany["Industry"] == industry)
        simples = betaByCompany["SimpleBeta"].where(betaByCompany["Industry"] == industry)

        betasByIndustry = betasByIndustry.append({"Industry": industry,
                                                  "UpBeta": ups.sum() / ups.count(),
                                                  "DownBeta": downs.sum() / downs.count(),
                                                  "SimpleBeta": simples.sum() / simples.count()},
                                                  ignore_index = True)

    betasByIndustry = betasByIndustry.set_index("Industry")
    betaByCompanyIndexed = betaByCompany.set_index("Company")


######################## BEGIN OUTPUT ###################################





    displayHeaderText()

    displayIndustryData(betasByIndustry)



    st.write("# Best/Worst Performing Stock Analysis")
    st.write("Below are the top and bottom 5 individual stocks by Positive and Negative Betas.  These are the individual stocks that showed the most volotility in their respective beta categories across all S&P 500 Stocks")

    allCompanyPositives = betaByCompanyIndexed["UpBeta"].sort_values(ascending = False)
    allCompanyNegatives = betaByCompanyIndexed["DownBeta"].sort_values(ascending = False)
    topBottomCompanyPositives = allCompanyPositives.iloc[0:5].append(allCompanyPositives.iloc[allCompanyPositives.size - 5: allCompanyPositives.size])
    topBottomCompanyNegatives = allCompanyNegatives.iloc[0:5].append(allCompanyNegatives.iloc[allCompanyNegatives.size - 5: allCompanyNegatives.size])

    plotStockBarGraph(topBottomCompanyPositives, "UpBeta")
    plotStockBarGraph(topBottomCompanyNegatives, "DownBeta")

    # May need to start using Altair for charts if continued issues with matplotlib
    # st.bar_chart(topBottomCompanyNegatives)

    st.write("# Custom Stock Analysis")
    st.write("Select a stock from the list on the side to compare its performance aginast the S&P500 and within an Industry")
    st.write(" ")

    tickerOpenValue = tickerDf.iloc[0]["Open"]
    indexOpenValue = indexDf.iloc[0]["Open"]

    tickerDf[tickerName] = ((tickerDf["Open"] - tickerOpenValue) / tickerOpenValue) * 100
    indexDf["S&P 500"] = ((indexDf["Open"] - indexOpenValue) / indexOpenValue) * 100

    # tickerDf["Change %"] = (tickerDf["Change"] / tickerDf["Open"]) * 100

    st.write(f"Percentage Change of {tickerName} ({constituents.loc[tickerName]['Symbol']}) from Feb 20 2020 through present compared with S&P 500")
    st.line_chart(pd.concat([tickerDf[tickerName], indexDf["S&P 500"]], axis = 1))


    selectedIndustry = betaByCompanyIndexed.at[tickerName, "Industry"]
    originalIndustryBetas = betaByCompanyIndexed.where(betaByCompanyIndexed["Industry"] == selectedIndustry)
    originalIndustryBetas.dropna(inplace = True)

    # to view all industry betas in the industry
    # st.write(originalIndustryBetas)


    st.write("{} had a positive beta value of {:.3f}.  This compares to an industry average for {} of {:.3f}.  The average across all S&P500 stocks is {:.3f}".format(
                                                        tickerName,
                                                        originalIndustryBetas["UpBeta"][tickerName],
                                                        selectedIndustry,
                                                        betasByIndustry.at[selectedIndustry, "UpBeta"],
                                                        betaByCompany["UpBeta"].sum() / betaByCompany["UpBeta"].count()))
    st.write("{} had a negative beta value of {:.3f}.  This compares to an industry average for {} of {:.3f}.  The average across all S&P500 stocks is {:.3f}".format(
                                                        tickerName,
                                                        originalIndustryBetas["DownBeta"][tickerName],
                                                        selectedIndustry,
                                                        betasByIndustry.at[selectedIndustry, "DownBeta"],
                                                        betaByCompany["DownBeta"].sum() / betaByCompany["DownBeta"].count()))


    plt.figure(3)

    fig2, ax2 = plt.subplots()



    industries = betasByIndustry.index.sort_values()

    customIndustry = st.sidebar.checkbox("Compare Scatterplot against a Different Industry")
    if customIndustry:
        selectedIndustry = st.sidebar.selectbox("Compare against an industry", industries)
        selectedIndustryBetas = betaByCompanyIndexed.where(betaByCompanyIndexed["Industry"] == selectedIndustry)
        selectedIndustryBetas.dropna(inplace = True)
    else:
        selectedIndustryBetas = originalIndustryBetas


    plt.scatter(selectedIndustryBetas["UpBeta"], selectedIndustryBetas["DownBeta"])
    plt.scatter(betaByCompanyIndexed["UpBeta"][tickerName], originalIndustryBetas["DownBeta"][tickerName])
    plt.annotate(tickerName, (betaByCompanyIndexed["UpBeta"][tickerName], originalIndustryBetas["DownBeta"][tickerName]))


    #add the min and max company sum of the betas on the graph for reference
    selectedIndustryBetas["SumBothBetas"] = selectedIndustryBetas["UpBeta"] + selectedIndustryBetas["DownBeta"]
    minCompany = selectedIndustryBetas["SumBothBetas"].idxmin()
    maxCompany = selectedIndustryBetas["SumBothBetas"].idxmax()

    plt.annotate(minCompany, (betaByCompanyIndexed["UpBeta"][minCompany], selectedIndustryBetas["DownBeta"][minCompany]))
    plt.annotate(maxCompany, (betaByCompanyIndexed["UpBeta"][maxCompany], selectedIndustryBetas["DownBeta"][maxCompany]))



    ax2.set_xlabel("Positive Beta")
    ax2.set_ylabel('Negative Beta')
    ax2.set_title("{} vs Industry ({}) Positive and Negative Beta Values".format(tickerName, selectedIndustry))

    st.pyplot(fig2, clear_figure = True)





# This function will keep track real time of progress on a running alg
# latest_iteration = st.empty()
# bar = st.progress(0)
#
# for i in range(100):
#   # Update the progress bar with each iteration.
#   latest_iteration.text(f'Iteration {i+1}')
#   bar.progress(i + 1)
#   time.sleep(0.1)
