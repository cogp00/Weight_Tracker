from app import app, db
from app.forms import AddWeightForm
from flask import render_template, request
from datetime import date
from datetime import timedelta

@app.route("/", methods=["GET", "POST"])
def index():
    start_date = date.today() - timedelta(days=date.isoweekday(date.today()))
    select = "SELECT days, testweight.weight FROM public.testweight RIGHT JOIN generate_series(%(start)s, %(start)s + "\
             "interval '6 day', interval '1 day') days ON days = testweight.measurement_date ORDER BY days asc"

    form = AddWeightForm()
    form.start_date.data = start_date.strftime('%m-%d-%Y')
    current_week_values = db.engine.execute(select,
                                 {'start': start_date}
                                 ).fetchall()

    if request.method == 'GET':
        for vdate, vweight in current_week_values:
            form.days_list.append_entry(vweight)

    for nth, day_field in enumerate(form.days_list):
        day_field.label = current_week_values[nth][0].strftime("%m-%d")

    if form.validate_on_submit():
        insert_list = []
        update_list = []
        delete_list = []

        sql_insert = 'INSERT INTO public.testweight(measurement_date, weight) VALUES(%(vdate)s, %(vweight)s)'
        sql_update = 'UPDATE public.testweight SET weight = %(vweight)s WHERE measurement_date = %(vdate)s'
        sql_delete = 'DELETE FROM public.testweight WHERE measurement_date = %(vdate)s'

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
