import sys

import requests
from flask import Flask, render_template, redirect, make_response, jsonify, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort
from requests import get

from data import db_session, jobs_api, users_api
from data.add_job import AddJobForm
from data.payment_form import AddDepartForm
from data.login_form import LoginForm
from data.users import User
from data.jobs import Jobs, Category
from data.payments import Payments
from data.register import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api_key = "40d1649f-0493-4b70-98ba-98533de7710b"
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/users_show/<int:user_id>')
def show_city(user_id):
    user = get(f'http://localhost:5000/api/users/{user_id}').json()
    response = requests.get(
        f"http://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={user['users']['city_from']}&format=json")

    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = ','.join(toponym["Point"]["pos"].split())
        # print(toponym_coodrinates)
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={toponym_coodrinates}&spn=0.03,0.03&l=sat"
        city_map = requests.get(map_request)
        # print(city_map)
        map_file = "static/img/map.png"
        with open(map_file, "wb") as file:
            file.write(city_map.content)
            user['users']['city'] = "../static/img/map.png"
    else:
        print("Ошибка выполнения запроса:")
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    return render_template('show_city.html', user=user, title='Hometown')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


db_session.global_init("db/our_wallet.sqlite")


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Wrong login or password", form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route("/")
@app.route("/index")
def index():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    users = session.query(User).all()
    #надо достать категорию
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("index.html", jobs=jobs, names=names, title='Мой кошлек')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register', form=form,
                                   message="Passwords don't match")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register', form=form,
                                   message="This user already exists")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            position=form.position.data,
            email=form.email.data,
            speciality=form.speciality.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/addjob', methods=['GET', 'POST'])
def addjob():
    add_form = AddJobForm()
    if add_form.validate_on_submit():
        session = db_session.create_session()
        jobs = Jobs(
            job=add_form.job.data,
            whose_salary=add_form.whose_salary.data,
            work_size=add_form.work_size.data,
            #collaborators=add_form.collaborators.data,
            #is_finished=add_form.is_finished.data
        )
        session.add(jobs)
        session.commit()
        return redirect('/')
    return render_template('addjob.html', title='Adding a job', form=add_form)


@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def job_edit(id):
    form = AddJobForm()
    if request.method == "GET":
        session = db_session.create_session()
        jobs = session.query(Jobs).filter(Jobs.id == id,
                                          (Jobs.whose_salary == current_user.id) | (current_user.id == 1)).first()
        if jobs:
            form.job.data = jobs.job
            form.whose_salary.data = jobs.whose_salary
            form.work_size.data = jobs.work_size
            # form.category.data = jobs.category
            # form.is_finished.data = jobs.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        jobs = session.query(Jobs).filter(Jobs.id == id,
                                          (Jobs.whose_salary == current_user.id) | (current_user.id == 1)).first()
        if jobs:
            jobs.job = form.job.data
            jobs.whose_salary = form.whose_salary.data
            jobs.work_size = form.work_size.data
            # jobs.category = form.category.data
            # jobs.is_finished = form.is_finished.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('addjob.html', title='Редактирование записи дохода', form=form)


@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def job_delete(id):
    session = db_session.create_session()
    jobs = session.query(Jobs).filter(Jobs.id == id,
                                      (Jobs.whose_salary == current_user.id) | (current_user.id == 1)).first()

    if jobs:
        session.delete(jobs)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/add_pay', methods=['GET', 'POST'])
def add_pay():
    add_form = AddDepartForm()
    if add_form.validate_on_submit():
        session = db_session.create_session()
        pay = Payments(
            title=add_form.title.data,
            who_paid=add_form.who_paid.data,
            pay_size=add_form.pay_size.data,
            category=add_form.category.data
        )
        session.add(pay)
        session.commit()
        return redirect('/')
    return render_template('add_pay.html', title='Adding a Payment', form=add_form)


@app.route("/payments")
def pay():
    session = db_session.create_session()
    payments = session.query(Payments).all()
    users = session.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("payments.html", payments=payments, names=names, title='List of Payments')


@app.route('/payments/<int:id>', methods=['GET', 'POST'])
@login_required
def pay_edit(id):
    form = AddDepartForm()
    if request.method == "GET":
        session = db_session.create_session()
        pay = session.query(Payments).filter(Payments.id == id,
                                                  (Payments.chief == current_user.id) | (
                                                          current_user.id == 1)).first()

        if pay:
            form.title.data = pay.title
            form.who_paid.data = pay.who_paid
            form.pay_size.data = pay.pay_size
            form.category.data = pay.category
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        pay = session.query(Payments).filter(Payments.id == id,
                                                  (Payments.chief == current_user.id) | (
                                                          current_user.id == 1)).first()
        if pay:

            pay.title = form.title.data
            pay.who_paid = form.who_paid.data
            pay.pay_size = form.pay_size.data
            pay.category = form.category.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_pay.html', title='Payments Edit', form=form)


@app.route('/payment_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def payments_delete(id):
    session = db_session.create_session()
    pay = session.query(Payments).filter(Payments.id == id,
                                              (Payments.chief == current_user.id) | (
                                                      current_user.id == 1)).first()
    if pay:
        session.delete(pay)
        session.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init("db/our_wallet.sqlite")
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(users_api.blueprint)

    app.run()


if __name__ == '__main__':
    main()
