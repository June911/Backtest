# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 13:24:13 2020

@author: Administrator
"""

import os
import pandas as pd

# dir_path = os.getcwd()
# file_name = 'BTCUSDT.csv'
# df_continue = pd.read_csv(os.path.join(dir_path,file_name))
# df_tohandle = df_continue[['Datetime','Close']]  

#　找潜在高点,只找一个小三角
def high(df,index,leftlen,rightlen,maxlen):
    presentbar = - rightlen
    high_mode = False 
    
    # find previous high
    while abs(presentbar) < maxlen and high_mode == False:
        # 先往前走一格
        presentpoint = df.iloc[index + presentbar,1]
        bar = True
        
        #　往前比较
        comparaisonbar = presentbar - 1
        while presentbar - comparaisonbar <= leftlen and bar == True:
            if df.iloc[index + comparaisonbar,1] > presentpoint:
                bar = False
            else:
                comparaisonbar = comparaisonbar - 1
        # 向后比较
        comparaisonbar = presentbar + 1           
        while comparaisonbar - presentbar <= rightlen and bar == True:
            if df.iloc[index + comparaisonbar,1] > presentpoint:
                bar = False
            else:
                comparaisonbar = comparaisonbar + 1
                
        if bar == True:
            high_mode = True
        else:
            presentbar = presentbar - 1
         
    if high_mode == True:
        high = presentpoint
    else:
        high = -1
    
    return high


# h = high(df_tohandle,6,1,1,2)

#　找潜在低点
def low(df,index,leftlen,rightlen,maxlen):
    presentbar = - rightlen
    low_mode = False 
    
    # find previous low
    while abs(presentbar) < maxlen and low_mode == False:
        # 先往前走一格
        presentpoint = df.iloc[index + presentbar,1]
        bar = True
        
        #　往前比较
        comparaisonbar = presentbar - 1
        while presentbar - comparaisonbar <= leftlen and bar == True:
            if df.iloc[index + comparaisonbar,1] < presentpoint:
                bar = False
            else:
                comparaisonbar = comparaisonbar - 1
                
        # 向后比较
        comparaisonbar = presentbar + 1           
        while comparaisonbar - presentbar <= rightlen and bar == True:
            if df.iloc[index + comparaisonbar,1] < presentpoint:
                bar = False
            else:
                comparaisonbar = comparaisonbar + 1
                
        if bar == True:
            low_mode = True
        else:
            presentbar = presentbar - 1
         
    if low_mode == True:
        low = presentpoint
    else:
        low=-1
    
    return low

# l = low(df_tohandle,6,1,1,2)


# inputs: 时间，价格， 幅度
def zigzag(df,pct):
    # 预设变量
    highlow = 0
    new_pivot = False
    substitute = False
    change = False
    price = df.iloc[0,1]
    
    df_record = df.head(1)
    
    
    # 前 2 个 bar 不能算， 否则和序列倒数比较
    for index in range(2,len(df)):
        possible_point = high(df,index,1,1,2)
        # print(index,possible_point)       
        #　找极大值，等于-1忽略
        if possible_point != -1:
            
            """
            highlow = 1 ==> 高点
            highlow = 0 ==> 起点
            highlow = -1 ==> 低点
            """
            # 前低后高，且高出涨幅，为新高点
            if highlow <= 0 and possible_point > (1+pct*0.01)*price:
                # print("第高",possible_point)
                new_pivot = True
                change = True
                highlow = 1

            #　前高后高，且高出上个price水平，代替
            elif highlow ==1 and possible_point > price:
                # print("高高")
                change = True
                substitute = True
     
        #　找极小值
        else:
           possible_point = low(df,index,1,1,2)
           if possible_point != -1:
                #　前高后低，且低过跌幅，为新低点
                if highlow >= 0 and possible_point < (1-pct*0.01)*price:
                    new_pivot = True
                    change = True
                    highlow = -1
                    
                # 前低后低，且低于上个price, 代替
                elif highlow == -1 and possible_point < price:
                    change = True
                    substitute = True

                    
        #　２种改变
        if change == True:
            price = df.iloc[index-1,1]
            #　新点记录
            if new_pivot == True:
                df_record = df_record.append(df.iloc[index-1])
                new_pivot = False
            #代替
            elif substitute == True:
                df_record.iloc[-1,:] = df.iloc[index-1,:]
                substitute = False
            change = False
            
            
    df_record.reset_index(inplace=True)
    df_record = df_record.iloc[:,1:]              
    return df_record                


def zigzag2(df,amount):
    # 预设变量
    highlow = 0
    new_pivot = False
    substitute = False
    change = False
    price = df.iloc[0,1]
    
    df_record = df.head(1)
    
    
    # 前 2 个 bar 不能算， 否则和序列倒数比较
    for index in range(2,len(df)):
        possible_point = high(df,index,1,1,2)
        # print(index,possible_point)       
        #　找极大值，等于-1忽略
        if possible_point != -1:
            
            """
            highlow = 1 ==> 高点
            highlow = 0 ==> 起点
            highlow = -1 ==> 低点
            """
            # 前低后高，且高出涨幅，为新高点
            if highlow <= 0 and possible_point > price + amount*0.01:
                # print("第高",possible_point)
                new_pivot = True
                change = True
                highlow = 1

            #　前高后高，且高出上个price水平，代替
            elif highlow ==1 and possible_point > price:
                # print("高高")
                change = True
                substitute = True
     
        #　找极小值
        else:
           possible_point = low(df,index,1,1,2)
           if possible_point != -1:
                #　前高后低，且低过跌幅，为新低点
                if highlow >= 0 and possible_point < price - amount*0.01:
                    new_pivot = True
                    change = True
                    highlow = -1
                    
                # 前低后低，且低于上个price, 代替
                elif highlow == -1 and possible_point < price:
                    change = True
                    substitute = True

                    
        #　２种改变
        if change == True:
            price = df.iloc[index-1,1]
            #　新点记录
            if new_pivot == True:
                df_record = df_record.append(df.iloc[index-1])
                new_pivot = False
            #代替
            elif substitute == True:
                df_record.iloc[-1,:] = df.iloc[index-1,:]
                substitute = False
            change = False
            
            
    df_record.reset_index(inplace=True)
    df_record = df_record.iloc[:,1:]              
    return df_record                
                
# result = zigzag(df_tohandle,10)