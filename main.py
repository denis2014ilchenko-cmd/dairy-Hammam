#Импорт
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'my_top_secret_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Таблица карточек
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Card {self.id}>'

# Таблица пользователей
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.id}>'

# Страница входа
@app.route('/', methods=['GET','POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']

        users_db = User.query.all()
        for user in users_db:
            if form_login == user.user_email and form_password == user.password:
                session['user_email'] = user.user_email
                return redirect('/index')

        error = 'Неправильно указан пользователь или пароль'
        return render_template('login.html', error=error)
    else:
        return render_template('login.html')

# Страница регистрации
@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User(user_email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect('/')
    else:
    
        return render_template('registration.html')

# Главная страница (список карточек)
@app.route('/index')
def index():
    if 'user_email' not in session:
        return redirect('/')

    email = session['user_email']
    cards = Card.query.filter_by(user_email=email).all()
    return render_template('index.html', cards=cards)

# Страница одной карточки
@app.route('/card/<int:id>')
def card(id):
    if 'user_email' not in session:
        return redirect('/')

    card = Card.query.get(id)
    if card and card.user_email == session['user_email']:
        return render_template('card.html', card=card)
    else:
        return redirect('/index')

# Страница создания новой карточки
@app.route('/create')
def create():
    if 'user_email' not in session:
        return redirect('/')
    return render_template('create_card.html')

# Обработка формы создания
@app.route('/form_create', methods=['GET','POST'])
def form_create():
    if 'user_email' not in session:
        return redirect('/')

    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        text = request.form['text']

        email = session['user_email']
        card = Card(title=title, subtitle=subtitle, text=text, user_email=email)

        db.session.add(card)
        db.session.commit()
        return redirect('/index')
    else:
        return render_template('create_card.html')

if __name__ == "__main__":
    app.run(debug=True)