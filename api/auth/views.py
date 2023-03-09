from flask_restx import Namespace, Resource


auth_namespace=Namespace('auth', description= "This is a namespace for authentication")

@auth_namespace.route('/signup')
class SignUp(Resource):


    def post(self):
        """
        Register a new student account
        Request methods: POST
        """
        pass

@auth_namespace.route('/login')
class Login(Resource):


    def post(self):
        """
        Generate JWT Token
        Request methods: POST
        """
        pass

