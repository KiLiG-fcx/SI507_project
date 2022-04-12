#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import numpy as np
import os,re,us
import json
import plotly.express as px
px.set_mapbox_access_token("pk.eyJ1IjoiZmN4LWtpbGlnIiwiYSI6ImNsMHIwaG5rODJmY2QzYnM1NW1rcHRjOHMifQ.1kdhIW8dwvtyNDFHOCyx5g")
API_Key = 'pzFDw36S40GxhJLXmtLYN4MfW'
API_Key_Secret = 'bV7FUFPK4Eaqmts26r26POmC7JNlgyt7vSdR63QDEHSms8UL5J'
Bearer_Token = 'AAAAAAAAAAAAAAAAAAAAAKGFbQEAAAAAWcrusWRsy0QE3lLWsvF7lPbnJfc%3DyWDpEWxNK1yLhFsRjSe7c9v5HoGXqIcX88Qmr4QGRI38lfgn15'
Access_Token = '1506028898525450241-LqmCE8DmRY7KSMOJL0WXULWyr7iA8D'
Access_Token_Secret = 'IXeFTTYLsXhc6lCt5POk7dgtH4No42dvtA4ZeHPxSp7DO'


# In[2]:


class Site:
    def __init__(self,json=None):
        self.statecode=json['state_code']
        self.latitude=json['latitude']
        self.longitude=json['longitude']
        self.airdata=AirQuality(json)


# In[3]:


def addpollutant(json):
    pollutants={}
    if (json['parameter_code']=="42401"):
        pollutants['SO2']=json['arithmetic_mean']
    elif (json['parameter_code']=="42101"):
        pollutants['CO']=json['arithmetic_mean']
    elif (json['parameter_code']=="42602"):
        pollutants['NO2']=json['arithmetic_mean']
    elif (json['parameter_code']=="44201"):
        pollutants['Ozone']=json['arithmetic_mean']
    elif (json['parameter_code']=="81102"):
        pollutants['PM10']=json['arithmetic_mean']
    elif (json['parameter_code']=="88101"):
        pollutants['PM25']=json['arithmetic_mean']
    return pollutants

class AirQuality:
    def __init__(self,json=None):
        self.aqi=0
        if (json['aqi']!='null'):
            self.aqi=json['aqi']
        self.pollutants=addpollutant(json)
        #print(self.pollutants)      


# In[4]:


search_url = "https://api.twitter.com/2/tweets/search/recent"
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {Bearer_Token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    #print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


# In[5]:


def get_pop(json):
    result=0
    for v in json['public_metrics'].values():
        result += v
    return result


# In[6]:


class Tweet:
    def __init__(self,json):
        self.id=json['id']
        self.text=json['text']
        self.popularity=get_pop(json)


# In[63]:


def getalltweets(fips,num):
    StateName=us.states.lookup(str(fips)).name
    query=f"{StateName} pollution"
    query_params={
        'query':query,
        'max_results':num,
        'tweet.fields':'public_metrics'
    }
    result=[]
    c=connect_to_endpoint(search_url,query_params)
    #print(c['data'])
    try:
        for items in c['data']:
            result.append(Tweet(items))
        return c['data'],result
    except:
        result.append('No data recently!')
        return {},result
    #return c['data'],result


# In[64]:


class StateNews:
    def __init__(self,fips=1,num=10):
        self.state=us.states.lookup(str(fips)).name
        self.json, self.tweet=getalltweets(fips,num)
        self.number=num


# In[9]:


sitefile='air_cache.json'  # cache for air pollution data archived site
tweetfile='tweet_cache.json'  # cache for daily tweets capture
def open_cache(filename):
    try:
        cache_file = open(filename, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(filename,cache_dict):
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(filename,"w")
    fw.write(dumped_json_cache)
    fw.close() 


# In[10]:


base_url="https://aqs.epa.gov/data/api/dailyData/byState?email=mingyuli@umich.edu&key=greenkit68&param="
pollutant_para={'co':"42101",'so2':"42401",'no2':"42602",'ozone':"44201",'pm10':"81102",'pm25':"88101"}
# sample: 45201&bdate=20210515&edate=20210515&state=37"

def geturl(pollutant_name,fips,date):
    url=base_url+pollutant_para[pollutant_name]+"&bdate="+date+"&edate="+date+"&state="+str(fips).zfill(2)
    return url

def getjson(url):
    return requests.get(url).json()['Data']


# In[39]:


site_cache={}  # used for caching
allsites=[]  #  used to create data plots

# capture data for co_test
##  This will be modified as plotly callback function afterwards

for date in range(20211101,20211102):
    for fips in range(26,28):
        url=geturl("co",str(fips),str(date))
        jsondata=getjson(url)
        have_captured=("co"+str(fips).zfill(2)+str(date))
        site_cache[have_captured]=jsondata  # save cache
        for i in range(len(jsondata)):
            allsites.append(Site(jsondata[i]))
            
save_cache(sitefile,site_cache)

for fips in range(26,29):
    have_captured=("co"+str(fips)+"20211101")
    dic=open_cache(sitefile)
    if (have_captured in dic.keys()):
        print("Cache used! ")
    else:
        print("No cache")


# In[68]:


import datetime
now = datetime.datetime.now()
#print(now.year, now.month, now.day, now.hour)
alltweet=[]
tweet_cache={}

for fips in range(26,29):
    news=StateNews(fips,10)
    alltweet.append(news)
    tweet_cache[str(fips)+str(now.hour)]=news.json

save_cache(tweetfile,tweet_cache)

for tw in range(26,33):
    if ((str(tw)+str(now.hour)) in open_cache(tweetfile)):
        print('Cache found!')
    else:
        print('No cache!')


# In[ ]:




