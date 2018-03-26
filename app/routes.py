from app import app, db
from app.forms import AddWeightForm
from flask import render_template, request
from datetime import date
from datetime import timedelta
from datetime import datetime
import calendar

@app.route("/", methods=["GET"])
def view_weight():
    month = [week for week in calendar.Calendar(firstweekday=calendar.SUNDAY).monthdatescalendar(date.today().year, date.today().month)]
    app.logger.info(min([day for week in month for day in week]))
    app.logger.info(max([day for week in month for day in week]))
    week = [week for week in calendar.Calendar(firstweekday=calendar.SUNDAY).monthdatescalendar(date.today().year, date.today().month) if date.today() in week]
    app.logger.info(week)
    start_date = datetime(date.today().year, date.today().month, 1)
    select = "SELECT days, weight FROM public.weight RIGHT JOIN generate_series(%(start)s, %(start)s + "\
             "interval '6 day', interval '1 day') days ON days = weight.measurement_date ORDER BY days asc"
    return render_template("view_weight.html", curdate=datetime(date.today().year,date.today().month, 1))

@app.route("/add_weight", methods=["GET", "POST"])
def update_weight():
    week = [day for week in calendar.Calendar(firstweekday=calendar.SUNDAY).monthdatescalendar(date.today().year, date.today().month) if date.today() in week for day in week]
    select = "SELECT measurement_date, weight FROM public.weight WHERE weight.measurement_date between %(start)s AND %(end)s"

    form = AddWeightForm()
    form.start_date.data = min(week)
    current_week_values = db.engine.execute(select, {'start': min(week), 'end': max(week)}).fetchall()

    if request.method == 'GET':
        sub_iter
        for day in week:
            if current_week_values and current_week_values[-1][0] == day:
                form.days_list.append_entry(current_week_values[-1][1])
        for vdate, vweight in current_week_values:
            form.days_list.append_entry(vweight)

    for nth, day_field in enumerate(form.days_list):
        day_field.label = current_week_values[nth][0].strftime("%m-%d")

    if form.validate_on_submit():
        insert_list = []
        update_list = []
        delete_list = []

        sql_insert = 'INSERT INTO public.weight(measurement_date, weight) VALUES(%(vdate)s, %(vweight)s)'
        sql_update = 'UPDATE public.weight SET weight = %(vweight)s WHERE measurement_date = %(vdate)s'
        sql_delete = 'DELETE FROM public.weight WHERE measurement_date = %(vdate)s'

        def make_dict(a, b):
            return {'vdate': a, 'vweight': b}

        def run_list(cmd_cur, cmd_sql, cmd_list):
            if cmd_list:
                cmd_cur.executemany(cmd_sql, cmd_list)

        for nth, updated in enumerate(form.days_list):
            if current_week_values[nth][1] is None and updated.data != '':
                insert_list.append(make_dict(current_week_values[nth][0], float(updated.data)))
            elif updated.data == '':
                if current_week_values[nth][1] is not None:
                    delete_list.append(make_dict(current_week_values[nth][0], None))
            elif current_week_values[nth][1] != float(updated.data):
                update_list.append(make_dict(current_week_values[nth][0], float(updated.data)))

        if insert_list + update_list + delete_list:
            rawcon = db.engine.raw_connection()
            rawcur = rawcon.cursor()
            run_list(rawcur, sql_insert, insert_list)
            run_list(rawcur, sql_update, update_list)
            run_list(rawcur, sql_delete, delete_list)
            rawcon.commit()
            rawcon.close()

        return "Data Loaded"


    return render_template("insert_weight.html", form=form)
