from app import app, db
from app.forms import AddWeightForm
from flask import render_template, request
from datetime import date
from datetime import timedelta
from datetime import datetime
import calendar

@app.route("/", methods=["GET"])
def view_weight():
    month = [week for week in
             calendar.Calendar(firstweekday=calendar.SUNDAY).monthdatescalendar(date.today().year, date.today().month)]
    start_date = min([day for week in month for day in week])
    end_date = max([day for week in month for day in week])

    select = "SELECT measurement_date, weight FROM public.weight WHERE weight.measurement_date between %(start)s " \
             "AND %(end)s order by measurement_date asc"

    current_month_values = db.engine.execute(select, {'start': start_date, 'end': end_date}).fetchall()
    current_month_values = dict(zip([val[0] for val in current_month_values], [val[1] for val in current_month_values]))
    weight_month = []
    for week in month:
        for day in week:
            if day in current_month_values:
                weight_month.append((day, current_month_values[day]))
            else:
                weight_month.append((day, None))
    return render_template("view_weight.html", month=weight_month)

@app.route("/add_weight", methods=["GET", "POST"])
def update_weight():
    form = AddWeightForm()
    start_date = date.today()
    form.start_date.data = start_date.strftime('%m-%d-%Y')
    py_week = [day for week in calendar.Calendar(firstweekday=calendar.SUNDAY)\
               .monthdatescalendar(date.today().year, date.today().month) if start_date in week for day in week]
    select = "SELECT measurement_date, weight FROM public.weight WHERE weight.measurement_date between %(start)s " \
             "AND %(end)s order by measurement_date asc"

    current_week_values = db.engine.execute(select, {'start': py_week[0], 'end': py_week[-1]}).fetchall()
    current_week_values = dict(zip([day[0] for day in current_week_values],
                                   [weight[1] for weight in current_week_values]))
    if request.method == 'GET':
        for day in py_week:
            if day in current_week_values:
                form.days_list.append_entry(current_week_values[day])
            else:
                form.days_list.append_entry()

        for nth, day_field in enumerate(form.days_list):
            day_field.label = py_week[nth].strftime("%m-%d")

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
            if (not current_week_values and updated.data) or \
                    (py_week[nth] not in current_week_values and updated.data != ''):
                insert_list.append(make_dict(py_week[nth], float(updated.data)))
            elif py_week[nth] in current_week_values:
                if updated.data == '' and current_week_values[py_week[nth]] is not None:
                    delete_list.append(make_dict(py_week[nth], None))
                elif updated.data != current_week_values[py_week[nth]]:
                    update_list.append(make_dict(py_week[nth], float(updated.data)))

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
