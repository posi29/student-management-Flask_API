from flask_restx import Namespace, Resource, fields
from ..utils import db
from flask import request
from ..models.students import Student
from ..models.studentcourse import StudentCourse
from ..models.courses import Course
from ..models.users import User
from ..models.grade import Score
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..auth.views import admin_required, staff_required, student_required, teacher_required
from http import HTTPStatus



def get_grade(score):
    """ Convert a score to corresponding grade """
    if score < 100 and score > 89:
        return 'A'
    elif score < 90 and score > 79:
        return 'B'
    elif score < 80 and score > 69:
        return 'C'
    elif score < 70 and score > 59:
        return 'D'
    elif score < 60 and score > 49:
        return 'E'
    elif score < 50 :
        return 'F'    
    else:
        return 'F'

def convert_grade_to_gpa(grade):
    """Convert a grade to the corresponding point value """
    if grade == 'A':
        return 4.0
    elif grade == 'B':
        return 3.3
    elif grade == 'C':
        return 2.3
    elif grade == 'D':
        return 1.3
    else:
        return 0.0

students_namespace = Namespace('students', description='Namespace for Student ')

students_fields_schema = {
    'id': fields.String(),
    'identifier': fields.String(required=False, description='User identifier'),
    'email': fields.String(required=True, description='User email address'),
    'first_name': fields.String(required=True, description="First name"),
    'last_name': fields.String(required=True, description="Lat name"),
    'admission_no': fields.String(required=True, description="First name"),
}



student_score_add_fields_schema = {
    'student_id': fields.Integer(required=False, description='ID of student'),
    'course_id': fields.Integer(required=True, description='ID of course'),
    'score': fields.Integer(required=True, description="Score value"),
}



course_fields_schema = {
    'course_id': fields.String(required=True),
}

course_retrieve_fields_schema =  {
    'id': fields.Integer(),
    'name': fields.String(required=True, description="A course name"),
    'course_code': fields.String(description="A course code"),
    'teacher_id': fields.Integer(), 
    'created_at': fields.DateTime( description="Course creation date"),
}



students_schema = students_namespace.model('Students list serializer', students_fields_schema)
courses_schema = students_namespace.model('Students courses list serializer', course_retrieve_fields_schema)
courses_add_schema = students_namespace.model('Courses add serializer', course_fields_schema)
student_score_add_schema = students_namespace.model('Courses add serializer', student_score_add_fields_schema)




# Route for login user in( Authentication )
@students_namespace.route('')
class StudentsListView(Resource):

    @students_namespace.marshal_with(students_schema)
    @students_namespace.doc(
        description="""
            This endpoint is accessible only to an admin user. 
            It allows the admin retrieve all student is the school
            """
    )
    @admin_required() 
    def get(self):
        """
        Retrieve all students in school
        """
        students = Student.query.all()
        return students , HTTPStatus.OK




@students_namespace.route('/<int:student_id>')
class StudentRetrieveDeleteUpdateView(Resource):

    @students_namespace.marshal_with(students_schema)
    @students_namespace.doc(
        description="""
            This endpoint is accessible only to an admin and teacher. 
            It allows the  retrieval of a student
            """
    )
    @staff_required()
    def get(self, student_id):
        """
        Retrieve a student 
        """
        student = Student.query.filter_by(id=student_id).first()
        if not student:
            return {'message':'Student does not exist'}, HTTPStatus.NOT_FOUND
        return student , HTTPStatus.OK
     


@students_namespace.route('/<int:student_id>/courses/grade')
class StudentCoursesGradeListView(Resource):

    @admin_required()
    def get(self, student_id):
        """
        Retrieve a student all courses grade
        """     
        courses = StudentCourse.get_student_courses(student_id)
        response = []
        
        for course in courses:
            grade_response = {}
            score_in_course = Score.query.filter_by(student_id=student_id , course_id=course.id).first()
            grade_response['name'] = course.name
            if score_in_course:
                grade_response['score'] = score_in_course.score
                grade_response['grade'] = score_in_course.grade
            else:
                grade_response['score'] = None
                grade_response['grade'] = None 
            response.append(grade_response)
        return response , HTTPStatus.OK
    

@students_namespace.route('/<int:student_id>/courses')
class StudentCoursesListView(Resource):

    @students_namespace.marshal_with(courses_schema)
    def get(self, student_id):
        """
        Retrieve a student courses
        """     
        courses = StudentCourse.get_student_courses(student_id)
        return courses , HTTPStatus.OK


