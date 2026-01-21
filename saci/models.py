from django.db import models
from django.contrib.auth.models import User
from principal.models import SEX_CHOICES

# Create your models here.
class SaciUser(models.Model):
    id = models.AutoField('ID',primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    saci_birth_year = models.IntegerField('User birth year', null=True, blank=True)
    saci_school_year = models.CharField('User school year', max_length=32,null=True, blank=True)
    saci_sex = models.CharField(
        'Gênero',
        max_length=1,
        choices = SEX_CHOICES,
        null=True
    )
    registration_date = models.DateTimeField('Registration Date', null=True, blank=True)
    num_backups = models.IntegerField('Exercise', null=True, blank=True)
    block_email = models.BooleanField('Block Email', default=False)
    class Meta:
        db_table = 'saci_user'
        verbose_name = 'Saci user'
        verbose_name_plural = 'Saci users'

class SaciEvent(models.Model):
    def __str__(self):
        return self.id

    id = models.AutoField('ID',primary_key=True)
    the_type = models.IntegerField('Type',null=True, blank=True)
    the_time = models.DateTimeField('Time',auto_now_add=True,null=True, blank=True)
    user = models.ForeignKey(User,verbose_name="User",on_delete=models.SET_NULL,null=True, blank=True)
    course = models.CharField('Course', max_length=32,null=True, blank=True)
    class_name = models.CharField('Class', max_length=32,null=True, blank=True)
    class_index = models.IntegerField('Class index', null=True, blank=True)
    exercise = models.IntegerField('Exercise', null=True, blank=True)
    code = models.CharField('Code',max_length=32600, null=True, blank=True)
    total_tests = models.IntegerField('Total tests', null=True, blank=True)
    correct_tests = models.IntegerField('Correct tests', null=True, blank=True)
    class Meta:
        db_table = 'saci_event'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

class SaciBackup(models.Model):
    def __str__(self):
        return self.comment

    id = models.AutoField('ID',primary_key=True)
    the_time = models.DateTimeField('Time',auto_now_add=True,null=True, blank=True)
    exercise = models.IntegerField('Exercise', null=True, blank=True)
    class_name = models.CharField('Class',max_length=256, null=True, blank=True)
    comment = models.CharField('Comment',max_length=256, null=True, blank=True)
    data = models.CharField('Data',max_length=25600, null=True, blank=True)
    user = models.ForeignKey(User,verbose_name="User",on_delete=models.CASCADE)
    the_type = models.IntegerField('Type')
    course = models.CharField('Course',max_length=256, null=True, blank=True)
    class Meta:
        db_table = 'saci_backup'
        verbose_name = 'Backup'
        verbose_name_plural = 'Backups'

# class SaciClass(models.Model):
#     def __str__(self):
#         return self.name

#     id = models.AutoField('ID',primary_key=True)
#     course_id = models.IntegerField('Course')
#     num_exercises = models.IntegerField('Number of exercises')
#     is_public = models.BooleanField("Public")
#     name = models.CharField('Title',max_length=256, null=True, blank=True)
#     index = models.IntegerField('Index')
#     class Meta:
#         db_table = 'saci_class'
#         verbose_name = 'Class'
#         verbose_name_plural = 'Classes'

# class SaciCourse(models.Model):
#     def __str__(self):
#         return self.name_short

#     id = models.AutoField('ID',primary_key=True)
#     name_full = models.CharField('Name',max_length=256, null=True, blank=True)
#     name_short = models.CharField('Name abbrev.',max_length=7, null=True, blank=True)
#     #teacher_id = models.IntegerField('Instructor')
#     language = models.CharField('Programming Language',max_length=2, null=True, blank=True)
#     idiom = models.CharField('Idiom',max_length=2, null=True, blank=True)
#     class Meta:
#         db_table = 'saci_course'
#         verbose_name = 'Course'
#         verbose_name_plural = 'Courses'

# class SaciExercise(models.Model):
#     id = models.AutoField('ID',primary_key=True)
#     course = models.ForeignKey(SaciCourse,verbose_name="Course",on_delete=models.CASCADE)
#     the_class = models.ForeignKey(SaciClass,verbose_name="Class",on_delete=models.CASCADE)
#     exercise_total_test = models.IntegerField('Exercise', null=True, blank=True)
#     class Meta:
#         db_table = 'saci_exercise'
#         verbose_name = 'Exercise'
#         verbose_name_plural = 'Exercises'

# class SaciEvent(models.Model):
#     def __str__(self):
#         return self.id

#     id = models.AutoField('ID',primary_key=True)
#     the_type = models.CharField('Type', max_length=32,null=True, blank=True)
#     the_time = models.DateTimeField('Time',auto_now_add=True,null=True, blank=True)
#     user_id = models.ForeignKey(SaciUser,verbose_name="User",on_delete=models.CASCADE)
#     course = models.ForeignKey(SaciCourse,verbose_name="Course",on_delete=models.CASCADE)
#     the_class = models.ForeignKey(SaciClass,verbose_name="Class",on_delete=models.CASCADE)
#     exercise =  models.ForeignKey(SaciExercise,verbose_name="Exercise",on_delete=models.CASCADE)
#     code = models.CharField('Code',max_length=32600, null=True, blank=True)
#     total_tests = models.IntegerField('Total tests', null=True, blank=True)
#     correct_tests = models.IntegerField('Correct tests', null=True, blank=True)
#     class Meta:
#         db_table = 'saci_event'
#         verbose_name = 'Event'
#         verbose_name_plural = 'Events'

# class SaciExecute(models.Model):
#     id = models.AutoField('ID',primary_key=True)
#     user_id = models.ForeignKey(SaciUser,verbose_name="User",on_delete=models.CASCADE)
#     the_time = models.DateTimeField('Time',auto_now_add=True,null=True, blank=True)
#     course = models.ForeignKey(SaciCourse,verbose_name="Course",on_delete=models.CASCADE)
#     the_class = models.ForeignKey(SaciClass,verbose_name="Class",on_delete=models.CASCADE)
#     exercise =  models.ForeignKey(SaciExercise,verbose_name="Exercise",on_delete=models.CASCADE)
#     code = models.CharField('Code',max_length=32600, null=True, blank=True)
#     class Meta:
#         db_table = 'saci_execute'
#         verbose_name = 'Execute'
#         verbose_name_plural = 'Execute'

# class SaciHint(models.Model):
#     id = models.AutoField('ID',primary_key=True)
#     user_id = models.ForeignKey(SaciUser,verbose_name="User",on_delete=models.CASCADE)
#     the_time = models.DateTimeField('Time',auto_now_add=True,null=True, blank=True)
#     course = models.ForeignKey(SaciCourse,verbose_name="Course",on_delete=models.CASCADE)
#     the_class = models.ForeignKey(SaciClass,verbose_name="Class",on_delete=models.CASCADE)
#     exercise =  models.ForeignKey(SaciExercise,verbose_name="Exercise",on_delete=models.CASCADE)
#     code = models.CharField('Code',max_length=32600, null=True, blank=True)
#     class Meta:
#         db_table = 'saci_hint'
#         verbose_name = 'Hint'
#         verbose_name_plural = 'Hint'

# class SaciLoad(models.Model):
#     id = models.AutoField('ID',primary_key=True)
#     user_id = models.ForeignKey(SaciUser,verbose_name="User",on_delete=models.CASCADE)
#     the_time = models.DateTimeField('Time',auto_now_add=True,null=True, blank=True)
#     course = models.ForeignKey(SaciCourse,verbose_name="Course",on_delete=models.CASCADE)
#     the_class = models.ForeignKey(SaciClass,verbose_name="Class",on_delete=models.CASCADE)
#     class Meta:
#         db_table = 'saci_load'
#         verbose_name = 'Load'
#         verbose_name_plural = 'Loads'

# class SaciSubmit(models.Model):
#     id = models.AutoField('ID',primary_key=True)
#     user_id = models.ForeignKey(SaciUser,verbose_name="User",on_delete=models.CASCADE)
#     the_time = models.DateTimeField('Time',auto_now_add=True,null=True, blank=True)
#     course = models.ForeignKey(SaciCourse,verbose_name="Course",on_delete=models.CASCADE)
#     the_class = models.ForeignKey(SaciClass,verbose_name="Class",on_delete=models.CASCADE)
#     exercise =  models.ForeignKey(SaciExercise,verbose_name="Exercise",on_delete=models.CASCADE)
#     code = models.CharField('Code',max_length=32600, null=True, blank=True)
#     submit_answer = models.CharField('Code',max_length=32600, null=True, blank=True)
#     total_tests = models.IntegerField('Number of tests', null=True, blank=True)
#     correct_tests = models.IntegerField('Number of correct tests', null=True, blank=True)
#     class Meta:
#         db_table = 'saci_submit'
#         verbose_name = 'Hint'
#         verbose_name_plural = 'Hint'


'''
--
-- PostgreSQL database dump
--
CREATE TABLE public.backup (
    backup_id integer NOT NULL,
    backup_time double precision NOT NULL,
    backup_exercise_id integer,
    backup_class_name character varying(256),
    backup_comment character varying(256),
    backup_data text,
    backup_user_id integer,
    backup_type integer,
    backup_course_name character varying(256)
);


ALTER TABLE public.backup OWNER TO postgres;

--
-- Name: backup_backup_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.backup_backup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.backup_backup_id_seq OWNER TO postgres;

--
-- Name: backup_backup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.backup_backup_id_seq OWNED BY public.backup.backup_id;


--
-- Name: classes; Type: TABLE; Schema: public; Owner: obi; Tablespace: 
--

CREATE TABLE public.classes (
    class_id integer NOT NULL,
    class_course_id integer,
    class_num_exercises integer,
    class_is_public boolean,
    class_name character varying(256),
    class_index integer
);


ALTER TABLE public.classes OWNER TO obi;

--
-- Name: classes_class_id_seq; Type: SEQUENCE; Schema: public; Owner: obi
--

CREATE SEQUENCE public.classes_class_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.classes_class_id_seq OWNER TO obi;

--
-- Name: classes_class_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: obi
--

ALTER SEQUENCE public.classes_class_id_seq OWNED BY public.classes.class_id;


--
-- Name: courses; Type: TABLE; Schema: public; Owner: obi; Tablespace: 
--

CREATE TABLE public.courses (
    course_id integer NOT NULL,
    course_name_full character varying(256),
    course_name_short character(5),
    course_teacher_id integer,
    course_language character(2),
    course_idiom character(2)
);


ALTER TABLE public.courses OWNER TO obi;

--
-- Name: courses_course_id_seq; Type: SEQUENCE; Schema: public; Owner: obi
--

CREATE SEQUENCE public.courses_course_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.courses_course_id_seq OWNER TO obi;

--
-- Name: courses_course_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: obi
--

ALTER SEQUENCE public.courses_course_id_seq OWNED BY public.courses.course_id;


--
-- Name: event_type; Type: TABLE; Schema: public; Owner: obi; Tablespace: 
--

CREATE TABLE public.event_type (
    event_id integer,
    event_name character varying(32)
);


ALTER TABLE public.event_type OWNER TO obi;

--
-- Name: events; Type: TABLE; Schema: public; Owner: obi; Tablespace: 
--

CREATE TABLE public.events (
    id integer NOT NULL,
    the_type integer,
    the_time double precision,
    user_id integer,
    course_id integer,
    class_index integer,
    exercise_id integer,
    code text,
    total_tests integer,
    correct_tests integer
);


ALTER TABLE public.events OWNER TO obi;

--
-- Name: events_id_seq; Type: SEQUENCE; Schema: public; Owner: obi
--

CREATE SEQUENCE public.events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.events_id_seq OWNER TO obi;

--
-- Name: events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: obi
--

ALTER SEQUENCE public.events_id_seq OWNED BY public.events.id;


--
-- Name: execute; Type: TABLE; Schema: public; Owner: obi; Tablespace: 
--

CREATE TABLE public.execute (
    id integer NOT NULL,
    user_id integer,
    execute_time double precision,
    exercise_id integer,
    code text,
    class_id integer,
    course_id integer,
    "time" double precision
);


ALTER TABLE public.execute OWNER TO obi;

--
-- Name: exercises; Type: TABLE; Schema: public; Owner: obi; Tablespace: 
--

CREATE TABLE public.exercises (
    exercise_id integer NOT NULL,
    exercise_class_id integer,
    exercise_index integer,
    exercise_total_tests integer
);


ALTER TABLE public.exercises OWNER TO obi;

--
-- Name: exercises_exercise_id_seq; Type: SEQUENCE; Schema: public; Owner: obi
--

CREATE SEQUENCE public.exercises_exercise_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exercises_exercise_id_seq OWNER TO obi;

--
-- Name: exercises_exercise_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: obi
--

ALTER SEQUENCE public.exercises_exercise_id_seq OWNED BY public.exercises.exercise_id;


--
-- Name: hint; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE public.hint (
    id integer NOT NULL,
    user_id integer,
    "time" double precision,
    exercise_id integer,
    code text,
    class_id integer,
    course_id integer
);


ALTER TABLE public.hint OWNER TO postgres;

--
-- Name: load; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE public.load (
    id integer NOT NULL,
    user_id integer,
    "time" double precision,
    class_id integer,
    course_id integer
);


ALTER TABLE public.load OWNER TO postgres;

--
-- Name: load_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.load_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.load_id_seq OWNER TO postgres;

--
-- Name: load_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.load_id_seq OWNED BY public.load.id;


--
-- Name: saciexecute_execute_id_seq; Type: SEQUENCE; Schema: public; Owner: obi
--

CREATE SEQUENCE public.saciexecute_execute_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.saciexecute_execute_id_seq OWNER TO obi;

--
-- Name: saciexecute_execute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: obi
--

ALTER SEQUENCE public.saciexecute_execute_id_seq OWNED BY public.execute.id;


--
-- Name: sacihint_hint_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sacihint_hint_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sacihint_hint_id_seq OWNER TO postgres;

--
-- Name: sacihint_hint_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sacihint_hint_id_seq OWNED BY public.hint.id;


--
-- Name: submit; Type: TABLE; Schema: public; Owner: obi; Tablespace: 
--

CREATE TABLE public.submit (
    id integer NOT NULL,
    user_id integer,
    "time" double precision,
    exercise_id integer,
    code text,
    submit_answer text,
    total_tests integer,
    correct_tests integer,
    class_id integer,
    course_id integer
);


ALTER TABLE public.submit OWNER TO obi;

--
-- Name: sacisubmit_submit_id_seq; Type: SEQUENCE; Schema: public; Owner: obi
--

CREATE SEQUENCE public.sacisubmit_submit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sacisubmit_submit_id_seq OWNER TO obi;

--
-- Name: sacisubmit_submit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: obi
--

ALTER SEQUENCE public.sacisubmit_submit_id_seq OWNED BY public.submit.id;


--
-- Name: saciuser; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE public.saciuser (
    user_id integer NOT NULL,
    user_name character varying(64),
    user_year character varying(64),
    user_email character varying(64),
    user_sex character varying(1),
    user_birth_year integer,
    user_num_backups integer,
    user_reg_date timestamp without time zone DEFAULT now(),
    user_block_email boolean DEFAULT false
);


ALTER TABLE public.saciuser OWNER TO postgres;

--
-- Name: saciuser_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.saciuser_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.saciuser_user_id_seq OWNER TO postgres;

--
-- Name: saciuser_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.saciuser_user_id_seq OWNED BY public.saciuser.user_id;


--
-- Name: teachers; Type: TABLE; Schema: public; Owner: obi; Tablespace: 
--

CREATE TABLE public.teachers (
    teacher_id integer NOT NULL,
    teacher_name character varying(256),
    teacher_email character varying(256),
    teacher_affiliation character varying(256)
);


ALTER TABLE public.teachers OWNER TO obi;

--
-- Name: teachers_teacher_id_seq; Type: SEQUENCE; Schema: public; Owner: obi
--

CREATE SEQUENCE public.teachers_teacher_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.teachers_teacher_id_seq OWNER TO obi;

--
-- Name: teachers_teacher_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: obi
--

ALTER SEQUENCE public.teachers_teacher_id_seq OWNED BY public.teachers.teacher_id;


--
-- Name: backup_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backup ALTER COLUMN backup_id SET DEFAULT nextval('public.backup_backup_id_seq'::regclass);


--
-- Name: class_id; Type: DEFAULT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.classes ALTER COLUMN class_id SET DEFAULT nextval('public.classes_class_id_seq'::regclass);


--
-- Name: course_id; Type: DEFAULT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.courses ALTER COLUMN course_id SET DEFAULT nextval('public.courses_course_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.events ALTER COLUMN id SET DEFAULT nextval('public.events_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.execute ALTER COLUMN id SET DEFAULT nextval('public.saciexecute_execute_id_seq'::regclass);


--
-- Name: exercise_id; Type: DEFAULT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.exercises ALTER COLUMN exercise_id SET DEFAULT nextval('public.exercises_exercise_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hint ALTER COLUMN id SET DEFAULT nextval('public.sacihint_hint_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.load ALTER COLUMN id SET DEFAULT nextval('public.load_id_seq'::regclass);


--
-- Name: user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saciuser ALTER COLUMN user_id SET DEFAULT nextval('public.saciuser_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.submit ALTER COLUMN id SET DEFAULT nextval('public.sacisubmit_submit_id_seq'::regclass);


--
-- Name: teacher_id; Type: DEFAULT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.teachers ALTER COLUMN teacher_id SET DEFAULT nextval('public.teachers_teacher_id_seq'::regclass);


--
-- Name: backup_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY public.backup
    ADD CONSTRAINT backup_pkey PRIMARY KEY (backup_id);


--
-- Name: classes_pkey; Type: CONSTRAINT; Schema: public; Owner: obi; Tablespace: 
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_pkey PRIMARY KEY (class_id);


--
-- Name: courses_pkey; Type: CONSTRAINT; Schema: public; Owner: obi; Tablespace: 
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (course_id);


--
-- Name: events_pkey; Type: CONSTRAINT; Schema: public; Owner: obi; Tablespace: 
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- Name: exercises_pkey; Type: CONSTRAINT; Schema: public; Owner: obi; Tablespace: 
--

ALTER TABLE ONLY public.exercises
    ADD CONSTRAINT exercises_pkey PRIMARY KEY (exercise_id);


--
-- Name: load_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY public.load
    ADD CONSTRAINT load_pkey PRIMARY KEY (id);


--
-- Name: saciexecute_pkey; Type: CONSTRAINT; Schema: public; Owner: obi; Tablespace: 
--

ALTER TABLE ONLY public.execute
    ADD CONSTRAINT saciexecute_pkey PRIMARY KEY (id);


--
-- Name: sacihint_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY public.hint
    ADD CONSTRAINT sacihint_pkey PRIMARY KEY (id);


--
-- Name: sacisubmit_pkey; Type: CONSTRAINT; Schema: public; Owner: obi; Tablespace: 
--

ALTER TABLE ONLY public.submit
    ADD CONSTRAINT sacisubmit_pkey PRIMARY KEY (id);


--
-- Name: saciuser_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY public.saciuser
    ADD CONSTRAINT saciuser_pkey PRIMARY KEY (user_id);


--
-- Name: saciuser_user_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY public.saciuser
    ADD CONSTRAINT saciuser_user_email_key UNIQUE (user_email);


--
-- Name: teachers_pkey; Type: CONSTRAINT; Schema: public; Owner: obi; Tablespace: 
--

ALTER TABLE ONLY public.teachers
    ADD CONSTRAINT teachers_pkey PRIMARY KEY (teacher_id);


--
-- Name: classes_class_course_id_idx; Type: INDEX; Schema: public; Owner: obi; Tablespace: 
--

CREATE INDEX classes_class_course_id_idx ON public.classes USING btree (class_course_id);


--
-- Name: courses_course_name_short_idx; Type: INDEX; Schema: public; Owner: obi; Tablespace: 
--

CREATE INDEX courses_course_name_short_idx ON public.courses USING btree (course_name_short);


--
-- Name: exercises_exercise_class_id_idx; Type: INDEX; Schema: public; Owner: obi; Tablespace: 
--

CREATE INDEX exercises_exercise_class_id_idx ON public.exercises USING btree (exercise_class_id);


--
-- Name: classes_class_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_class_course_id_fkey FOREIGN KEY (class_course_id) REFERENCES public.courses(course_id) ON DELETE CASCADE;


--
-- Name: exercises_exercise_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.exercises
    ADD CONSTRAINT exercises_exercise_class_id_fkey FOREIGN KEY (exercise_class_id) REFERENCES public.classes(class_id) ON DELETE CASCADE;


'''
