from flask import Flask, render_template, request
from utilities.calculator import calculate_period
from utilities.tracker import predict_with_global_model, predict_with_personal_history
from utilities.helper import parse_int, parse_float

app = Flask(__name__)


@app.route("/")
def home():
    """Home page route."""
    return render_template("index.html")


@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    """Period Calculator route."""
    if request.method == "POST":
        try:
            # Get data from the 'name' attributes in the HTML
            last_period_str = request.form.get("lastPeriodDate")
            period_length = int(request.form.get("periodLength"))
            cycle_length = int(request.form.get("cycleLength"))

            # Perform calculations and get results as a dictionary for the template
            results = calculate_period(last_period_str, cycle_length, period_length)

            return render_template("result.html", **results)
        except (ValueError, TypeError) as e:
            # Handle the error and display an error message to the user
            return f"Error: {str(e)}"

    return render_template("calculator.html")


@app.route("/tracker", methods=["GET", "POST"])
def tracker():
    """Period Tracker route."""
    if request.method == "POST":
        source = request.form.get("source")

        try:
            if source == "tracker-yes":
                # Handle "Yes, I have an existing profile"
                username = parse_int(request.form.get("username"))
                last_period_str = request.form.get("lastPeriodDate")
                cycle_length = parse_int(request.form.get("cycleLength"))
                period_length = parse_int(request.form.get("periodLength"))

                results = predict_with_personal_history(
                    user_id=username,
                    manual_last_period_date=last_period_str,
                    manual_avg_period_length=period_length,
                    manual_all_time_avg_cycle=cycle_length,
                )
            elif source == "tracker-no":
                # Handle "No, enter my cycle history"
                month1_str = request.form.get("month1")
                month2_str = request.form.get("month2")
                month3_str = request.form.get("month3")
                period_length = parse_int(request.form.get("periodLength"))
                age = parse_int(request.form.get("age"))
                bmi = parse_float(request.form.get("bmi"))

                results = predict_with_global_model(
                    last_3_dates=[month1_str, month2_str, month3_str],
                    avg_length=period_length,
                    bmi=bmi,
                    age=age,
                )
            else:
                raise ValueError("Invalid source value.")

            return render_template("result.html", **results)

        except ValueError as e:
            return f"Error: {str(e)}"

    return render_template("tracker.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
