from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, Shell 
import json
import os.path

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
manager = Manager(app)

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command("shell", Shell(make_context=make_shell_context))

@app.route('/')
def index():
    result =  { 'success': True }
    code = 200

    user_results = list()
    users = User.query.all()
    for user in users:
        user_to_add = { 'id': user.id, 'username': user.username, 'role': user.role.name }
        user_results.append(user_to_add)
    result.update({ 'users': user_results })

    role_results = list()
    roles = Role.query.all()
    for role in roles:
        role_to_add = { 'id': role.id, 'name': role.name }
        role_results.append(role_to_add)
    result.update({ 'roles': role_results })

    return json.dumps(result), code

@app.route('/users', methods=['GET'])
def get_users():
    result = dict()
    code = None

    users = User.query.all()
    if len(users) > 0:
        user_results = list()
        for user in users:
            user_to_add = {'id': user.id, 'username': user.username, 'role': user.role.name }
            user_results.append(user_to_add)
        result.update({ 'users': user_results })
        result.update({ 'success': True })
        code = 200
    else:
        result.update({ 'success': False })
        result.update({ 'message': 'not found' })
        code = 404

    return json.dumps(result), code

@app.route('/users', methods=['POST'])
def add_user():
    result = dict()
    code = None

    username = request.form['username']
    role_id = request.form['role']
    user_exists = User.query.filter_by(username=request.form['username']).first()
    role = Role.query.filter_by(id=request.form['role']).first()

    if username is None:
        result.update({ 'success': False })
        result.update({ 'message': 'missing name' })
        code = 500
    elif user_exists is not None:
        result.update({ 'success': False })
        result.update({ 'message': 'already exits' })
        code = 500
    elif role_id is None:
        result.update({ 'success': False })
        result.update({ 'message': 'missing role' })
        code = 500
    elif role is None:
        result.update({ 'success': False })
        result.update({ 'message': 'role does not exist' })
        code = 500
    else:
        user = User(username=request.form['username'], role=role)
        db.session.add(user)
        result.update({ 'success': True })
        code = 200

    return json.dumps(result), code

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    result = dict()
    code = None

    user = User.query.filter_by(id=int(user_id)).first()
    if user is None:
        result.update({ 'success': False })
        result.update({ 'message': 'not found'})
        code = 404
    else:
        user_result = { 'user': { 'id': user.id, 'username': user.username, 'role': user.role.name }}
        result.update(user_result)
        result.update({ 'success': True })
        code = 200

    return json.dumps(result), code

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    result = dict()
    code = None

    user = User.query.filter_by(id=int(user_id)).first()
    if user is None:
        result.update({ 'success': False })
        result.update({ 'message': 'not found'})
        code = 404
    else:
        username = request.form['username']
        role_id = request.form['role_id']
        if role_id is not None:
            role = Role.query.filter_by(id=int(role_id)).first()
            if role is None:
                result.update({ 'success': False })
                result.update({ 'message': 'invalid role' })
                code = 500
            else:
                user.role = role
                db.session.add(user)
                result.update({ 'success': True })
                code = 200
        if username is not None:
            existing_user = User.query.filter_by(username=username).first()
            if (existing_user is not None) and (existing_user != user):
                result.update({ 'success': False })
                result.update({ 'message': 'username taken by another user' })
                code = 500
            else: 
                user.username = username
                db.session.add(user)
                if code is None:
                    result.update({ 'success': True })
                    code = 500

    return json.dumps(result), code

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    result = dict()
    code = None

    user = User.query.filter_by(id=int(user_id)).first()
    if user is None:
        result.update({ 'success': False })
        result.update({ 'message': 'not found'})
        code = 404
    else:
        db.session.delete(user)
        result.update({ 'success': True })
        code = 200

    return json.dumps(result), code

@app.route('/roles', methods=['GET'])
def get_roles():
    result = dict()
    code = None

    roles = Role.query.all()
    if len(roles) > 0:
        role_results = list()
        for role in roles:
            role_to_add = {'id': role.id, 'name': role.name }
            role_results.append(role_to_add)
        result.update({ 'roles': role_results })
        result.update({ 'success': True })
        code = 200
    else:
        result.update({ 'success': False })
        result.update({ 'message': 'not found' })
        code = 404

    return json.dumps(result), code

@app.route('/roles', methods=['POST'])
def add_roll():
    result = dict()
    code = None

    name = request.form['name']
    if name is None:
        result.update({ 'success': False })
        result.update({ 'message': 'missing name' })
        code = 500
    else:
        role = Role.query.filter_by(name=request.form['name']).first()
        if role is None:
            role = Role(name=request.form['name'])
            db.session.add(role)
            result.update({ 'success': True })
            code = 200
        else:
            result.update({ 'success': False })
            result.update({ 'message': 'already exits' })
            code = 500

    return json.dumps(result), code

@app.route('/roles/<role_id>', methods=['GET'])
def get_role(role_id):
    result = dict()
    code = None

    role = Role.query.filter_by(id=int(role_id)).first()
    if role is None:
        result.update({ 'success': False })
        result.update({ 'message': 'not found'})
        code = 404
    else:
        role_result = { 'role': { 'id': role.id, 'name': role.name }}
        result.update(role_result)
        result.update({ 'success': True })
        code = 200

    return json.dumps(result), code

@app.route('/roles/<role_id>', methods=['PUT'])
def update_role(role_id):
    result = dict()
    code = None

    role = Role.query.filter_by(id=int(role_id)).first()
    if role is None:
        result.update({ 'success': False })
        result.update({ 'message': 'not found'})
        code = 404
    else:
        name = request.form['name']
        if name is None:
            result.update({ 'success': False })
            result.update({ 'message': 'missing name'})
            code = 500
        else:
            role.name = name
            db.session.add(role)
            result.update({ 'success': True })
            code = 200

    return json.dumps(result), code

@app.route('/roles/<role_id>', methods=['DELETE'])
def delete_role(role_id):
    result = dict()
    code = None

    role = Role.query.filter_by(id=int(role_id)).first()
    if role is None:
        result.update({ 'success': False })
        result.update({ 'message': 'not found'})
        code = 404
    else:
        user = User.query.filter_by(role=role).first()
        if user is not None:
            result.update({ 'success': False })
            result.update({ 'message': 'users with role exist' })
            code = 500
        else:
            db.session.delete(role)
            result.update({ 'success': True })
            code = 200
    
    return json.dumps(result), code

if __name__ == '__main__':
    manager.run()
