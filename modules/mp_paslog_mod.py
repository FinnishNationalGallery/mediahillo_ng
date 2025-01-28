import requests
from lxml import etree as et
from io import BytesIO
from dotenv import dotenv_values
import modules.mp_api as mp_api

config = dotenv_values(".env") 
DATA_path = config['DATA_FOLDER']
METADATA_path = config['METADATA_FOLDER']
#
if "Production" in config['CONF_PASLOG']:
    MP_URL = config['MP_PROD_URL'] 
    MP_PASSI = config['MP_PROD_PASS']
    MP_ENV = 'MuseumPlus PRODUCTION ENVIRONMENT'
else:
    MP_URL = config['MP_TEST_URL'] 
    MP_PASSI = config['MP_TEST_PASS']
    MP_ENV = 'MuseumPlus TESTING ENVIRONMENT'
MP_PASS = tuple(MP_PASSI.split(","))
MP_PASSI_WRITE = config['MP_TEST_PASS_WRITE']
MP_PASS_WRITE = tuple(MP_PASSI_WRITE.split(","))
#
if "Production" in config['CONF_PASLOG']:
    REST_SERVER = config['REST_SERVER_PROD']
    REST_AUTH = config['REST_AUTH_PROD']
    REST_ENV = 'CSC-PAS PRODUCTION ENVIRONMENT'
else:
    REST_SERVER = config['REST_SERVER_TEST']
    REST_AUTH = config['REST_AUTH_TEST']
    REST_ENV = 'CSC-PAS TESTING ENVIRONMENT'
REST_PASS = tuple(REST_AUTH.split(","))
REST_URNUUID = config['REST_URNUUID']
REST_URL = REST_SERVER + REST_URNUUID


# This is better way to parse XML response
def get_mp_object_by_paslog():
    ria = mp_api.get_mp_objects_by_paslog(MP_URL, MP_PASS)
    mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
    input = BytesIO(mp_response.content)
    tree = et.parse(input)
    totalSize = "0"
    mydict ={}
    ###
    ns_mod = {'ns':'http://www.zetcom.com/ria/ws/module'}
    root = tree.getroot()
    # Find all moduleItem elements
    module_items = root.findall('.//ns:moduleItem', namespaces=ns_mod)
    module_element = root.find('.//ns:module', namespaces=ns_mod)
    if module_element is not None:
        totalSize = module_element.get('totalSize')
    else:
        totalSize = "TotalSize attribute not found in the XML."
    for module_item in module_items:
        __id = module_item.find('./ns:systemField[@name="__id"]/ns:value', namespaces=ns_mod).text
        obj_object_vrt = module_item.find('./ns:virtualField[@name="ObjObjectVrt"]/ns:value', namespaces=ns_mod).text
        obj_pas_log_01_clb = module_item.find('./ns:dataField[@name="ObjPASLog01Clb"]/ns:value', namespaces=ns_mod).text
        thumbnail_element = module_item.find('./ns:thumbnails/ns:thumbnail[@size="small"]/ns:value', namespaces=ns_mod)
        if thumbnail_element is not None and thumbnail_element.text is not None:
            thumbnail = thumbnail_element.text
        else:
            thumbnail = None
        #mydict[__id] = {'ObjObjectVrt': obj_object_vrt, 'Thumbnail': thumbnail}
        #mydict[__id] = obj_object_vrt
        mydict[__id] = {'ObjPASLog01Clb': obj_pas_log_01_clb, 'ObjObjectVrt': obj_object_vrt}
    output = et.tostring(tree, pretty_print=True, encoding='utf8') # For testing purposes
    return totalSize, mydict, output

def get_accepted_created_by_id(created):
    #url = REST_URL+"search?q=OBJID:* AND mets_dmdSec_mdWrap_xmlData_lidoWrap_lido_administrativeMetadata_recordWrap_recordID:*"
    url = REST_URL+"search?q=mets_dmdSec_CREATED:"+ created + " mets_dmdSec_mdWrap_xmlData_lidoWrap_lido_administrativeMetadata_recordWrap_recordID:/.*/ &limit=1000"
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

def set_paslog_data(obj_id, aipid, timestamp):
    log_text = "PAS arkistointi: AIP-ID= " + aipid + " " + " Timestamp= " +timestamp
    ria = mp_api.put_mplog_by_objid(obj_id, log_text, MP_URL, MP_PASS_WRITE)
    try:
        mp_response = requests.request(method=ria[0], url=ria[1], verify=False, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
        response_status = mp_response.status_code
    except Exception as e: 
        error = str(e)
        return f'Error writing data to MuseumPlus API: {str(e)}', 500
    return response_status