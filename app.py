from flask import Flask, render_template, request
import json
import requests

app = Flask(__name__)


# Set up your Google Generative Language API key
api_key = 'AIzaSyDyDRVBYxLBY7WEq2H3Tt6s9AE0U7eCx6g'

def generate_workout_plan(workout_name, num_days, volume_per_week, workout_type, include_warmup, include_cooldown, workout_location, weak_body_parts, client_gender):
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + api_key

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Generate a workout plan strictly following the format based on the following parameters:\n"
                                f"Workout Name/Title: {workout_name}\n"
                                f"Number of Days: {num_days}\n"
                                f"Volume per Week: {volume_per_week}\n"
                                f"Type of Workout: {workout_type}\n"
                                f"Include Warm-Up: {include_warmup}\n"
                                f"Include Cool-Down: {include_cooldown}\n"
                                f"Workout Location: {workout_location}\n"
                                f"Weak Body Parts: {weak_body_parts}\n"
                                f"Client Gender: {client_gender}\n"
                                f"The format of plan SHOULD be like this:\n"
                                f"Workout Plan Title\n"
                                f"    - Day name (menu)\n"
                                f"        o warm up (section 1)\n"
                                f"             exercise\n"
                                f"        o workout (section 2)\n"
                                f"             exercise / sets / reps / rest period / notes\n"
                                f"             exercise / sets / reps / rest period / notes\n"
                                f"             etc\n"
                                f"        o cool down (section 3)\n"
                                f"             exercise\n"
                                f"Please follow the structue and parameter as provided!I dont want any mistake\n"
                    }
                ]
            }
        ]
    }

    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        generated_content = response.json()['candidates'][0]['content']['parts'][0]['text']
        return generated_content
    else:
        return f"Error: {response.status_code} - {response.text}"

def updated_workout_plan(initial_plan, changes):
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + api_key

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"I have made a workout plan and I want you to make only these changes: {changes}\n"
                                f"From the following workout plan:\n{initial_plan}\n"
                                f"Please print the whole initial plan with only the above mentioned changes. Don't make any further changes."
                    }
                ]
            }
        ]
    }

    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        generated_content = response.json()['candidates'][0]['content']['parts'][0]['text']
        return generated_content
    else:
        return f"Error: {response.status_code} - {response.text}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if request.method == 'POST':
        # Retrieve form data
        workout_name = request.form['workout_name']
        num_days = request.form['num_days']
        volume_per_week = request.form['volume_per_week']
        workout_type = request.form['workout_type']
        include_warmup = request.form['include_warmup']
        include_cooldown = request.form['include_cooldown']
        workout_location = request.form['workout_location']
        weak_body_parts = request.form['weak_body_parts']
        client_gender = request.form['client_gender']

        initial_plan = generate_workout_plan(workout_name, num_days, volume_per_week, workout_type, include_warmup, include_cooldown, workout_location, weak_body_parts, client_gender)
        if initial_plan:
            return render_template('confirm_plan.html', initial_plan_lines=initial_plan.split('\n'))


@app.route('/confirm', methods=['POST'])
def confirm():
    if request.method == 'POST':
        initial_plan = request.form['initial_plan']
        is_true = request.form['is_true'].lower()

        if is_true == "true":
            return render_template('generated_plan.html', generated_plan_lines=initial_plan.split('\n'))
        elif is_true == "false":
            return render_template('update_plan.html', initial_plan_lines=initial_plan.split('\n'))


@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        initial_plan = request.form['initial_plan']
        changes = request.form['changes']
        updated_plan = updated_workout_plan(initial_plan, changes)
        return render_template('confirm_plan.html', initial_plan_lines=updated_plan.split('\n'))
    else:
        return render_template('update_plan.html')


if __name__ == "__main__":
    app.run(debug=True)
