import os
import xmltodict
import datetime
import requests
from lxml import etree as et
from io import StringIO, BytesIO
from dotenv import dotenv_values
import modules.mp_api as mp_api

config = dotenv_values(".env") 
DATA_path = config['DATA_FOLDER']
METADATA_path = config['METADATA_FOLDER']
SIP_path = config['SIP_FOLDER']
LIDO_SOURCE = config['LIDO_SOURCE']
if "Production" in config['CONF_MP']:
    MP_URL = config['MP_PROD_URL'] 
    MP_PASSI = config['MP_PROD_PASS']
    MP_ENV = 'MuseumPlus PRODUCTION ENVIRONMENT'
else:
    MP_URL = config['MP_TEST_URL'] 
    MP_PASSI = config['MP_TEST_PASS']
    MP_ENV = 'MuseumPlus TESTING ENVIRONMENT'
MP_PASS = tuple(MP_PASSI.split(","))

def read_lido_xml():
    try:
        files = os.listdir(METADATA_path)
        classification1 = ""
        classification2 = ""
        classification3 = ""
        for file in files:
            if "lido_description.xml" in file:
                filepath = METADATA_path + file
                lidofile = open(filepath, "r")
                #xml_obj = xmltodict.parse(lidofile.read())
                # Määritellään nimiavaruuskartta "lido" -> "http://www.lido-schema.org"
                NS = {'lido': 'http://www.lido-schema.org'}
                # Luodaan ElementTree-olio
                tree = et.parse(filepath)
                root = tree.getroot()

                # 1) lidoRecID (teksti) + attribuutit (source, type)
                lido_rec_id_elem = root.find('.//lido:lidoRecID', NS)
                lido_rec_id = lido_rec_id_elem.text if lido_rec_id_elem is not None else None
                lido_rec_id_source = lido_rec_id_elem.get('{http://www.lido-schema.org}source') if lido_rec_id_elem is not None else None
                lido_rec_id_type = lido_rec_id_elem.get('{http://www.lido-schema.org}type') if lido_rec_id_elem is not None else None

                # 2) objectWorkType (esim. "Taideteos")
                object_work_type_elem = root.find('.//lido:objectWorkTypeWrap/lido:objectWorkType/lido:term', NS)
                object_work_type = object_work_type_elem.text if object_work_type_elem is not None else None

                # 3) classification-arvot:
                #    - aineistotyyppi = "Taideteos"
                #    - pääluokka = "mediataide"
                #    - erikoisluokka = "videoinstallaatio"
                classification_ain_elem = root.find('.//lido:classification[@lido:type="aineistotyyppi"]/lido:term', NS)
                classification_ain = classification_ain_elem.text if classification_ain_elem is not None else None

                classification_paa_elem = root.find('.//lido:classification[@lido:type="luokitus"]/lido:term[@lido:label="pääluokka"]', NS)
                classification_paa = classification_paa_elem.text if classification_paa_elem is not None else None

                classification_erik_elem = root.find('.//lido:classification[@lido:type="luokitus"]/lido:term[@lido:label="erikoisluokka"]', NS)
                classification_erik = classification_erik_elem.text if classification_erik_elem is not None else None

                # 4) Title ("Pyhiinvaellus")
                title_elem = root.find('.//lido:titleWrap/lido:titleSet/lido:appellationValue', NS)
                title = title_elem.text if title_elem is not None else None

                # 5) Repository (esim. "Kansallisgalleria / Nykytaiteen museo Kiasma")
                repository_elem = root.find('.//lido:repositorySet/lido:repositoryName/lido:legalBodyName/lido:appellationValue', NS)
                repository = repository_elem.text if repository_elem is not None else None

                # 6) WorkID ("N-2005-30")
                work_id_elem = root.find('.//lido:repositorySet/lido:workID', NS)
                work_id = work_id_elem.text if work_id_elem is not None else None

                # 7) eventType ("valmistus")
                event_type_elem = root.find('.//lido:event/lido:eventType/lido:term', NS)
                event_type = event_type_elem.text if event_type_elem is not None else None

                # 8) eventActor ("Rekula, Heli, Artist")
                event_actor_elem = root.find('.//lido:eventActor/lido:actorInRole/lido:actor/lido:nameActorSet/lido:appellationValue', NS)
                event_actor = event_actor_elem.text if event_actor_elem is not None else None

                # 9) eventDate ("valmistusaika: 1996 - 1998")
                event_date_elem = root.find('.//lido:eventDate/lido:displayDate', NS)
                event_date = event_date_elem.text if event_date_elem is not None else None

                # 10) recordID (MuseumPlusObjectId) = "624177"
                record_id_elem = root.find('.//lido:recordWrap/lido:recordID[@lido:type="MuseumPlusObjectId"]', NS)
                record_id = record_id_elem.text if record_id_elem is not None else None
                if record_id == None:
                    record_id_elem = root.find('.//lido:recordWrap/lido:recordID[@lido:type="ObjectId"]', NS)
                    record_id = record_id_elem.text if record_id_elem is not None else None    

                # 11) recordType ("objekti")
                record_type_elem = root.find('.//lido:recordWrap/lido:recordType/lido:term', NS)
                record_type = record_type_elem.text if record_type_elem is not None else None

                # 12) recordSource ("Suomen valtio")
                record_source_elem = root.find('.//lido:recordWrap/lido:recordSource/lido:legalBodyName/lido:appellationValue', NS)
                record_source = record_source_elem.text if record_source_elem is not None else None

                # 13) recordMetadataDate ("2018-04-12 13:43:47.426")
                record_metadata_date_elem = root.find('.//lido:recordWrap/lido:recordInfoSet/lido:recordMetadataDate', NS)
                record_metadata_date = record_metadata_date_elem.text if record_metadata_date_elem is not None else None
                if record_metadata_date_elem is not None:
                    CreatedDateISO = record_metadata_date.replace(" ", "T")
                    record_metadata_date = CreatedDateISO
                ###
                lidofile.close()
                ### 
                data = {
                    "lidoRecID": lido_rec_id,
                    "lidoRecID_source": lido_rec_id_source,
                    "lidoRecID_type": lido_rec_id_type,
                    "objectWorkType": object_work_type,
                    "classification1": classification_ain,
                    "classification2": classification_paa,
                    "classification3": classification_erik,
                    "mp_name": title,
                    "mp_repository": repository,
                    "mp_inv": work_id,
                    "eventType": event_type,
                    "mp_actor": event_actor,
                    "mp_creation": event_date,
                    "mp_id": record_id,
                    "recordType": record_type,
                    "mp_owner": record_source,
                    "mp_created": record_metadata_date
                }
    except Exception as e: 
        data = {
            "mp_name": "Error: " + str(e)
        }

    if not os.path.exists(METADATA_path + "lido_description.xml"):
        data = {
            "mp_name": "No file detected!"
        }

    return data

def read_lido_xml_backup():
    try:
        files = os.listdir(METADATA_path)
        classification1 = ""
        classification2 = ""
        classification3 = ""
        for file in files:
            if "lido_description.xml" in file:
                filepath = METADATA_path + file
                lidofile = open(filepath, "r")
                xml_obj = xmltodict.parse(lidofile.read())

                classifications = xml_obj['lido:lidoWrap']['lido:lido']['lido:descriptiveMetadata']['lido:objectClassificationWrap']['lido:classificationWrap']['lido:classification']
                for classification in classifications:
                    if classification['@lido:type'] == 'aineistotyyppi':
                        classification1 = classification['lido:term']['#text']
                    elif classification['@lido:type'] == 'luokitus' and classification['lido:term']['@lido:label'] == 'pääluokka':
                        classification2 = classification['lido:term']['#text']
                    elif classification['@lido:type'] == 'luokitus' and classification['lido:term']['@lido:label'] == 'erikoisluokka':
                        classification3 = classification['lido:term']['#text']


                mp_name = xml_obj['lido:lidoWrap']['lido:lido']['lido:descriptiveMetadata']['lido:objectIdentificationWrap']['lido:titleWrap']['lido:titleSet']['lido:appellationValue']['#text']

                recordWrap = xml_obj['lido:lidoWrap']['lido:lido']['lido:administrativeMetadata']['lido:recordWrap']
                mp_inv = xml_obj['lido:lidoWrap']['lido:lido']['lido:lidoRecID']['#text']
                mp_id = recordWrap['lido:recordID']['#text']
                mp_owner = recordWrap['lido:recordSource']['lido:legalBodyName']['lido:appellationValue']

                # Tarkista, onko 'lido:recordInfoSet' olemassa
                recordInfoSet = recordWrap.get('lido:recordInfoSet')
                if recordInfoSet:
                    # Tarkista, onko 'lido:recordMetadataDate' olemassa
                    recordMetadataDate = recordInfoSet.get('lido:recordMetadataDate')
                    if not recordMetadataDate:  # Jos avain puuttuu tai sen arvo on None
                        mp_created = datetime.datetime.now().isoformat()
                    elif isinstance(recordMetadataDate, dict) and recordMetadataDate.get('#text', '').strip() == "":
                        # Jos sisältö on sanakirja, mutta tekstikenttä on tyhjä
                        mp_created = datetime.datetime.now().isoformat()
                    else:
                        # Jos sisältö on tekstiä tai sanakirjan '#text'-avain sisältää arvoja
                        CreatedDate = recordMetadataDate if isinstance(recordMetadataDate, str) else recordMetadataDate.get('#text', '').strip()
                        CreatedDateISO = CreatedDate.replace(" ", "T")
                        mp_created = CreatedDateISO
                else:
                    # Jos 'lido:recordInfoSet' puuttuu kokonaan
                    mp_created = datetime.datetime.now().isoformat()
                    
                lidofile.close()
                ### 
                data = {
                    "classification1": classification1,
                    "classification2": classification2,
                    "classification3": classification3,
                    "mp_inv": mp_inv,
                    "mp_id": mp_id,
                    "mp_name": mp_name,
                    "mp_created": mp_created,
                    "mp_owner": mp_owner
                }
    except Exception as e: 
        data = {
            "mp_name": "Error: " + str(e)
        }

    if not os.path.exists(METADATA_path + "lido_description.xml"):
        data = {
            "mp_name": "No file detected!"
        }

    return data

def read_mets_lido_xml():
    try:
        files = os.listdir(SIP_path)
        for file in files:
            if "mets.xml" in file:
                filepath = SIP_path + file
                metsfile = open(filepath, "r")
                xml_obj = xmltodict.parse(metsfile.read())
                lido_wrap = xml_obj['mets:mets']['mets:dmdSec']['mets:mdWrap']['mets:xmlData']['lido:lidoWrap']
                lido_name = lido_wrap['lido:lido']['lido:descriptiveMetadata']['lido:objectIdentificationWrap']['lido:titleWrap']['lido:titleSet']['lido:appellationValue']['#text']
                lido_inv = lido_wrap['lido:lido']['lido:lidoRecID']['#text']
                recordWrap = lido_wrap['lido:lido']['lido:administrativeMetadata']['lido:recordWrap']
                lido_id = recordWrap['lido:recordID']['#text']
                if recordWrap['lido:recordInfoSet']['lido:recordMetadataDate'] == None:
                    lido_created = datetime.datetime.now().isoformat()
                else:
                    CreatedDate = recordWrap['lido:recordInfoSet']['lido:recordMetadataDate']
                    CreatedDateISO = CreatedDate.replace(" ", "T")
                    lido_created = CreatedDateISO
                metsfile.close()
    except Exception as e:
        lido_inv = ""
        lido_id = ""
        lido_name = "Error: " +str(e)
        lido_created = ""
    if not os.path.exists(SIP_path + "mets.xml"):
        lido_inv = ""
        lido_id = ""
        lido_name = ""
        lido_created = ""
    return lido_inv, lido_id, lido_name, lido_created

def save_object_by_id(object_id):
    thumb_stat = False
    ria = mp_api.get_objects_by_id(object_id, MP_URL, MP_PASS)
    try:
        mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
        input = BytesIO(mp_response.content)
        xml = et.parse(input)
        ###
        file = open(DATA_path+"MP_obj_id_"+object_id+".xml", "w")
        byte_string = et.tostring(xml)
        regular_string = byte_string.decode('utf-8')
        file.write(regular_string)
        file.close()
        ###
        message = ""
    except Exception as e: 
        message = str(e)
    return message

def get_object_by_id(object_id):
    thumb_status = False
    ria = mp_api.get_objects_by_id(object_id, MP_URL, MP_PASS)
    try:
        mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
        input = BytesIO(mp_response.content)
        xml_data ={}
        xml_obj = xmltodict.parse(input)
        xml_data = mp_api.parse_xml_object(xml_obj)
        if len(xml_data["thumbnail"]) > 0:
            thumb_status = True
    except:
        pass
    return xml_data, thumb_status

def load_attachment(object_id):
    ria = mp_api.load_attachment_by_id(object_id, MP_URL, MP_PASS)
    mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
    input = BytesIO(mp_response.content)
    return input

def get_object_by_number(object_inv):
    ria = mp_api.get_objects_by_number(object_inv, MP_URL, MP_PASS)
    mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
    input = BytesIO(mp_response.content)
    try:
        tree = et.parse(input)
    except:
        totalSize="0"
        mylist=[["1","Error:"],["2","MuseumPlus API interface:"],["3","503 Service Temporarily Unavailable"]]
        xml=""
        return totalSize, mylist, xml
    mylist = []
    totalSize="0"
    xml=""
    ns_mod = {'ns':'http://www.zetcom.com/ria/ws/module'}
    ###############################################
    def get_values(element):
        name = element.attrib['name']
        value = element.xpath('./ns:value/text()', namespaces = ns_mod)
        if not value:
            value = ['']
        list = [name, value[0]]
        return list
    ###############################################
    def get_thumbnail(element):
        name = "thumbnail=" + element.attrib['size']
        value = element.xpath('./ns:value/text()', namespaces = ns_mod)
        if not value:
            value = ['']
        list = [name, value[0]]
        return list
    ###############################################
    for element in tree.iter():
        try:
            totalSize = element.attrib['totalSize']
        except:
            pass
        try:
            name = element.attrib['name']
            list = get_values(element)
            mylist.append(list)
        except:
            pass
        try:
            name = element.attrib['size']
            list = get_thumbnail(element)
            mylist.append(list)
        except:
            pass
    output = et.tostring(tree, pretty_print=True, encoding='utf8') # For testing
    return totalSize, mylist, output

def get_object_by_title(title):
    ria = mp_api.get_objects_by_title(title, MP_URL, MP_PASS)
    try:
        mp_response = requests.request(method=ria[0], url=ria[1], verify=True,
                                       params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
        mp_response.raise_for_status()  # Nostaa poikkeuksen, jos status code on virheellinen
    except requests.exceptions.RequestException as error:
        totalSize = "0"
        mylist = [["1", "Error:"], ["2", "MuseumPlus API interface:"], ["3", str(error)]]
        xml = ""
        return totalSize, mylist, xml

    input = BytesIO(mp_response.content)
    try:
        tree = et.parse(input)
    except Exception as error:
        totalSize = "0"
        mylist = [["1", "Error:"], ["2", "MuseumPlus API interface:"], ["3", str(error)]]
        xml = ""
        return totalSize, mylist, xml

    mylist = []
    totalSize = "0"
    xml = ""
    ns_mod = {'ns': 'http://www.zetcom.com/ria/ws/module'}

    def get_values(element):
        name = element.attrib['name']
        value = element.xpath('./ns:value/text()', namespaces=ns_mod)
        if not value:
            value = ['']
        return [name, value[0]]

    def get_thumbnail(element):
        name = "thumbnail=" + element.attrib['size']
        value = element.xpath('./ns:value/text()', namespaces=ns_mod)
        if not value:
            value = ['']
        return [name, value[0]]

    for element in tree.iter():
        try:
            totalSize = element.attrib['totalSize']
        except:
            pass
        try:
            list_item = get_values(element)
            mylist.append(list_item)
        except:
            pass
        try:
            list_item = get_thumbnail(element)
            mylist.append(list_item)
        except:
            pass

    output = et.tostring(tree, pretty_print=True, encoding='utf8')
    return totalSize, mylist, output


def create_lido_xml(object_id):
    #session.back_link_id = request.env.http_referer
    thumb_stat = False
    ria = mp_api.get_objects_by_id(object_id, MP_URL, MP_PASS)
    mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
    input = BytesIO(mp_response.content)
    xml_data ={}
    xml_obj = xmltodict.parse(input)
    xml_data = mp_api.parse_xml_object(xml_obj)
    ###
    output = mp_api.parse_lido_xml(et, xml_data, LIDO_SOURCE)

    file = open(METADATA_path+"lido_description.xml", "w")
    regular_string = output.decode('utf-8')
    file.write(str(regular_string))
    file.close()
    ###
    message = ""
    return message



##############################
### ANOTHER WAY TO DO THIS ###
##############################
def get_object_by_id_dev(object_id):
    thumb_stat = False
    ria = mp_api.get_objects_by_id(object_id, MP_URL, MP_PASS)
    mp_response = requests.request(method=ria[0], url=ria[1], verify=True, params=ria[2], data=ria[3], auth=ria[4], headers=ria[5])
    input = BytesIO(mp_response.content)
    ###############################################
    xml_parse = et.parse(input)
    xml_parsed = et.tostring(xml_parse, encoding="unicode", pretty_print=True)
    tree = xml_parse
    mydict = {}
    ns_mod = {'ns':'http://www.zetcom.com/ria/ws/module'}
    ###>>>
    def get_values(element):
        name = element.attrib['name']
        value = element.xpath('./ns:value/text()', namespaces = ns_mod)
        if not value: 
            value = ['']
        list = [name, value[0]]
        return list
    ###>>>
    for element in tree.xpath('//ns:moduleItem/ns:systemField', namespaces = ns_mod):
        list = get_values(element)
        mydict[list[0]] = list[1]
    for element in tree.xpath('//ns:moduleItem/ns:dataField', namespaces = ns_mod):
        list = get_values(element)
        mydict[list[0]] = list[1]
    for element in tree.xpath('//ns:moduleItem/ns:virtualField', namespaces = ns_mod):
        list = get_values(element)
        mydict[list[0]] = list[1]
    for element in tree.xpath('//ns:moduleItem/ns:thumbnails/ns:thumbnail/ns:value/text()', namespaces = ns_mod):
        list = ["thumbnail", element]
        thumbnail = element
        mydict[list[0]] = list[1]
        thumb_stat = True
    ###############################################
    xml_data ={}
    xml_obj = xmltodict.parse(input)
    xml_data = mp_api.parse_xml_object(xml_obj)
    ###############################################
    return xml_parsed, mydict, thumb_stat, xml_data

