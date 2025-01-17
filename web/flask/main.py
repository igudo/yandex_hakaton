import os
import time
import hashlib
from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
import logging
import json
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, ValidationError, IntegerField
from wtforms.validators import DataRequired, EqualTo
from flask_ckeditor import CKEditor
from datetime import datetime, timedelta


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# Настройка приложения и подключение бд от фласка sqlite

app.config['SECRET_KEY'] = 'moy-MEGA-klyu4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Бут страп тоже от фласка. + обозначение регистрация объектов по классам ниже

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
ckeditor = CKEditor(app)


class LoginForm(FlaskForm):
    # Форма ввода. Лог + пароль. Проверка на правильность лог пароля от приложений фласка))))

    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    # Регистрация + валид от фласка. И подтверждение пароля.

    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField(
        'Пароль', 
        validators=[
            DataRequired(), 
            EqualTo('password2', message='Пароли не совпадают.')
        ]
    )
    password2 = PasswordField('Подтвердите пароль ещё раз', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    # Проверка валидности логика. валид = правильност
    def validate_login(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Такой пользователь уже существует.')


class PostForm(FlaskForm):
    # Посты + валидность от фласка.

    date_offset = StringField("Через сколько часов дедлайн? (необязательно)", validators=[])
    body = TextAreaField("Есть новая заметка?", validators=[DataRequired()])
    submit = SubmitField('Запостить')


class DelegatePostForm(FlaskForm):
    # Посты + валидность от фласка.

    exec_id = StringField("ID Исполнителя", validators=[DataRequired()])
    submit = SubmitField('Запостить')


class EditProfileForm(FlaskForm):
    about = TextAreaField('Обо мне')
    submit = SubmitField('Обновить')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        'Старый пароль', 
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Новый пароль', 
        validators=[
            DataRequired(), 
            EqualTo('password2', message='Пароли не совпадают.')
        ]
    )
    password2 = PasswordField(
        'Новый пароль ещё раз', 
        validators=[DataRequired()]
    )
    submit = SubmitField('Сменить')


class User(UserMixin, db.Model):
    # Подключение бд. типы данных для них и колонка users для всех юзеров.

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about = db.Column(db.Text)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    # тест от ошибок, чтобы не крашило серв.
    @property
    def password(self):
        raise AttributeError('пароль прочесть нельзя.')
    
    @password.setter
    def password(self, password):
        # Собственно установка пароля.  При регистрации
        # Фласковый генератор хеша для пароля.
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        # Подтверждение проверки тот ли пароль когда авторизуешься
        return check_password_hash(self.password_hash, password)
    
    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        email = '{}@bookmarks.ru'.format(self.username.lower()).encode('utf-8')
        email_hash = hashlib.md5(email).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=email_hash, size=size, default=default, rating=rating)
    
    def robohash(self, size=200):
        # нужны картинки( робохеш крч ты каждому юзеру свою рандомную аву генеришь, у него там свои
        # методы. но она сохраняется навсегда тк есть индификатор постоянный для юзеров
        # . главное чтобы инет был - а то все падет!
        url = 'https://robohash.org/'
        return url + self.username + '?size={}x{}'.format(size, size)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    author_name = db.Column(db.Text)
    exec_name = db.Column(db.Text)
    date_offset = db.Column(db.Integer)
    # время UTC ну лондонское
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    date_end = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    exec_id = db.Column(db.Integer)
    status = db.Column(db.Integer)

    finish = db.Column(db.Integer)


@app.context_processor
def inject_app_name():
    return dict(app_name="Заметки")


@app.route('/old', methods=['GET', 'POST'])
def old():
    # Тема такая. У каждого обычного есть свои посты и главная. А у админа только свои посты
    # Он публикует и их все видят на главной. Первый человек сайта становится админом.
    admin_posts = Post.query.filter_by(author_id=1).order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=admin_posts)


