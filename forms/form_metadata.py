from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,DateTimeField
from wtforms.validators import DataRequired,Email,EqualTo,Length


class SearchMuseumPlus(FlaskForm):
    objectid = StringField('objectid', validators = [Length(min=0, max=100)])
    inventorynumber = StringField('inventorynumber', validators= [Length(min=0, max=100)])
    title = StringField('title', validators = [Length(min=0, max=100)])
    submit = SubmitField('Search')

class Settings(FlaskForm):
    premis_video_normalization_date = DateTimeField('Your premis_video_normalization_date', format='%Y-%m-%dT%H:%M')    
    premis_video_normalization_agent = StringField('premis_video_normalization_agent', validators= [Length(min=0, max=200)])
    mets_createdate = StringField('mets_createdate', validators= [Length(min=0, max=200)])
    submit = SubmitField('Save')

class LidoSave(FlaskForm):
    classification1 = StringField('Classification \"Aineistotyyppi\"', default="Taideteos", validators=[DataRequired()])
    classification2 = StringField('Classification \"Pääluokka\"', validators=[DataRequired()])
    classification3 = StringField('Classification \"Erikoisluokka\"')
    mp_inv = StringField('Inventory number', validators=[DataRequired()])
    mp_id = StringField('Object ID', validators=[DataRequired()])
    mp_name = StringField('Title', validators=[DataRequired()])
    mp_actor = StringField('Creator', validators=[DataRequired()])
    mp_creation = StringField('Creation time', validators=[DataRequired()])
    mp_created = StringField('Record creation time')
    mp_repository = StringField('Current repository', validators=[DataRequired()])
    mp_owner = StringField('Current owner', validators=[DataRequired()])
    submit = SubmitField('Generate Lido-XML')

