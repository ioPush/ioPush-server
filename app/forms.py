#-*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from flask_security.forms import RegisterForm
from .models import User


class ExtendedRegisterForm(RegisterForm):
    """ Add nickname field to the register's class
    """
    nickname = StringField('Nickname', [DataRequired()])
    
    def validate(self):
        """ Add nicknae validation
        
            :return: True is the form is valid
        """
        # Use standart validator
        rv = Form.validate(self)
        if not rv:
            return False
         
        # Check if nickname already exists       
        user = User.query.filter_by(
            nickname=self.nickname.data).first()
        if user is not None:
            self.nickname.errors.append('Nickname already exists')
            return False
            
        return True