
CREATE TABLE Score_jang
(
	stuno                CHAR(18) NOT NULL ,
	subcode              CHAR(18) NOT NULL ,
	year                 CHAR(18) NULL ,
	testcategory         CHAR(18) NULL ,
	testname             CHAR(18) NULL ,
	score                CHAR(18) NULL ,
	testcatefory         CHAR(18) NULL 
);



CREATE UNIQUE INDEX XPK점수 ON Score_jang
(stuno   ASC,subcode   ASC);



ALTER TABLE Score_jang
	ADD CONSTRAINT  XPK점수 PRIMARY KEY (stuno,subcode);



CREATE TABLE Student_jang
(
	stuno                CHAR(18) NOT NULL ,
	stuname              CHAR(18) NULL 
);



CREATE UNIQUE INDEX XPK학생 ON Student_jang
(stuno   ASC);



ALTER TABLE Student_jang
	ADD CONSTRAINT  XPK학생 PRIMARY KEY (stuno);



CREATE TABLE subject_jang
(
	subcode              CHAR(18) NOT NULL ,
	subname              CHAR(18) NULL ,
	professor            CHAR(18) NULL 
);



CREATE UNIQUE INDEX XPK과목 ON subject_jang
(subcode   ASC);



ALTER TABLE subject_jang
	ADD CONSTRAINT  XPK과목 PRIMARY KEY (subcode);



ALTER TABLE Score_jang
	ADD (CONSTRAINT R_3 FOREIGN KEY (stuno) REFERENCES Student_jang (stuno));



ALTER TABLE Score_jang
	ADD (CONSTRAINT R_4 FOREIGN KEY (subcode) REFERENCES subject_jang (subcode));



CREATE  TRIGGER tI_Score_jang BEFORE INSERT ON Score_jang for each row
-- ERwin Builtin Trigger
-- INSERT trigger on Score_jang 
DECLARE NUMROWS INTEGER;
BEGIN
    /* ERwin Builtin Trigger */
    /* Student_jang  Score_jang on child insert restrict */
    /* ERWIN_RELATION:CHECKSUM="0001f875", PARENT_OWNER="", PARENT_TABLE="Student_jang"
    CHILD_OWNER="", CHILD_TABLE="Score_jang"
    P2C_VERB_PHRASE="", C2P_VERB_PHRASE="", 
    FK_CONSTRAINT="R_3", FK_COLUMNS="stuno" */
    SELECT count(*) INTO NUMROWS
      FROM Student_jang
      WHERE
        /* %JoinFKPK(:%New,Student_jang," = "," AND") */
        :new.stuno = Student_jang.stuno;
    IF (
      /* %NotnullFK(:%New," IS NOT NULL AND") */
      
      NUMROWS = 0
    )
    THEN
      raise_application_error(
        -20002,
        'Cannot insert Score_jang because Student_jang does not exist.'
      );
    END IF;

    /* ERwin Builtin Trigger */
    /* subject_jang  Score_jang on child insert restrict */
    /* ERWIN_RELATION:CHECKSUM="00000000", PARENT_OWNER="", PARENT_TABLE="subject_jang"
    CHILD_OWNER="", CHILD_TABLE="Score_jang"
    P2C_VERB_PHRASE="", C2P_VERB_PHRASE="", 
    FK_CONSTRAINT="R_4", FK_COLUMNS="subcode" */
    SELECT count(*) INTO NUMROWS
      FROM subject_jang
      WHERE
        /* %JoinFKPK(:%New,subject_jang," = "," AND") */
        :new.subcode = subject_jang.subcode;
    IF (
      /* %NotnullFK(:%New," IS NOT NULL AND") */
      
      NUMROWS = 0
    )
    THEN
      raise_application_error(
        -20002,
        'Cannot insert Score_jang because subject_jang does not exist.'
      );
    END IF;


-- ERwin Builtin Trigger
END;
/

CREATE  TRIGGER tU_Score_jang AFTER UPDATE ON Score_jang for each row
-- ERwin Builtin Trigger
-- UPDATE trigger on Score_jang 
DECLARE NUMROWS INTEGER;
BEGIN
  /* ERwin Builtin Trigger */
  /* Student_jang  Score_jang on child update restrict */
  /* ERWIN_RELATION:CHECKSUM="0001fc42", PARENT_OWNER="", PARENT_TABLE="Student_jang"
    CHILD_OWNER="", CHILD_TABLE="Score_jang"
    P2C_VERB_PHRASE="", C2P_VERB_PHRASE="", 
    FK_CONSTRAINT="R_3", FK_COLUMNS="stuno" */
  SELECT count(*) INTO NUMROWS
    FROM Student_jang
    WHERE
      /* %JoinFKPK(:%New,Student_jang," = "," AND") */
      :new.stuno = Student_jang.stuno;
  IF (
    /* %NotnullFK(:%New," IS NOT NULL AND") */
    
    NUMROWS = 0
  )
  THEN
    raise_application_error(
      -20007,
      'Cannot update Score_jang because Student_jang does not exist.'
    );
  END IF;

  /* ERwin Builtin Trigger */
  /* subject_jang  Score_jang on child update restrict */
  /* ERWIN_RELATION:CHECKSUM="00000000", PARENT_OWNER="", PARENT_TABLE="subject_jang"
    CHILD_OWNER="", CHILD_TABLE="Score_jang"
    P2C_VERB_PHRASE="", C2P_VERB_PHRASE="", 
    FK_CONSTRAINT="R_4", FK_COLUMNS="subcode" */
  SELECT count(*) INTO NUMROWS
    FROM subject_jang
    WHERE
      /* %JoinFKPK(:%New,subject_jang," = "," AND") */
      :new.subcode = subject_jang.subcode;
  IF (
    /* %NotnullFK(:%New," IS NOT NULL AND") */
    
    NUMROWS = 0
  )
  THEN
    raise_application_error(
      -20007,
      'Cannot update Score_jang because subject_jang does not exist.'
    );
  END IF;


