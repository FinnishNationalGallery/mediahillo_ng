
def get_objects_by_id(object_id, const_url, const_auth):
    method = "GET"
    url = const_url +"/Object/" + object_id
    querystring = {"loadThumbnailMedium":"true"}
    payload = ""
    auth = const_auth
    headers = {
        'Content-Type': "application/xml",
        'cache-control': "no-cache"
        }
    return method, url, querystring, payload, auth, headers

def get_objects_by_number(number, const_url, const_auth):
    method = "POST"
    url = const_url +"/Object/search"
    querystring = {}
    payload = "<application><modules><module name=\"Object\">\n<search limit=\"500\" offset=\"0\" loadThumbnailSmall =\"true\">\n<select><field fieldPath=\"__id\"/> <field fieldPath=\"ObjObjectVrt\"/> </select>\n<fulltext>*</fulltext>\n<expert module=\"Object\"><and><startsWithField fieldPath=\"ObjObjectNumberVrt\" operand=\""+ number + "\"/></and>\n</expert>\n</search>\n</module>\n</modules>\n</application>"
    auth = const_auth
    headers = {
        'Content-Type': "application/xml",
        'cache-control': "no-cache"
        }
    return method, url, querystring, payload, auth, headers

def get_objects_by_title(title, const_url, const_auth):
    method = "POST"
    url = const_url +"/Object/search"
    querystring = {}
    payload = "<application><modules><module name=\"Object\">\n<search limit=\"500\" offset=\"0\" loadThumbnailSmall =\"true\">\n<select><field fieldPath=\"__id\"/> <field fieldPath=\"ObjObjectVrt\"/> </select>\n<fulltext>*</fulltext>\n<expert module=\"Object\"><and><equalsField fieldPath=\"__orgUnit\" operand=\"KGMuusa\"/>\n<contains fieldPath=\"ObjObjectTitleVrt\" operand=\""+ title	 + "\"/></and>\n</expert>\n</search>\n</module>\n</modules>\n</application>"
    auth = const_auth
    headers = {
        'Content-Type': "application/xml",
        'cache-control': "no-cache"
        }
    return method, url, querystring, payload, auth, headers

def get_mp_objects_by_paslog(const_url, const_auth):
    method = "POST"
    url = const_url +"/Object/search"
    querystring = {}
    #payload = "<application><modules><module name=\"Object\">\n<search limit=\"1000\" offset=\"0\" loadThumbnailSmall =\"true\">\n<select><field fieldPath=\"__id\"/> <field fieldPath=\"ObjObjectVrt\"/> </select>\n<fulltext>*</fulltext>\n<expert module=\"Object\"><and><isNotNull fieldPath=\"ObjPASLog01Clb\"/></and>\n</expert>\n</search>\n</module>\n</modules>\n</application>"
    payload = "<application><modules><module name=\"Object\">\n<search limit=\"10000\" offset=\"0\" loadThumbnailSmall =\"flase\">\n<select><field fieldPath=\"__id\"/> <field fieldPath=\"ObjObjectVrt\"/> <field fieldPath=\"ObjPASLog01Clb\"/> </select>\n<fulltext>*</fulltext>\n<expert module=\"Object\"><and><isNotNull fieldPath=\"ObjPASLog01Clb\"/></and>\n</expert>\n</search>\n</module>\n</modules>\n</application>"
    auth = const_auth
    headers = {
        'Content-Type': "application/xml",
        'cache-control': "no-cache"
        }
    return method, url, querystring, payload, auth, headers

def put_mplog_by_objid(objid, logtext, const_url, const_auth):
    method = "PUT"
    url = const_url +"/Object/" + objid
    querystring = {}
    payload = "<?xml version='1.0' encoding='UTF-8'?>\n<application xmlns=\"http://www.zetcom.com/ria/ws/module\">\n<modules>\n<module name=\"Object\">\n<moduleItem id=\""+ objid	 + "\">\n<dataField dataType=\"Clob\" name=\"ObjPASLog01Clb\">\n<value>\""+ logtext	 + "\"</value>\n</dataField>\n</moduleItem>\n</module>\n</modules>\n</application>"
    auth = const_auth
    headers = {
        'Content-Type': "application/xml",
        'cache-control': "no-cache"
        }
    return method, url, querystring, payload, auth, headers

def load_attachment_by_id(object_id, const_url, const_auth):
	method = "GET"
	url = const_url + "/Multimedia/"+object_id+"/attachment"
	querystring = {}
	payload = ""
	auth = const_auth
	headers = {
		'Accept': "application/octet-stream",
		}
	return method, url, querystring, payload, auth, headers

