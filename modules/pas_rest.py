import os
import requests
from dotenv import dotenv_values

config = dotenv_values(".env") 
if "Production" in config['CONF_REST']:
    REST_SERVER = config['REST_SERVER_PROD']
    REST_AUTH = config['REST_AUTH_PROD']
    REST_ENV = 'PAS PRODUCTION ENVIRONMENT'
else:
    REST_SERVER = config['REST_SERVER_TEST']
    REST_AUTH = config['REST_AUTH_TEST']
    REST_ENV = 'PAS TESTING ENVIRONMENT'
    
REST_PASS = tuple(REST_AUTH.split(","))
REST_URNUUID = config['REST_URNUUID']
REST_URL = REST_SERVER + REST_URNUUID

def get_status():
    url = REST_URL+"statistics/overview"
    authentication = REST_PASS
    try:
        response = requests.get(url, verify=False, auth=authentication)
    except Exception as e: 
        response = str(e)
        r_json = ""
    r_json = response.json()
    return r_json

def get_accepted_created(created):
    #Use ?* or /.*/ for Apache Lucene wildcard search
    url = REST_URL+"search?q=mets_dmdSec_CREATED:"+ created + " AND mets_OBJID:/.*/ AND mets_dmdSec_mdWrap_xmlData_lidoWrap_lido_administrativeMetadata_recordWrap_recordID:/.*/ &limit=1000"
    authentication = REST_PASS
    counter = 0
    try:
        response = requests.get(url, verify=False, auth=authentication)
        r_json = response.json()
        error = ""
        for result in r_json['data']['results']:
            counter = counter + 1
    except Exception as e: 
        error = str(e)
        counter = 0
        r_json = ""
    return r_json, counter, error

def get_accepted_mpid(mpid):
    #Use ?* or /.*/ for Apache Lucene wildcard search
    url = REST_URL+"search?q=mets_dmdSec_mdWrap_xmlData_lidoWrap_lido_administrativeMetadata_recordWrap_recordID:" + mpid + " AND mets_OBJID:/.*/ AND mets_dmdSec_CREATED:/.*/ &limit=1000"
    authentication = REST_PASS
    counter = 0
    try:
        response = requests.get(url, verify=False, auth=authentication)
        r_json = response.json()
        error = ""
        for result in r_json['data']['results']:
            counter = counter + 1
    except Exception as e: 
        error = str(e)
        counter = 0
        r_json = ""
    return r_json, counter, error

def get_accepted_mpinv(mpinv):
    #Use ?* or /.*/ for Apache Lucene wildcard search
    url = REST_URL+"search?q=mets_CONTENTID:" + mpinv + " AND mets_dmdSec_CREATED:/.*/ AND mets_dmdSec_mdWrap_xmlData_lidoWrap_lido_administrativeMetadata_recordWrap_recordID:/.*/ &limit=1000"
    authentication = REST_PASS
    counter = 0
    try:
        response = requests.get(url, verify=False, auth=authentication)
        r_json = response.json()
        error = ""
        for result in r_json['data']['results']:
            counter = counter + 1
    except Exception as e: 
        error = str(e)
        counter = 0
        r_json = ""
    return r_json, counter, error

def disseminate_aip(aipid):
    url = REST_URL+"preserved/" + aipid + "/disseminate?format=zip"
    authentication = REST_PASS
    try:
        response = requests.post(url, verify=False, auth=authentication)
        r_json = response.json()
        error = ""
    except Exception as e: 
        error = str(e)
        r_json = ""
    return r_json, error