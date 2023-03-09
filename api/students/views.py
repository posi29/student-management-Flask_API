from flask_restx import Namespace, Resource


student_namespace=Namespace('students', description= "This is a namespace for students")

@student_namespace.route('/students')
class StudentGetCreate(Resource):


    def get(self):

        """
        View all students
        Request methods: GET
        """
        pass


    def post(self):

        """
        Add a new student
        Request methods: POST
        """
        pass


@student_namespace.route('/students/<int:student_id>')
class GetUpdateDelete(Resource):


    def get(self, student_id):

        """
        Retrieve a student by its ID
        Request methods: GET
        """
        pass

    def put(self, student_id):

        """
        Update a student by its ID
        Request methods: PUT
        """
        pass

    def delete(self, student_id):

        """
        Delete a student by its ID
        Request methods: DELETE
        """
        pass

@student_namespace.route('/students/course/<int:course_id>/student/<int:student_id>')
class GetSpecificStudentCourse (Resource):
    def get(self, student_id, course_id):

        """
       Get a Student's Specific course
        """
        pass

@student_namespace.route('/students/course/<int:course_id>/student/<int:student_id>')
