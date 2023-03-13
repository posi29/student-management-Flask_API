from flask_restx import Namespace, Resource, fields
from flask import request
import datetime
from ..models.students import Student
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.users import User
from ..utils import db, random_char
from functools import wraps
from flask import jsonify
from ..models.teacher import Teacher
from http import HTTPStatus
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, jwt_required, get_jwt_identity, unset_jwt_cookies,verify_jwt_in_request





auth_namespace=Namespace('auth', description= "This is a namespace for authentication")

def get_user_type(pk:int):
    """ Get the type a user belong 
    param:
        pk : user id
    """
    user = User.query.filter_by(id=pk).first()
    if user:
        return user.user_type
    return None


def admin_required():
    """
    A decorator to protect an endpoint with JSON Web Tokens.
    Any route decorated with this will require a user type of admin  to be present in the
    request before the endpoint can be called.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args,**kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            print(claims)
            if get_user_type(claims['sub']) == 'admin':
                return fn(*args,**kwargs)
            return jsonify({'msg':"Admin only!"}) , HTTPStatus.UNAUTHORIZED
        return decorator
    return wrapper

def staff_required():
    """
    A decorator to protect an endpoint with JSON Web Tokens.
    Any route decorated with this will require a user type of admin or teacher  to be present in the
    request before the endpoint can be called.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args,**kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if get_user_type(claims['sub']) == 'admin' or get_user_type(claims['sub']) == 'teacher':
                return fn(*args,**kwargs)
            return jsonify({'msg': "Staff Only!" }) , HTTPStatus.UNAUTHORIZED
        return decorator
    return wrapper



def teacher_required():
    """
    A decorator to protect an endpoint with JSON Web Tokens.
    Any route decorated with this will require a user type of teacher to be present in the
    request before the endpoint can be called.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args,**kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if get_user_type(claims['sub']) == 'teacher' :
                return fn(*args,**kwargs)
            return jsonify({'msg': "Student Only!" }) , HTTPStatus.UNAUTHORIZED
        return decorator
    return wrapper


def student_required():
    """
    A decorator to protect an endpoint with JSON Web Tokens.
    Any route decorated with this will require a user type of student  to be present in the
    request before the endpoint can be called.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args,**kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if get_user_type(claims['sub']) == 'student' :
                return fn(*args,**kwargs)
            return jsonify({'msg': "Student Only!" }) , HTTPStatus.UNAUTHORIZED
        return decorator
    return wrapper    


signup_schema = auth_namespace.model(
    'Signup', {
    'email': fields.String(required=True, description='User email address'),
    'first_name': fields.String(required=True, description="First name"),
    'last_name': fields.String(required=True, description="Lat name"),
    'password': fields.String(required=True, description="A password"),
}
)

login_schema = auth_namespace.model(
    'Login', {
    'email': fields.String(required=True, description='User email address'),
    'password': fields.String(required=True, description='User password')
}
)

Admin_model = auth_namespace.model(
    'User', {
        'id': fields.Integer(),
        'username': fields.String(required=True, description="A username"),
        'email': fields.String(required=True, description="An email"),
        'password_hash': fields.String(required=True, description="A password"),
        'is_active': fields.Boolean(description="This shows if a User is active or not"),
        'is_admin': fields.Boolean(description="Is the user an admin?")
    }
)

# Route for registering a user 
@auth_namespace.route('/signup')
class StudentRegistrationView(Resource):

    @auth_namespace.expect(signup_schema)
    @auth_namespace.doc(
        description="""
            This endpoint is accessible only to all user. 
            It allows the  creation of account as a student
            """
    )
    def post(self):
        """ Create a new student account """
        data = request.get_json()
        # Check if user already exists
        user = User.query.filter_by(email=data.get('email', None)).first()
        if user:
            return {'message': 'User already exists'} , HTTPStatus.CONFLICT
        # Create new user
        identifier=random_char(10)  
        current_year =  str(datetime.datetime.now().year)
        admission= 'STD@' + random_char(6) + current_year
        new_user =  Student(
            email=data.get('email'), 
            identifier=identifier,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            user_type = 'student',
            password_hash = generate_password_hash(data.get('password')),
            admission_no=admission
            )
        # match data.get('user_type'):
        #     case 'admin':
        #         designation= 'Principal'
        #         new_user = Admin(
        #             email=data.get('email'), 
        #             identifier=identifier,
        #             first_name=data.get('first_name'),
        #             last_name=data.get('last_name'),
        #             user_type = 'admin',
        #             password_hash = generate_password_hash(data.get('password')),
        #             designation=designation
        #             )
        #     case _ :
        #         response = {'message': 'Invalid user type'}
        #         return response , HTTPStatus.BAD_REQUEST
        try:
            new_user.save()
        except:
            db.session.rollback()
            return {'message': 'An error occurred while saving user'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'User registered successfully as a {}'.format(new_user.user_type)}, HTTPStatus.CREATED