-- ERwin Builtin Trigger
END;
/


CREATE  TRIGGER  tD_Student_jang AFTER DELETE ON Student_jang for each row
-- ERwin Builtin Trigger
-- DELETE trigger on Student_jang 
DECLARE NUMROWS INTEGER;
BEGIN
    /* ERwin Builtin Trigger */
    /* Student_jang  Score_jang on parent delete restrict */
    /* ERWIN_RELATION:CHECKSUM="0000d0bd", PARENT_OWNER="", PARENT_TABLE="Student_jang"
    CHILD_OWNER="", CHILD_TABLE="Score_jang"
    P2C_VERB_PHRASE="", C2P_VERB_PHRASE="", 
    FK_CONSTRAINT="R_3", FK_COLUMNS="stuno" */
    SELECT count(*) INTO NUMROWS
      FROM Score_jang
      WHERE
        /*  %JoinFKPK(Score_jang,:%Old," = "," AND") */
        Score_jang.stuno = :old.stuno;
    IF (NUMROWS > 0)
    THEN
      raise_application_error(
        -20001,
        'Cannot delete Student_jang because Score_jang exists.'
      );
    END IF;


-- ERwin Builtin Trigger
END;
/

CREATE  TRIGGER tU_Student_jang AFTER UPDATE ON Student_jang for each row
-- ERwin Builtin Trigger
-- UPDATE trigger on Student_jang 
DECLARE NUMROWS INTEGER;
BEGIN
  /* ERwin Builtin Trigger */
  /* Student_jang  Score_jang on parent update restrict */
  /* ERWIN_RELATION:CHECKSUM="0000f502", PARENT_OWNER="", PARENT_TABLE="Student_jang"
    CHILD_OWNER="", CHILD_TABLE="Score_jang"
    P2C_VERB_PHRASE="", C2P_VERB_PHRASE="", 
    FK_CONSTRAINT="R_3", FK_COLUMNS="stuno" */
  IF
    /* %JoinPKPK(:%Old,:%New," <> "," OR ") */
    :old.stuno <> :new.stuno
  THEN
    SELECT count(*) INTO NUMROWS
      FROM Score_jang
      WHERE
        /*  %JoinFKPK(Score_jang,:%Old," = "," AND") */
        Score_jang.stuno = :old.stuno;
    IF (NUMROWS > 0)
    THEN 
      raise_application_error(
        -20005,
        'Cannot update Student_jang because Score_jang exists.'
      );
    END IF;
  END IF;


-- ERwin Builtin Trigger
END;
/


CREATE  TRIGGER  tD_subject_jang AFTER DELETE ON subject_jang for each row
-- ERwin Builtin Trigger
-- DELETE trigger on subject_jang 
DECLARE NUMROWS INTEGER;
BEGIN
    /* ERwin Builtin Trigger */
    /* subject_jang  Score_jang on parent delete restrict */
    /* ERWIN_RELATION:CHECKSUM="0000d603", PARENT_OWNER="", PARENT_TABLE="subject_jang"
    CHILD_OWNER="", CHILD_TABLE="Score_jang"
    P2C_VERB_PHRASE="", C2P_VERB_PHRASE="", 
    FK_CONSTRAINT="R_4", FK_COLUMNS="subcode" */
    SELECT count(*) INTO NUMROWS
      FROM Score_jang
      WHERE
        /*  %JoinFKPK(Score_jang,:%Old," = "," AND") */
        Score_jang.subcode = :old.subcode;
    IF (NUMROWS > 0)
    THEN
      raise_application_error(
        -20001,
        'Cannot delete subject_jang because Score_jang exists.'
      );
    END IF;


-- ERwin Builtin Trigger
END;
/

CREATE  TRIGGER tU_subject_jang AFTER UPDATE ON subject_jang for each row
-- ERwin Builtin Trigger
-- UPDATE trigger on subject_jang 
DECLARE NUMROWS INTEGER;
BEGIN
  /* ERwin Builtin Trigger */
  /* subject_jang  Score_jang on parent update restrict */
  /* ERWIN_RELATION:CHECKSUM="0001042f", PARENT_OWNER="", PARENT_TABLE="subject_jang"
    CHILD_OWNER="", CHILD_TABLE="Score_jang"
    P2C_VERB_PHRASE="", C2P_VERB_PHRASE="", 
    FK_CONSTRAINT="R_4", FK_COLUMNS="subcode" */
  IF
    /* %JoinPKPK(:%Old,:%New," <> "," OR ") */
    :old.subcode <> :new.subcode
  THEN
    SELECT count(*) INTO NUMROWS
      FROM Score_jang
      WHERE
        /*  %JoinFKPK(Score_jang,:%Old," = "," AND") */
        Score_jang.subcode = :old.subcode;
    IF (NUMROWS > 0)
    THEN 
      raise_application_error(
        -20005,
        'Cannot update subject_jang because Score_jang exists.'
      );
    END IF;
  END IF;


-- ERwin Builtin Trigger
END;
/