def get_report_by_number(object_id, report_id, const_url, const_auth):
	method = "GET"
	url = const_url +"/Object/" + object_id + "/export/" + report_id
	querystring = {}
	payload = ""
	auth = const_auth
	headers = {
        'Content-Type': "application/octet-stream",
        'cache-control': "no-cache"
        }
	return method, url, querystring, payload, auth, headers

###################################
### PARSE MuseumPlus XML OBJECT 
###################################
def parse_xml_object(xml_obj):
    xml_data ={}
    # -------------------- #
    __id = ""
    __orgUnit = ""
    __created = ""
    ObjPASLog01Clb = ""
    ObjManagOwnerNBA01Ref = ""
    ObjManagResponsibleNBA01Ref = ""
    ObjObjectNumberTxt = ""
    ObjObjectNumberVrt = ""
    ObjObjectTitleTxt = ""
    ObjObjectTitleVrt = ""
    ObjObjectTitleGrp = [] # Todo
    ObjPerAssociationRef = []
    ObjObjectVrt = ""
    ObjCategoryVoc = ""
    ObjClassificationsNBA01Grp = []
    ObjDateGrp_PreviewVrt = ""
    ObjDateGrp_YearFromLnu = ""
    ObjDimAllGrp_PreviewVrt = []
    ObjMultimediaRef_id = ""
    ObjMultimediaRef_name = ""
    ObjMultimediaRef = {}
    thumbnail = ""
    # ---------------
    # systemField
    # ---------------
    try:
        for systemField in xml_obj['application']['modules']['module']['moduleItem']['systemField']:
            if systemField['@name'] == '__id':
                __id = systemField['value']
            if systemField['@name'] == '__created':
                __created = systemField['value']
            if systemField['@name'] == '__orgUnit':
                __orgUnit = systemField['value']
    except:
        pass
    # ---------------
    # dataField
    # ---------------
    try:
        for dataField in xml_obj['application']['modules']['module']['moduleItem']['dataField']:
            if dataField['@name'] == 'ObjObjectNumberTxt':
                ObjObjectNumberTxt = dataField['value']
            if dataField['@name'] == 'ObjObjectTitleTxt':
                ObjObjectTitleTxt = dataField['value']
            if dataField['@name'] == 'ObjPASLog01Clb':
                ObjPASLog01Clb = dataField['value']
    except:
        pass
    # ---------------
    # virtualField
    # ---------------
    try:
        for virtualField in xml_obj['application']['modules']['module']['moduleItem']['virtualField']:
            if virtualField['@name'] == 'ObjObjectVrt':
                ObjObjectVrt = virtualField['value']
            if virtualField['@name'] == 'ObjObjectNumberVrt':
                ObjObjectNumberVrt = virtualField['value']
            if virtualField['@name'] == 'ObjObjectTitleVrt':
                ObjObjectTitleVrt = virtualField['value']
    except:
        pass
    # ---------------
    # vocabularyReference -Category
    # ---------------
    try: # one
        vocabularyReference = xml_obj['application']['modules']['module']['moduleItem']['vocabularyReference']
        ObjCategoryVoc = vocabularyReference['vocabularyReferenceItem']['formattedValue']['#text']
    except: # many
        try:
            for vocabularyReference in xml_obj['application']['modules']['module']['moduleItem']['vocabularyReference']:
                if vocabularyReference['@name'] == 'ObjCategoryVoc':
                    ObjCategoryVoc = vocabularyReference['vocabularyReferenceItem']['@name']
        except:
            pass
    # ---------------
    # repeatableGroup
    # ---------------
    try:
        for rGroup in xml_obj['application']['modules']['module']['moduleItem']['repeatableGroup']:
            # Classification
            if rGroup['@name'] == 'ObjClassificationsNBA01Grp':
                try: # one
                    ObjClassificationsNBA01Grp.append(rGroup['repeatableGroupItem']['vocabularyReference']['vocabularyReferenceItem']['@name'])
                except: # many
                    for rItem in rGroup['repeatableGroupItem']:
                        ObjClassificationsNBA01Grp.append(rItem['vocabularyReference']['vocabularyReferenceItem']['@name'])
            # Creation time
            if rGroup['@name'] == 'ObjDateGrp':
                try: # one
                    if rGroup['repeatableGroupItem']['virtualField']['@name'] =='PreviewVrt':
                        ObjDateGrp_PreviewVrt = rGroup['repeatableGroupItem']['virtualField']['value']
                    if rGroup['repeatableGroupItem']['dataField']['@name'] =='YearFromLnu':
                        ObjDateGrp_YearFromLnu = rGroup['repeatableGroupItem']['dataField']['value']
                except: # many
                    dummy = 'real dummy'
            # Measurements
            if rGroup['@name'] == 'ObjDimAllGrp':
                try: # one
                    if rGroup['repeatableGroupItem']['virtualField']['@name'] =='PreviewVrt':
                        ObjDimAllGrp_PreviewVrt.append(rGroup['repeatableGroupItem']['virtualField']['value'])
                except:
                    for rItem in rGroup['repeatableGroupItem']:
                        ObjDimAllGrp_PreviewVrt.append(rItem['virtualField']['value'])
                else:
                    pass
    except:
        pass
    try:
        for mReference in xml_obj['application']['modules']['module']['moduleItem']['moduleReference']:
            # Multimedia
            if mReference['@name'] == 'ObjMultimediaRef':
                try: # one
                    #if mReference['moduleReferenceItem']['dataField']['value'] == 'true': #ThumbnailBoo = true
                        ObjMultimediaRef_id = mReference['moduleReferenceItem']['@moduleItemId']
                        ObjMultimediaRef_name = mReference['moduleReferenceItem']['formattedValue']['#text']
                        temp = ObjMultimediaRef_name.split(',')
                        ObjMultimediaRef_name = temp[0].encode('utf8', 'replace')
                        temp_id = mReference['moduleReferenceItem']['@moduleItemId']
                        temp_name = mReference['moduleReferenceItem']['formattedValue']['#text']
                        temp_name2 = temp_name.split(',')
                        ObjMultimediaRef[temp_id] = temp_name2[0]#.encode('utf8', 'replace')
                except: # many
                    for mItem in mReference['moduleReferenceItem']:
                        try:
                            #if mItem['dataField']['value'] == 'true': # Attachment with ThumbnailBoo = true
                                ObjMultimediaRef_id = mItem['@moduleItemId']
                                ObjMultimediaRef_name = mItem['formattedValue']['#text']
                                temp = ObjMultimediaRef_name.split(',')
                                ObjMultimediaRef_name = temp[0]#.encode('utf8', 'replace')
                            # All other attachments
                            #
                        except:
                            pass
                        try:
                            temp_id = mItem['@moduleItemId']
                            temp_name = mItem['formattedValue']['#text']
                            temp_name2 = temp_name.split(',')
                            ObjMultimediaRef[temp_id] = temp_name2[0]#.encode('utf8', 'replace')
                        except:
                            dummy = 'real dummy'
            # Owner
            if mReference['@name'] == 'ObjManagOwnerNBA01Ref':
                try: # one
                    ObjManagOwnerNBA01Ref = mReference['moduleReferenceItem']['formattedValue']['#text']
                except: # many
                    ObjManagOwnerNBA01Ref = "Can there be several owners?"
            # Keeper
            if mReference['@name'] == 'ObjManagResponsibleNBA01Ref':
                try: # one
                    ObjManagResponsibleNBA01Ref = mReference['moduleReferenceItem']['formattedValue']['#text']
                except: # many
                    ObjManagResponsibleNBA01Ref = "Can there be several keepers?"
            # Persons
            if mReference['@name'] == 'ObjPerAssociationRef':
                try: # one
                    ObjPerAssociationRef.append(mReference['moduleReferenceItem']['formattedValue']['#text'])
                except: # many
                    for mItem in mReference['moduleReferenceItem']:
                        ObjPerAssociationRef.append(mItem['formattedValue']['#text'])
    except:
        pass
    # Thumbnail Base64
    try: # one
        thumbnail = xml_obj['application']['modules']['module']['moduleItem']['thumbnails']['thumbnail']['value']
    except:
        thumbnail = ''

    # -------------------- #
    xml_data["__id"] = __id
    xml_data["__orgUnit"] = __orgUnit
    xml_data["__created"] = __created 
    xml_data["ObjPASLog01Clb"] = ObjPASLog01Clb
    xml_data["ObjManagOwnerNBA01Ref"] = ObjManagOwnerNBA01Ref
    xml_data["ObjManagResponsibleNBA01Ref"] = ObjManagResponsibleNBA01Ref
    xml_data["ObjObjectNumberTxt"] = ObjObjectNumberTxt
    xml_data["ObjObjectNumberVrt"] = ObjObjectNumberVrt
    xml_data["ObjPerAssociationRef"] = ObjPerAssociationRef
    xml_data["ObjObjectTitleTxt"] = ObjObjectTitleTxt
    xml_data["ObjObjectTitleVrt"] = ObjObjectTitleVrt
    xml_data["ObjObjectTitleGrp"] = ObjObjectTitleGrp
    xml_data["ObjObjectVrt"] = ObjObjectVrt
    xml_data["ObjCategoryVoc"] = ObjCategoryVoc
    xml_data["ObjClassificationsNBA01Grp"] = ObjClassificationsNBA01Grp
    xml_data["ObjDateGrp_PreviewVrt"] = ObjDateGrp_PreviewVrt
    xml_data["ObjDateGrp_YearFromLnu"] = ObjDateGrp_YearFromLnu
    xml_data["ObjDimAllGrp_PreviewVrt"] = ObjDimAllGrp_PreviewVrt
    xml_data["ObjMultimediaRef_id"] = ObjMultimediaRef_id
    xml_data["ObjMultimediaRef_name"] = ObjMultimediaRef_name
    xml_data["ObjMultimediaRef"] = ObjMultimediaRef
    xml_data["thumbnail"] = thumbnail

    # -------------------- #
    return xml_data

