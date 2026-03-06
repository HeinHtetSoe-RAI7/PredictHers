from flask import Flask, render_template, request
from calculator import calculate_period
from tracker import calculate_tracker

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/calculator", methods=["GET", "POST"])
def calculator():
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
            # Handle the error and display a message to the user
            return render_template(
                "calculator.html", error="Invalid input. Please enter valid numbers."
            )

    return render_template("calculator.html")


@app.route("/tracker", methods=["GET", "POST"])
def tracker():
    if request.method == "POST":
        # To check which form was submitted
        source = request.form.get("source")

        if source == "tracker-yes":
            # --- Form: "Yes, I have an existing profile" ---
            username = request.form.get("username")
            last_period_str = request.form.get("lastPeriodDate")
            cycle_length = int(request.form.get("cycleLength"))
            period_length = int(request.form.get("periodLength"))

            # ... perform calculations and return template ...
            return f"Processed YES for {username}"

        elif source == "tracker-no":
            # --- Form: "No, enter my cycle history" ---
            try:
                # The required visible fields
                month1_str = request.form.get("month1")
                month2_str = request.form.get("month2")
                month3_str = request.form.get("month3")
                period_length = int(request.form.get("periodLength"))

                # The optional fields (Age and BMI)
                age = int(request.form.get("age"))
                bmi = float(request.form.get("bmi"))

                results = calculate_tracker(
                    [month1_str, month2_str, month3_str], period_length
                )
                return render_template("result.html", **results)

            except (ValueError, TypeError):
                return render_template(
                    "tracker.html",
                    error="Invalid input. Please enter valid dates and numbers.",
                )

    return render_template("tracker.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