@app.route('/add-task', methods=['GET', 'POST'])
@login_required
def posts():
    # Сразу проверка на авторизацию. Если авторизован - то показывает.
    # У каждого свой личный кабинет. Только он видит свою инфу.
    form = PostForm()
    
    if form.validate_on_submit():
        post = Post(body=form.body.data, author_id=current_user.get_id(), exec_id=current_user.get_id(), author_name=current_user.username, exec_name=current_user.username, status=0, finish=0, date_offset=form.date_offset.data)
        db.session.add(post)
        db.session.commit()
        if form.date_offset.data:
            h = form.date_offset.data
            post.date_end = post.timestamp + timedelta(hours=int(h))
            db.session.add(post)
            db.session.commit()
        return redirect(url_for('posts'))

    user_posts = Post.query.filter_by(author_id=current_user.get_id()).order_by(Post.timestamp.desc()).all()
    user_posts_exec = Post.query.filter_by(exec_id=current_user.get_id()).order_by(Post.timestamp.desc()).all()
    return render_template('posts.html', form=form, posts=user_posts, posts_exec=user_posts_exec)


@app.route('/pross', methods=['GET', 'POST'])
@login_required
def pross():
    # Сразу проверка на авторизацию. Если авторизован - то показывает.
    # У каждого свой личный кабинет. Только он видит свою инфу.
    form = PostForm()

    if form.validate_on_submit():
        post = Post(body=form.body.data, author_id=current_user.get_id(), exec_id=current_user.get_id(),
                    author_name=current_user.username, exec_name=current_user.username, status=0, finish=0,
                    date_offset=form.date_offset.data)
        db.session.add(post)
        db.session.commit()
        if form.date_offset.data:
            h = form.date_offset.data
            post.date_end = post.timestamp + timedelta(hours=int(h))
            db.session.add(post)
            db.session.commit()
        return redirect(url_for('pross'))

    user_posts = Post.query.filter_by(author_id=current_user.get_id()).order_by(Post.timestamp.desc()).all()
    user_posts_exec = Post.query.filter_by(exec_id=current_user.get_id()).order_by(Post.timestamp.desc()).all()
    return render_template('pross.html', form=form, posts=user_posts, posts_exec=user_posts_exec, date_now=datetime.utcnow())


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # Сразу проверка на авторизацию. Если авторизован - то показывает.
    # У каждого свой личный кабинет. Только он видит свою инфу.
    form = PostForm()

    if form.validate_on_submit():
        post = Post(body=form.body.data, author_id=current_user.get_id(), exec_id=current_user.get_id(), author_name=current_user.username, exec_name=current_user.username, data_end=10, status=0, finish=0, date_offset=form.date_offset.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))

    user_posts = Post.query.filter_by(author_id=current_user.get_id()).order_by(Post.timestamp.desc()).all()
    user_posts_exec = Post.query.filter_by(exec_id=current_user.get_id()).order_by(Post.timestamp.desc()).all()
    return render_template('index2.html', form=form, posts=user_posts, posts_exec=user_posts_exec)

@app.errorhandler(404)
def page_not_found(e):
    # Если нет страницы, дропает 404 ошибку.
    # Нужен аргумент, но я его не юзаю. А без него краши
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@app.errorhandler(500)
def internal_server_error(e):
    # Ошибка сервера - 500 ошибка.
    # Нужен аргумент, но я его не юзаю. А без него краши
    return render_template('500.html'), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Авторизация. Форма - класс, который выше.
    form = LoginForm()
    # Проверка на правильность ввода форм. тож халявная функция
    if form.validate_on_submit():
        user1 = User.query.filter_by(username=form.login.data).first()
        # если юзер реален ну не пуст и верификация пароля пройдена( хеш от этого пароля совпадает с
        # хешом в бд, который фласк генерит. То авторизируем
        if user1 is not None and user1.verify_password(form.password.data):
            login_user(user1, False)
            return redirect(url_for('index'))
        # ну если сюда доходит то ошибка
        flash('Неправильный логин или пароль.')
    # функция есть загенерили страницу и работает
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    # чтобы выйти нужна авторизация. фласк тупа все дает это на изи сделать. Выходим и все.
    logout_user()
    flash('Вы вышли.')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Форма регистрации - класс, который выше
    form = RegistrationForm()
    if form.validate_on_submit():
        # проверка фласком на правильность полей и указание если все ок то пароль логин создаем юзера
        user1 = User(username=form.login.data, password=form.password.data)
        # добавляем бд и коммитим, ну запоминаем типо сохранение.
        db.session.add(user1)
        db.session.commit()
        flash('Теперь вы можете войти.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/delete_post/<int:post_id>')
