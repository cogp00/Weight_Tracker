from app import app, db
from app.models import Weight
from app.forms import AddWeightForm, ViewWeightFormBase, ViewWeightFormDynamic
from flask import render_template, request, redirect, url_for
from datetime import date
from datetime import timedelta
from datetime import datetime
import calendar


@app.route("/", methods=["GET", "POST"])
@app.route("/<view_date>")
def view_weight():
    if request.method == 'GET':
        if request.args.get('view_date'):
            base_date = datetime.fromtimestamp(float(request.args.get('view_date')))
        else:
            base_date = date.today()
    else:
        base_date = date.fromtimestamp(float(request.form['start_date']))
        year = base_date.year
        selected_week = [rfk for rfk in list(request.form.keys()) if rfk.startswith('week_')]
        if base_date.month == 1 and request.form.get('previous'):
            month = 12
            year = year - 1
        elif base_date.month == 12 and request.form.get('next'):
            month = 1
            year = year + 1
        elif request.form.get('previous'):
            month = base_date.month - 1
        elif request.form.get('next'):
            month = base_date.month + 1
        elif selected_week:
            selected_date = [week for week_num, week in
                             enumerate(calendar.Calendar(firstweekday=calendar.SUNDAY).monthdatescalendar(
                                 base_date.year,base_date.month))
                             if week_num == int(selected_week[0].replace('week_', ''))][0]
            selected_date = [sd for sd in selected_date if sd.month == base_date.month][0]
            return redirect(url_for("update_weight", update_week=datetime(year=selected_date.year,
                                                                          month=selected_date.month,
                                                                          day=selected_date.day).timestamp()))

        base_date = date(year=year, month=month, day=base_date.day)

    month = [week for week in
             calendar.Calendar(firstweekday=calendar.SUNDAY).monthdatescalendar(base_date.year, base_date.month)]

    month_values = {w.measurement_date.isoformat(): w.weight for w in
                    Weight.query.filter(Weight.measurement_date.between(month[0][0], month[-1][-1])).all()}

    weight_month = []
    day_labels = []
    weight_month_summary = []
    for num_week in range(len(month)):
        week = []
        week_summary = []
        for num_day in range(7):
            if num_week == 0:
                day_labels.append(month[num_week][num_day].strftime('%A'))
            week.append((month[num_week][num_day],
                         month_values.get(month[num_week][num_day].isoformat(), '')))
        non_null_values = [value[1] for value in week if value[1] != '']
        if non_null_values:
            weekly_average = str(round(sum(non_null_values) / len(non_null_values),1))
            weekly_max = max(non_null_values)
            weekly_min = min(non_null_values)
        else:
            weekly_average = '-'
            weekly_max = '-'
            weekly_min = '-'
        week_summary.append(weekly_average)
        week_summary.append(weekly_max)
        week_summary.append(weekly_min)

        weight_month.append(week)
        weight_month_summary.append(week_summary)
    summary_labels = ["Averages", "Max", "Min"]

    form = ViewWeightFormDynamic(len(weight_month))
    form.start_date.data = datetime(year=base_date.year, month=base_date.month, day=base_date.day).timestamp()
    return render_template("view_weight.html",
                           month_label=base_date.strftime('%B %Y'),
                           days=day_labels,
                           summary_labels=summary_labels,
                           month=weight_month,
                           month_summary=weight_month_summary,
                           form=form)


@app.route("/add_weight/<update_week>")
@app.route("/add_weight", methods=["GET", "POST"])
def update_weight():
    form = AddWeightForm()
    if request.args.get('update_week'):
        base_date = datetime.fromtimestamp(float(request.args.get('update_week')))
        form.orgin_date.data = request.args.get('update_week')
    elif request.method == 'Post':
        base_date = datetime.fromtimestamp(form.start_date.data)
    else:
        base_date = datetime.today()
    py_week = [day for week in calendar.Calendar(firstweekday=calendar.SUNDAY)\
               .monthdatescalendar(base_date.year, base_date.month) if base_date.date() in week for day in week]
    form.start_date.data = datetime(year=py_week[0].year, month=py_week[0].month, day=py_week[0].day).timestamp()

    week_values = {w.measurement_date.isoformat(): w for w in
                   Weight.query.filter(Weight.measurement_date.between(py_week[0], py_week[-1])).all()}

    if request.method == 'GET':
        day_labels = []
        date_labels = []
        for day in py_week:
            if day.isoformat() in week_values:
                form.days_list.append_entry(week_values[day.isoformat()].weight)
            else:
                form.days_list.append_entry('')
            day_labels.append(day.strftime('%A'))
            date_labels.append(day.strftime('%m-%d'))

    if form.validate_on_submit():
        start_date = date.fromtimestamp(form.start_date.data)
        for nth, updated in enumerate(form.days_list):
            cur_date = (start_date + timedelta(days=nth)).isoformat()
            if week_values.get(cur_date, -1) == -1 and updated.data != '':
                db.session.add(Weight(measurement_date=py_week[nth], weight=float(updated.data)))
            elif week_values.get(cur_date, -1) != -1 and updated.data == '':
                db.session.delete(week_values[cur_date])
            elif week_values.get(cur_date, -1) != -1 and week_values[cur_date].weight != updated.data:
                week_values[cur_date].weight = float(updated.data)
        db.session.commit()
        return redirect(url_for('view_weight', view_date=form.orgin_date.data))
    return render_template("insert_weight.html", form=form, labels=day_labels, dates=date_labels)