###################################
### PARSE LIDO XML from MuseumPlus object XML
###################################
def parse_lido_xml(et, xml_data, LIDO_SOURCE):
    LIDO_NS = "http://www.lido-schema.org"
    XML_NS = "http://www.w3.org/XML/1998/namespace"
    XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
    schemaLocation = "http://www.lido-schema.org http://www.lido-schema.org/schema/v1.0/lido-v1.0.xsd"

    NS_MAP = {"lido": LIDO_NS,
              "xml": XML_NS
              }
    ##########
    ### Lido
    ##########
    rootName = et.QName(LIDO_NS, 'lidoWrap')
    root = et.Element(rootName, attrib={"{" + XSI_NS + "}schemaLocation" : schemaLocation}, nsmap=NS_MAP)
    ##########
    document = et.ElementTree(root)
    lido = et.SubElement(root, et.QName(LIDO_NS, "lido"))
    lidoRecID = et.SubElement(lido, et.QName(LIDO_NS, "lidoRecID"), attrib={"{" + LIDO_NS + "}source" : LIDO_SOURCE, "{" + LIDO_NS + "}type" : "ITEM"})
    lidoRecID.text = xml_data["ObjObjectNumberVrt"]
    ########## Descriptive Metadata
    descriptiveMetadata = et.SubElement(lido, et.QName(LIDO_NS, "descriptiveMetadata"), attrib={"{" + XML_NS + "}lang" : "fi"})
    # Object type
    objectClassificationWrap = et.SubElement(descriptiveMetadata, et.QName(LIDO_NS, "objectClassificationWrap"))
    objectWorkTypeWrap = et.SubElement(objectClassificationWrap, et.QName(LIDO_NS, "objectWorkTypeWrap"))
    objectWorkType = et.SubElement(objectWorkTypeWrap, et.QName(LIDO_NS, "objectWorkType"))
    objectWorkType_term = et.SubElement(objectWorkType, et.QName(LIDO_NS, "term"))
    objectWorkType_term.text = xml_data["ObjCategoryVoc"]
    # Classification
    classificationWrap = et.SubElement(objectClassificationWrap, et.QName(LIDO_NS, "classificationWrap"))
    classification_type = et.SubElement(classificationWrap, et.QName(LIDO_NS, "classification"), attrib={"{" + LIDO_NS + "}type" : "aineistotyyppi"})
    classification_term = et.SubElement(classification_type, et.QName(LIDO_NS, "term"), attrib={"{" + LIDO_NS + "}label" : "aineistotyyppi"})
    classification_term.text = xml_data["ObjCategoryVoc"]
    for textfield in xml_data["ObjClassificationsNBA01Grp"]:
        tempclass = textfield.split('##')
        tmp_class = tempclass[0]
        if "luokka" in tmp_class:
            tmp_classtext = tempclass[1]
            classification_type = et.SubElement(classificationWrap, et.QName(LIDO_NS, "classification"), attrib={"{" + LIDO_NS + "}type" : "luokitus"})
            classification_term = et.SubElement(classification_type, et.QName(LIDO_NS, "term"), attrib={"{" + LIDO_NS + "}label" : tmp_class})
            classification_term.text = tmp_classtext
    # Title
    objectIdentificationWrap = et.SubElement(descriptiveMetadata, et.QName(LIDO_NS, "objectIdentificationWrap"))
    objectIdentificationWrap_titleWrap = et.SubElement(objectIdentificationWrap, et.QName(LIDO_NS, "titleWrap"))
    objectIdentificationWrap_titleSet = et.SubElement(objectIdentificationWrap_titleWrap, et.QName(LIDO_NS, "titleSet"), attrib={"{" + LIDO_NS + "}type" : "nimi"})
    objectIdentificationWrap_appellationValue = et.SubElement(objectIdentificationWrap_titleSet, et.QName(LIDO_NS, "appellationValue"), attrib={"{" + XML_NS + "}lang" : "fi"})
    objectIdentificationWrap_appellationValue.text = xml_data["ObjObjectTitleVrt"]
    # Repository current
    repositoryWrap = et.SubElement(objectIdentificationWrap, et.QName(LIDO_NS, "repositoryWrap"))
    repositorySet = et.SubElement(repositoryWrap, et.QName(LIDO_NS, "repositorySet"), attrib={"{" + LIDO_NS + "}type" : "haltija"})
    repositoryName = et.SubElement(repositorySet, et.QName(LIDO_NS, "repositoryName"))
    legalBodyName = et.SubElement(repositoryName, et.QName(LIDO_NS, "legalBodyName"))
    appellationValue = et.SubElement(legalBodyName, et.QName(LIDO_NS, "appellationValue"))
    appellationValue.text = xml_data["ObjManagResponsibleNBA01Ref"]
    workID = et.SubElement(repositorySet, et.QName(LIDO_NS, "workID"), attrib={"{" + LIDO_NS + "}type" : "inventaarionumero"})
    workID.text = xml_data["ObjObjectNumberVrt"]
    # Event - Creator
    eventWrap = et.SubElement(descriptiveMetadata, et.QName(LIDO_NS, "eventWrap"))
    eventSet = et.SubElement(eventWrap, et.QName(LIDO_NS, "eventSet"))
    event = et.SubElement(eventSet, et.QName(LIDO_NS, "event"))
    eventType = et.SubElement(event, et.QName(LIDO_NS, "eventType"))
    eventType_term = et.SubElement(eventType, et.QName(LIDO_NS, "term"))
    eventType_term.text = "valmistus"

    for actorname in xml_data["ObjPerAssociationRef"]:
        eventActor = et.SubElement(event, et.QName(LIDO_NS, "eventActor"))
        actorInRole = et.SubElement(eventActor, et.QName(LIDO_NS, "actorInRole"))
        actor = et.SubElement(actorInRole, et.QName(LIDO_NS, "actor"))
        nameActorSet = et.SubElement(actor, et.QName(LIDO_NS, "nameActorSet"))
        appellationValue = et.SubElement(nameActorSet, et.QName(LIDO_NS, "appellationValue"))
        appellationValue.text = actorname
    eventDate = et.SubElement(event, et.QName(LIDO_NS, "eventDate"))
    displayDate = et.SubElement(eventDate, et.QName(LIDO_NS, "displayDate"))
    displayDate.text = xml_data["ObjDateGrp_PreviewVrt"]
    ########## Administrative Metadata
    administrativeMetadata = et.SubElement(lido, et.QName(LIDO_NS, "administrativeMetadata"), attrib={"{" + XML_NS + "}lang" : "fi"})
    recordWrap = et.SubElement(administrativeMetadata, et.QName(LIDO_NS, "recordWrap"))
    recordID = et.SubElement(recordWrap, et.QName(LIDO_NS, "recordID"), attrib={"{" + LIDO_NS + "}type" : "MuseumPlusObjectId"})
    recordID.text = xml_data["__id"]
    ###
    #session.__id = xml_data["__id"]
    ###
    recordType = et.SubElement(recordWrap, et.QName(LIDO_NS, "recordType"))
    recordType_term = et.SubElement(recordType, et.QName(LIDO_NS, "term"))
    recordType_term.text = "objekti"
    recordSource = et.SubElement(recordWrap, et.QName(LIDO_NS, "recordSource"))
    legalBodyName = et.SubElement(recordSource, et.QName(LIDO_NS, "legalBodyName"))
    legalBodyName_appellationValue = et.SubElement(legalBodyName, et.QName(LIDO_NS, "appellationValue"))
    legalBodyName_appellationValue.text = xml_data["ObjManagOwnerNBA01Ref"]
    recordInfoSet = et.SubElement(recordWrap, et.QName(LIDO_NS, "recordInfoSet"))
    recordMetadataDate = et.SubElement(recordInfoSet, et.QName(LIDO_NS, "recordMetadataDate"))
    recordMetadataDate.text = xml_data["__created"] #CreateDate
    ##########
    ### OUTPUT
    ##########
    output = et.tostring(document, pretty_print=True, encoding='utf8')
    return output