@login_required
def delete_post(post_id):
    # авторизация нужна. Человек видит только свои посты, поэтому удалить по ид может свои.
    # удаление ну  и бд сохранение
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('posts'))


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if int(current_user.get_id()) != int(post.author_id):
        abort(403)
        
    form = PostForm()
    
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('Запись успешно изменена.')
        return redirect(url_for('edit_post', post_id=post.id))
    
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@app.route('/delegate_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delegate_post(post_id):
    post = Post.query.get_or_404(post_id)

    if int(current_user.get_id()) != int(post.author_id):
        abort(403)

    form = DelegatePostForm()

    if form.validate_on_submit():
        post.exec_id = form.exec_id.data
        u = User.query.get_or_404(form.exec_id.data)
        post.exec_name = u.username
        db.session.add(post)
        db.session.commit()
        flash('Запись успешно изменена.')
        return redirect(url_for('posts'))

    form.exec_id.data = post.exec_id
    return render_template('delegate_post.html', form=form)


@app.route('/api/auth', methods=['POST'])
def auth():
    logging.info('Request: %r', request.json)
    try:
        user1 = User.query.filter_by(username=request["login"]).first()
        # если юзер реален ну не пуст и верификация пароля пройдена( хеш от этого пароля совпадает с
        # хешом в бд, который фласк генерит. То авторизируем
        if user1 is not None and user1.verify_password(request["password"]):
            response = {'token': user1.id, "login": request['login'], "password": request["password"]}
        else:
            response = {'success': 'NO'}

        logging.info('Response: %r', request.json)

        return json.dumps(response)
    except Exception:
        response = {'success': 'NO'}
        return json.dumps(response)


@app.route('/api/task/<token>', methods=['GET'])
def tasks(token):
    try:
        posts = []
        user_posts = Post.query.filter_by(author_id=int(token)).order_by(Post.timestamp.desc()).all()
        user_posts_exec = Post.query.filter_by(exec_id=int(token)).order_by(Post.timestamp.desc()).all()
        for post in user_posts:
            posts.append(post.body)
        for post in user_posts_exec:
            posts.append(post.body)
        seva = {}
        seva["posts"] = posts
        return str(seva)
    except Exception:
        response = {'success': 'NO'}
        return str(response)


@app.route('/change_status_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def change_status_post(post_id):
    post = Post.query.get_or_404(post_id)

    if int(current_user.get_id()) not in (int(post.author_id), int(post.exec_id)):
        abort(403)
    post.status += 1

    if post.status == 6:
        post.finish = 1

    db.session.add(post)
    db.session.commit()
    flash('Запись успешно изменена.')
    return redirect(url_for('posts'))


@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def user(user_id):
    user1 = User.query.filter_by(id=user_id).first_or_404()
    posts_count = Post.query.filter_by(author_id=user_id).count()
    form = EditProfileForm()
    if form.validate_on_submit():
        user1.about = form.about.data
        db.session.commit()
        flash('Ваш профиль обновлён!')
        return redirect(url_for('user', user_id=user_id))
    return render_template('user.html', user=user1, posts_count=posts_count, form=form)


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Ваш пароль изменён.')
            return redirect(url_for('user', user_id=current_user.get_id()))
        else:
            flash('Ошибка пароля.')
    return render_template("change_password.html", form=form)


@login_manager.user_loader
def load_user(user_id):
    # подгрузка юзера
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    # запрос не был применен так как ему не хватает данных для действия лишнего. щас ок с этим. только
    # если самому не пробовать
    return render_template('401.html'), 401


if __name__ == "__main__":
    app.run()
