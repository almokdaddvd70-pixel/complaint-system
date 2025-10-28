from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complaints.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def home():
    return redirect(url_for('admin_panel'))

@app.route('/admin')
def admin_panel():
    complaints = Complaint.query.order_by(Complaint.date_created.desc()).all()

    now = datetime.utcnow()
    first_day = datetime(now.year, now.month, 1)
    if now.month == 12:
        next_month = datetime(now.year + 1, 1, 1)
    else:
        next_month = datetime(now.year, now.month + 1, 1)

    current_total = Complaint.query.filter(
        Complaint.date_created >= first_day,
        Complaint.date_created < next_month
    ).count()

    done_count = Complaint.query.filter(
        Complaint.status == 'Done',
        Complaint.date_created >= first_day,
        Complaint.date_created < next_month
    ).count()

    pending_count = Complaint.query.filter(
        Complaint.status == 'Pending',
        Complaint.date_created >= first_day,
        Complaint.date_created < next_month
    ).count()

    return render_template(
        'admin.html',
        complaints=complaints,
        total=current_total,
        done=done_count,
        pending=pending_count,
        current_month=now.month,
        current_year=now.year
    )

@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    complaint = Complaint.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ('Pending', 'Done'):
        complaint.status = new_status
        db.session.commit()
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(host='127.0.0.2', port=5000, debug=True)
