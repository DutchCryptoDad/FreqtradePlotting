# THIS IS VERSION 1.0 of this strategy


# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class kcx_strat_prod(IStrategy):
    stoploss = -0.2
    timeframe = "1d"
    minimal_roi = {"0": 0.6}

    order_types = {
        "buy": "limit",
        "sell": "limit",
        "emergencysell": "market",
        "stoploss": "market",
        "stoploss_on_exchange": True,
        "stoploss_on_exchange_interval": 60,
        "stoploss_on_exchange_limit_ratio": 0.99,
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["SMA"] = ta.SMA(dataframe, timeperiod=20)
        # MACD
        # https://mrjbq7.github.io/ta-lib/func_groups/momentum_indicators.html
        macd = ta.MACD(
            dataframe,
            fastperiod=12,
            fastmatype=0,
            slowperiod=26,
            slowmatype=0,
            signalperiod=9,
            signalmatype=0,
        )
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]
        dataframe["macdhist"] = macd["macdhist"]
        # RSI
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=7)
        # SLOW STOCHASTIC
        # https://mrjbq7.github.io/ta-lib/doc_index.html
        stoch = ta.STOCH(
            dataframe,
            fastk_period=14,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0,
        )
        dataframe["slowd"] = stoch["slowd"]
        dataframe["slowk"] = stoch["slowk"]
        # Keltner Channel
        # https://qtpylib.io/docs/latest/
        keltner = qtpylib.keltner_channel(dataframe, window=23, atrs=1)
        dataframe["kc_upperband"] = keltner["upper"]
        dataframe["kc_lowerband"] = keltner["lower"]
        dataframe["kc_middleband"] = keltner["mid"]
        dataframe["kc_percent"] = (dataframe["close"] - dataframe["kc_lowerband"]) / (
            dataframe["kc_upperband"] - dataframe["kc_lowerband"]
        )
        dataframe["kc_width"] = (dataframe["kc_upperband"] - dataframe["kc_lowerband"]) / dataframe[
            "kc_middleband"
        ]
        macd = ta.MACD(
            dataframe,
            fastperiod=12,
            fastmatype=0,
            slowperiod=26,
            slowmatype=0,
            signalperiod=9,
            signalmatype=0,
        )
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]
        dataframe["macdhist"] = macd["macdhist"]
        # print(metadata)
        # print(dataframe.tail(20))
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            ((dataframe["close"] > dataframe["kc_upperband"]) & (dataframe["macdhist"] > 0)),
            "buy",
        ] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["close"] < dataframe["kc_middleband"])
                | (dataframe["macdhist"] < 0) & (dataframe["slowd"] < 50)
            ),
            "sell",
        ] = 1
        return dataframe
