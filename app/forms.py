from re import fullmatch
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from app import app


class AddWeightForm(FlaskForm):
    sunday = StringField("Sunday")
    monday = StringField("Monday")
    tuesday = StringField("Tuesday")
    wednesday = StringField("Wednesday")
    thursday = StringField("Thursday")
    friday = StringField("Friday")
    saturday = StringField("Saturday")
    form_wide_error = HiddenField()

    submit = SubmitField("Save Daily Pounds")

    def validate(self):
        days_list = [self.sunday,
                     self.monday,
                     self.tuesday,
                     self.wednesday,
                     self.thursday,
                     self.friday,
                     self.saturday]

        days_with_data = [day for day in days_list if day.data]
        app.logger.info(self.thursday.data)
        if not days_with_data:
            app.logger.info(self.errors.items())
            self.form_wide_error.errors = ["At minimum, one day must have a weight to submit."]
            return False
        else:
            non_numeric_days = [non_numeric.label.text for non_numeric in days_with_data
                                if not (non_numeric.data.isnumeric()
                                        or fullmatch("[0-9]+(.[0-9]*)?", non_numeric.data)
                                        )]
            if non_numeric_days:
                self.form_wide_error.errors = [
                    'The following days are not valid numbers: {}'.format(', '.join(non_numeric_days))]
                return False

        return True