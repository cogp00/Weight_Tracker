from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, StringField, FieldList

from datetime import datetime
from datetime import timedelta
import re

class ViewWeightForm(FlaskForm):
    start_date = HiddenField()
    previous = SubmitField("Previous")
    next = SubmitField("Next")


class AddWeightForm(FlaskForm):
    days_list = FieldList(StringField())
    form_wide_error = HiddenField()
    start_date = HiddenField()

    submit = SubmitField("Save Daily Pounds")

    def validate(self):
        days_with_bad_format = []
        start_date = datetime.fromtimestamp(self.start_date.data)

        for nth, day in enumerate(self.days_list):
            if day.data:
                if day.data.isnumeric() or re.fullmatch("[0-9]+(.[0-9]*)?", day.data):
                    pass
                else:
                    bad_date = start_date + timedelta(days=nth)
                    days_with_bad_format.append(bad_date.strftime('%m-%d-%Y'))

        if days_with_bad_format:
            self.form_wide_error.errors = ['The following days are not valid numbers: {}'.format(
                ', '.join(days_with_bad_format))]
            return False
        return True