@students_namespace.route('/courses/add_and_drop')
class StudentCourseRegisterView(Resource):

    @students_namespace.marshal_with(courses_schema)
    @students_namespace.expect(courses_add_schema)
    @students_namespace.doc(
        description="""
            This endpoint is accessible only to a student. 
            It allows a student register for a course
            """
    )
    @student_required()  
    def post(self):
        """ 
        Register for a course 
        """     
        authenticated_user_id = get_jwt_identity() 
        student = Student.query.filter_by(id=authenticated_user_id).first()   
        data = request.get_json()
        course = Course.query.filter_by(id=data.get('course_id')).first()  
        if course:
            #check if student has registered for the course before
            get_student_in_course = StudentCourse.query.filter_by(student_id=student.id, course_id=course.id).first()
            if get_student_in_course:
                return {
                    'message':'Course has already been registered'
                    } , HTTPStatus.OK
            # Register the student to the course
            add_student_to_course = StudentCourse(student_id=student.id, course_id=course.id)
            try:
                add_student_to_course.save()
                return {'message': 'Course registered successfully'} , HTTPStatus.CREATED
            except:
                db.session.rollback()
                return {'message': 'An error occurred while registering course'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'Course does not exist'} , HTTPStatus.NOT_FOUND


    @students_namespace.expect(courses_add_schema)
    @students_namespace.doc(
        description="""
            This endpoint is accessible only to a student. 
            It allows a student unregister for a course
            """
    )
    @student_required()
    def delete(self):
        """
        Unregister a  course
        """
        data = request.get_json()
        authenticated_user_id = get_jwt_identity()
        student = Student.query.filter_by(id=authenticated_user_id).first()   
        data = request.get_json()
        course = Course.query.filter_by(id=data.get('course_id')).first()  
        if course:
            #check if student has registered for the course before
            get_student_in_course = StudentCourse.query.filter_by(student_id=student.id, course_id=course.id).first()
            if get_student_in_course:
                try:
                    get_student_in_course.delete()
                    return {'message': 'Course delete successfully'} , HTTPStatus.NO_CONTENT
                except:
                    db.session.rollback()
                    return {'message': 'An error occurred while delete student course'}, HTTPStatus.INTERNAL_SERVER_ERROR
            return {
                    'message':'You have not register for this course'
                    } , HTTPStatus.BAD_REQUEST

        return {'message': 'Course does not exist'} , HTTPStatus.NOT_FOUND
    


@students_namespace.route('/course/add_score')
class StudentCourseScoreAddView(Resource):

    @students_namespace.expect(student_score_add_schema)
    @students_namespace.doc(
        description='''
            This endpoint is accessible only to a teacher. 
            It allow teacher add a student score in a course. 
            NOTE : The teacher must be the course teacher
            '''
    )
    @teacher_required()
    def put(self):
        """
        Add a student course score
        """     
        authenticated_user_id = get_jwt_identity()
        student_id = request.json['student_id']
        course_id = request.json['course_id']
        score_value = request.json['score']
        teacher = User.query.filter_by(id=authenticated_user_id).first()   
        # check if student and course exist
        student = Student.query.filter_by(id = student_id).first()
        course = Course.query.filter_by(id=course_id).first()
        if not student or not course:
            return {'message': 'Student or course not found'}, HTTPStatus.NOT_FOUND
        #  check if teacher is the course teacher
        if course.teacher_id != teacher.id :
            return {'message':'You cannot add score for this student in this course'}, HTTPStatus.UNAUTHORIZED
        # check if student is registered for the course
        student_in_course = StudentCourse.query.filter_by(course_id=course.id, student_id=student.id).first() 
        if student_in_course:
            # check if the student already have a score in the course
            score = Score.query.filter_by(student_id=student_id, course_id=course_id).first()
            grade = get_grade(score_value)
            if score:
                score.score = score_value
                score.grade = grade
            else:
                # create a new score object and save to database
                score = Score(student_id=student_id, course_id=course_id, score=score_value , grade=grade)
            try:
                score.save()
                return {'message': 'Score added successfully'}, HTTPStatus.CREATED
            except:
                db.session.rollback()
                return {'message': 'An error occurred while saving student course score'}, HTTPStatus.INTERNAL_SERVER_ERROR
        return {'message': 'The student is not registered for this course'}, HTTPStatus.BAD_REQUEST

     



@students_namespace.route('/<int:student_id>/gpa')
class StudentGPAView(Resource):

    def get(self, student_id):
        """
        Calculate a student gpa score
        """     
        student = Student.get_by_id(student_id)
        # get all the course the students offer
        courses = StudentCourse.get_student_courses(student.id)
        total_weighted_gpa = 0
        total_credit_hours = 0
        for course in courses:
            # check if student have a score for the course
            score_exist = Score.query.filter_by(student_id=student.id, course_id=course.id).first()
            if score_exist:
                grade = score_exist.grade
                # calculate the gpa for the course
                gpa = convert_grade_to_gpa(grade)
                weighted_gpa = gpa * course.credit_hours
                total_weighted_gpa += weighted_gpa
                total_credit_hours += course.credit_hours
        if total_credit_hours == 0:
            return {
                'message':'GPA calculation completed.',
                'gpa': total_credit_hours
            }, HTTPStatus.OK
        else:
            gpa =  total_weighted_gpa / total_credit_hours
            return {
                'message':'GPA calculation completed',
                'gpa': round(gpa , 2 ) 
            }, HTTPStatus.OK