@auth_namespace.route('/register/teacher')
class TeacherCreationView(Resource):
    @auth_namespace.expect(signup_schema)
    @auth_namespace.doc(
        description="""
            This endpoint is accessible only to an admin. 
            It allows admin create a teacher
            """
    )
    #@admin_required()
    def post(self):
        """ Create a new teacher account """
        data = request.get_json()
        # Check if user already exists
        user = User.query.filter_by(email=data.get('email', None)).first()
        if user:
            return {'message': 'Email already exists'} , HTTPStatus.CONFLICT
        # Create new user
        identifier=random_char(10)  
        current_year =  str(datetime.datetime.now().year)
        employee= 'TCH@' + random_char(6) + current_year
        new_user = Teacher(
            email=data.get('email'), identifier=identifier,
            first_name=data.get('first_name'), last_name=data.get('last_name'),
            user_type = 'teacher', password_hash = generate_password_hash(data.get('password')),
            employee_no=employee
            )
        try:
            new_user.save()
        except:
            db.session.rollback()
            return {'message': 'An error occurred while saving user'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'User registered successfully as a {}'.format(new_user.user_type)}, HTTPStatus.CREATED



@auth_namespace.route('/register/teacher')
class TeacherCreationView(Resource):
    @auth_namespace.expect(signup_schema)
    @auth_namespace.doc(
        description="""
            This endpoint is accessible only to an admin. 
            It allows admin create a teacher
            """
    )
    @admin_required()
    def post(self):
        """ Create a new teacher account """
        data = request.get_json()
        # Check if user already exists
        user = User.query.filter_by(email=data.get('email', None)).first()
        if user:
            return {'message': 'Email already exists'} , HTTPStatus.CONFLICT
        # Create new user
        identifier=random_char(10)  
        current_year =  str(datetime.datetime.now().year)
        employee= 'TCH@' + random_char(6) + current_year
        new_user = Teacher(
            email=data.get('email'), identifier=identifier,
            first_name=data.get('first_name'), last_name=data.get('last_name'),
            user_type = 'teacher', password_hash = generate_password_hash(data.get('password')),
            employee_no=employee
            )
        try:
            new_user.save()
        except:
            db.session.rollback()
            return {'message': 'An error occurred while saving user'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'User registered successfully as a {}'.format(new_user.user_type)}, HTTPStatus.CREATED




# Route for Token refresh 
@auth_namespace.route('/token/refresh')
class Refresh(Resource):
    @auth_namespace.doc(
        description="""
            This endpoint is accessible only to all user. 
            It allows user refresh their tokens
            """
    )
    @jwt_required(refresh=True)
    def post(self):
        """
            Generate new tokens
        """
        username = get_jwt_identity()

        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,

            }, HTTPStatus.OK


# Route for login user in( Authentication )
@auth_namespace.route('/token')
class UserLoginView(Resource):
    @auth_namespace.expect(login_schema)
    @auth_namespace.doc(
        description="""
            This endpoint is accessible only to all user. 
            It allows user authentication
            """
    )
    def post(self):
        """ Authenticate a user"""
        populate_db()
        email = request.json.get('email')
        password = request.json.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            response = {'message': 'Invalid username or password'}
            return response, HTTPStatus.UNAUTHORIZED
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        response = {
            'access_token': access_token,
            'refresh_token': refresh_token, 
            }
        return response, HTTPStatus.OK


@auth_namespace.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """
            Generate Refresh Token
        """
        username = get_jwt_identity()

        access_token = create_access_token(identity=username)

        return {'access_token': access_token}, HTTPStatus.OK


@auth_namespace.route('/logout')
class Logout(Resource):
    @jwt_required()
    def post(self):
        """
            Log the User Out
        """
        unset_jwt_cookies
        db.session.commit()
        return {"message": "Successfully Logged Out"}, HTTPStatus.OK