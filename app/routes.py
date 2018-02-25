from app import app, db
from app.forms import AddWeightForm
from flask import render_template
from datetime import date
from datetime import timedelta


@app.route("/", methods=["GET", "POST"])
def index():
    form = AddWeightForm()
    today = date.today()
    day_of_week = date.isoweekday(today)


    dates_of_week = [
                             (today - timedelta(days=day_of_week)) + timedelta(days=offset)
                     for offset in range(7)]


    if form.validate_on_submit():
        insert_string = """INSERT INTO weight(measurement_Date, weight) values( %s, %s )"""

        days = [dw_tuple for dw_tuple in zip(dates_of_week,
                                             [form.sunday.data, form.monday.data, form.tuesday.data,
                                              form.wednesday.data, form.thursday.data, form.friday.data,
                                              form.saturday.data]) if dw_tuple[1]]
        rawcon = db.engine.raw_connection()
        rawcur = rawcon.cursor()
        rawcur.executemany(insert_string, days)
        rawcon.commit()
        rawcon.close()
        return "Data Loaded"

    return render_template("insert_weight.html",
                           form=form,
                           today="cat",
                           dates=[day.strftime("%m-%d") for day in dates_of_week])