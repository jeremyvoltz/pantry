from flask import Flask, render_template, request, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext import wtf
from flask.ext.superadmin import Admin, model

# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

status_code = [(0, "buy"),
                (1, "full"),
                (2, "if on sale")
                ]


# Create models


# Create M2M table
location_table = db.Table('location_table',
                           db.Column('food_id', db.Integer, db.ForeignKey('food.id')),
                           db.Column('store_id', db.Integer, db.ForeignKey('store.id'))
                           )


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    essential = db.Column(db.Boolean)
    # status_id = db.Column(db.String(80), db.ForeignKey('status.id'))
    status = db.Column(db.Integer)
    locations = db.relationship('Store', secondary=location_table,
        backref=db.backref('foods', lazy='dynamic'))

    def __unicode__(self):
        return self.name


# class Status(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), unique=True)
#     foods = db.relationship('Food', backref='status', lazy='dynamic')

#     def __unicode__(self):
#         return self.name

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

    def __unicode__(self):
        return self.name


# Flask views

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/add', methods=['GET', 'POST'])
def add():
    food = Food.query.order_by(Food.name)
    if request.method == 'POST':
        for f in food:
            if request.form.get(f) == '1':
                food = Food.query.filter_by(name=key).first()
                food.status = 0
                db.session.commit()
        for i in range(5):
            name = request.form.get(str(i))
            if name:
                essential = bool(request.form.get("checkbox_" + str(i)))
                food = Food(name=name, essential=essential, status=0)
                db.session.add(food)
                db.session.commit()
        return redirect(url_for('index'))
    return render_template('food.html', food=food)


@app.route('/pantry', methods=['GET', 'POST'])
def pantry():
    food = Food.query.order_by(Food.name)
    if request.method == 'POST':
        for f in food:
            food = Food.query.filter_by(name=f.name).first()
            food.essential = False
            if request.form.get(f.name + "_essential") == '1':
                food.essential = True
            if request.form.get(f.name + "_status"):
                food.status = request.form.get(f.name + "_status")
            if request.form.get(f.name + "_delete"):
                db.session.delete(food)
            db.session.commit()
        for i in range(5):
            name = request.form.get(str(i))
            if name:
                essential = bool(request.form.get("checkbox_" + str(i)))
                status = bool(request.form.get("status_" + str(i)))
                food = Food(name=name, essential=essential, status=status)
                db.session.add(food)
                db.session.commit()
        return redirect(url_for('index'))
    locations = Store.query.order_by("name").all()
    return render_template('pantry.html', food=food, locations=locations)


@app.route('/stores', methods=['GET', 'POST'])
def stores():
    food = Food.query.order_by(Food.name)
    locations = Store.query.order_by("name").all()
    if request.method == 'POST':
        for f in food:
            food = Food.query.filter_by(name=f.name).first()
            for store in locations:
                if request.form.get(f.name + "_" + store.name) == '1':
                    food.locations.append(store)
                elif store in food.locations:
                    food.locations.remove(store)

                db.session.commit()
        
        return redirect(url_for('index'))
    locations = Store.query.order_by("name").all()
    return render_template('stores.html', food=food, locations=locations)


if __name__ == '__main__':
    # Create admin
    admin = Admin(app, 'Simple Models')

    # Add views
    admin.register(Food, session=db.session)
    # admin.register(Status, session=db.session)
    admin.register(Store, session=db.session)
    # admin.add_view(sqlamodel.ModelView(Post, session=db.session))

    # Create DB
    db.create_all()

    # Start app
    app.debug = True
    app.run('0.0.0.0', 8000)