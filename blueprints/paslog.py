
from flask import Blueprint, render_template, request, url_for, flash, redirect, send_file, session, jsonify
from flask_login import login_required, current_user
import modules.mp_paslog_mod as mp_paslog_mod
from models import db_paslog_mp, db_paslog_csc
from extensions import db
from sqlalchemy import or_, and_, func

paslog_bp = Blueprint('paslog', __name__)

@paslog_bp.route("/paslog_index")
@login_required
def paslog_index():
    return render_template('paslog_index.html', environment=mp_paslog_mod.MP_ENV, environment2=mp_paslog_mod.REST_ENV)

@paslog_bp.route("/get_csc_paslog")
@login_required
def get_csc_paslog():
    error = ""
    try:
        r_json, counter, error = mp_paslog_mod.get_accepted_created_by_id("?*")
        if 'status' in r_json and 'data' in r_json and 'results' in r_json['data']: 
            results = r_json['data']['results'] 
        for result in results: 
            # Check if same ID is already in database
            check_csc_id = db_paslog_csc.query.filter_by(pas_id = result['id']).all()
            if check_csc_id == []: # If same ID not found, then insert to database
                pas_mp_id =result['match']['mets_dmdSec_mdWrap_xmlData_lidoWrap_lido_administrativeMetadata_recordWrap_recordID'][0]
                pas_id = result['id'] 
                if 'lastmoddate' in result:
                    pas_created = result['lastmoddate'][-1] 
                else:
                    pas_created = result['createdate']
                ###
                pas_location = result['location'] 
                paslog_mark = db_paslog_csc(pas_mp_id = pas_mp_id, pas_id = pas_id, pas_created = pas_created, pas_location = pas_location)
                db.session.add(paslog_mark)
                db.session.commit()
            else:
                csc_update = db_paslog_csc.query.filter_by(pas_id = result['id']).first()
                csc_update.pas_mp_id =result['match']['mets_dmdSec_mdWrap_xmlData_lidoWrap_lido_administrativeMetadata_recordWrap_recordID'][0]
                csc_update.pas_id = result['id'] 
                if 'lastmoddate' in result:
                    csc_update.pas_created = result['lastmoddate'][-1] 
                else:
                    csc_update.pas_created = result['createdate']
                ###
                csc_update.pas_location = result['location'] 
                db.session.commit()
    except Exception as e:
        return f'Error reading CSC API: {str(e)}', 500
    objects = r_json #['data']['results']
    return render_template('paslog_csc_accepted.html', totalSize=counter, objects=objects, error=error)

@paslog_bp.route("/get_mp_paslog")
@login_required
def get_mp_paslog():
    try:
        totalSize, mydict, xml = mp_paslog_mod.get_mp_object_by_paslog()
        for key, value in mydict.items():
            # Check if same ID is already in database
            check_mp_id = db_paslog_mp.query.filter_by(mp_id = key).all()
            ###
            if check_mp_id == []: # If same ID not found, then insert to database
                paslog_mark = db_paslog_mp(mp_id = key, mp_name = value["ObjObjectVrt"], mp_paslog = value["ObjPASLog01Clb"])
                db.session.add(paslog_mark)
                db.session.commit()
            else:
                # Update mp_name value if same ID is found
                mp_update = db_paslog_mp.query.filter_by(mp_id=key).first()
                mp_update.mp_name = value["ObjObjectVrt"]
                mp_update.mp_paslog = value["ObjPASLog01Clb"]
                db.session.commit()
            ###
            check_csc_mp_id = db_paslog_csc.query.filter_by(pas_mp_id = key).all()
            ###
            if check_csc_mp_id == []: # If same ID not found
                pass
            else: # In case same ID found
                csc_update = db_paslog_csc.query.filter_by(pas_mp_id = key).first()
                csc_update.mp_paslog = value["ObjPASLog01Clb"]
                db.session.add(csc_update)
                db.session.commit()
    except Exception as e:
        return f'Error fetching MP data: {str(e)}', 500
    return render_template('paslog_mp_marked.html', totalSize=totalSize, objects=mydict, xml=xml)

