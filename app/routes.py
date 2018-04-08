from app import app, db
from app.models import Weight
from app.forms import AddWeightForm, ViewWeightForm
from flask import render_template, request
from datetime import date
from datetime import timedelta
from datetime import datetime
import calendar


@app.route("/", methods=["GET", "POST"])
def view_weight():
    form = ViewWeightForm()
    if request.method == 'GET':
        base_date = date.today()
    else:
        base_date = date.fromtimestamp(float(form.start_date.data))
        year = base_date.year
        if base_date.month == 1 and form.previous.data:
            month = 12
            year = year - 1
        elif base_date.month == 12 and form.next.data:
            month = 1
            year = year + 1
        elif form.previous.data:
            month = base_date.month - 1
        elif form.next.data:
            month = base_date.month + 1

        base_date = date(year=year, month=month, day=base_date.day)

    form.start_date.data = datetime(year=base_date.year, month=base_date.month, day=base_date.day).timestamp()
    month = [week for week in
             calendar.Calendar(firstweekday=calendar.SUNDAY).monthdatescalendar(base_date.year, base_date.month)]

    month_values = {w.measurement_date.isoformat(): w.weight for w in
                    Weight.query.filter(Weight.measurement_date.between(month[0][0], month[-1][-1])).all()}

    weight_month = []
    day_labels = []
    for num_week in range(len(month)):
        week = []
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
        week.append(weekly_average)
        week.append(weekly_max)
        week.append(weekly_min)
        weight_month.append(week)
    day_labels.append("Averages")
    day_labels.append("Max")
    day_labels.append("Min")
    return render_template("view_weight.html",
                           month_label=base_date.strftime('%B, %Y'),
                           days=day_labels,
                           month=weight_month,
                           form=form)


@app.route("/add_weight", methods=["GET", "POST"])
def update_weight():
    form = AddWeightForm()
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
        return "Data Loaded"
    return render_template("insert_weight.html", form=form, labels=day_labels, dates=date_labels)