@paslog_bp.route('/paslog_show_data')
@login_required
def paslog_show_data():
    class Paslog:
        def __init__(self, id, pas_mp_id, pas_created, pas_id, mp_paslog):
            self.id = id
            self.pas_mp_id = pas_mp_id
            self.pas_created = pas_created
            self.pas_id = pas_id
            self.mp_paslog = mp_paslog

    pdata = []
    try:
        # Hae “ei-merkityt”: NULL, tyhjä tai whitespace
        data = (
            db.session.query(db_paslog_csc)
            .filter(
                or_(
                    db_paslog_csc.mp_paslog.is_(None),
                    func.trim(db_paslog_csc.mp_paslog) == ''
                )
            )
            .order_by(db_paslog_csc.pas_created.desc())
            .all()
        )

        for row in data:
            # Onko sama pas_mp_id jo merkattu (ei-tyhjä ja ei-NULL)?
            check = (
                db.session.query(db_paslog_csc)
                .filter(
                    db_paslog_csc.pas_mp_id == row.pas_mp_id,
                    and_(
                        db_paslog_csc.mp_paslog.isnot(None),
                        func.length(func.trim(db_paslog_csc.mp_paslog)) > 0
                    )
                )
                .all()
            )

            if not check:  # ei merkintää -> näytetään
                pdata.append(Paslog(
                    id=row.id,
                    pas_mp_id=row.pas_mp_id,
                    pas_created=row.pas_created,
                    pas_id=row.pas_id,
                    mp_paslog=row.mp_paslog
                ))

        totalSize = len(pdata)
        return render_template('paslog_show_data.html', data=pdata, totalSize=totalSize)

    except Exception as e:
        return f'Error fetching MP marked data: {str(e)}', 500

'''
@paslog_bp.route('/paslog_show_data')
@login_required
def paslog_show_data():
    # Define the Paslog class (move this outside the function if possible)
    class Paslog:
        def __init__(self, id, pas_mp_id, pas_created, pas_id, mp_paslog):
            self.id = id
            self.pas_mp_id = pas_mp_id
            self.pas_created = pas_created
            self.pas_id = pas_id
            self.mp_paslog = mp_paslog

    # Create an empty list to store Paslog objects
    pdata = []
    try:
        # Use is_ for NULL comparison
        data = db.session.query(db_paslog_csc).filter(db_paslog_csc.mp_paslog.is_(None)).order_by(db_paslog_csc.pas_created.desc()).all()
        
        for row in data:
            donotmark = False
            # Check if there is already log mark made by same MuseumPlus ID
            check = db.session.query(db_paslog_csc).filter(
                db_paslog_csc.pas_mp_id == row.pas_mp_id, 
                db_paslog_csc.mp_paslog.isnot(None)
            ).all()
            
            # Modified check logic
            for p in check:
                # Check for non-empty mp_paslog
                if p.mp_paslog:  # This handles both non-None and non-empty string cases
                    donotmark = True
                    break  # Exit the loop once a mark is found
            
            # Only append if not marked
            if not donotmark:
                pdata.append(Paslog(
                    id=row.id, 
                    pas_mp_id=row.pas_mp_id, 
                    pas_created=row.pas_created, 
                    pas_id=row.pas_id, 
                    mp_paslog=row.mp_paslog
                ))
        
        totalSize = len(pdata)
        return render_template('paslog_show_data.html', data=pdata, totalSize=totalSize)
    
    except Exception as e:
        # Use proper error logging in production
        # current_app.logger.error(f'Error fetching MP marked data: {str(e)}')
        return f'Error fetching MP marked data: {str(e)}', 500
'''

@paslog_bp.route('/paslog_put_mark/', methods=['GET', 'POST'])
@login_required
def paslog_put_mark():
    obj_id = request.args.get('obj_id')
    aipid = request.args.get('aipid')
    timestamp = request.args.get('timestamp')
    response_status = mp_paslog_mod.set_paslog_data(obj_id, aipid, timestamp)
    # Status code 204 = OK, code 400 = Bad request, 403 = Forbidden
    # return f'Status code: {response_status}', 200
    if response_status == 204:
        try:
            #paslog_update = db_paslog_csc.query.filter_by(pas_mp_id=obj_id).first()
            paslog_update = db_paslog_csc.query.filter_by(pas_id=aipid).first()
            paslog_update.mp_paslog = "\"PAS arkistointi: AIP-ID= " + aipid + " " + " Timestamp= " +timestamp + "\""
            db.session.commit()
        except Exception as e:
            return f'Error writing PASLOG data to database: {str(e)}', 500
    return render_template('paslog_put_mark.html', response_status=response_status, obj_id=obj_id, aipid=aipid, timestamp=timestamp)

@paslog_bp.route("/make_empty_db")
@login_required
def make_empty_db():
    try:
        # Create a session context and use it to delete rows
        #with app.app_context():
        db.session.query(db_paslog_mp).delete()
        db.session.query(db_paslog_csc).delete()
        db.session.commit()
        return 'Table truncated successfully', 200
    except Exception as e:
        return f'Error truncating table: {str(e)}', 500
    #return render_template('paslog_db_trunc.html', environment=mp_paslog_mod.MP_ENV)