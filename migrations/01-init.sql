CREATE TABLE Subdivisions (
  ID SERIAL PRIMARY KEY,
  Name VARCHAR(16) UNIQUE NOT NULL
);

CREATE TABLE Roles (
  ID SERIAL PRIMARY KEY,
  Name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE AdditionalStatuses (
  ID SERIAL PRIMARY KEY,
  Name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE Groups (
  ID SERIAL PRIMARY KEY,
  SubdivisionID INT NOT NULL,
  Name VARCHAR(255) UNIQUE NOT NULL,
  Year INT NOT NULL DEFAULT 2024
);

CREATE TABLE Users (
  ID SERIAL PRIMARY KEY,
  Login VARCHAR(50) UNIQUE NOT NULL,
  PasswordHash VARCHAR(255) NOT NULL,
  SubdivisionID INT
);

CREATE TABLE UserRoles (
  UserID INT NOT NULL,
  RoleID INT NOT NULL,
  PRIMARY KEY (UserID, RoleID)
);

CREATE TABLE StudentData (
  ID SERIAL PRIMARY KEY,
  Phone VARCHAR(15),
  Email VARCHAR(255) UNIQUE,
  Birthday DATETIME
);

CREATE TABLE Students (
  ID SERIAL PRIMARY KEY,
  GroupID INT NOT NULL,
  FullName VARCHAR(255) NOT NULL,
  IsActive BOOLEAN NOT NULL DEFAULT false,
  IsBudget BOOLEAN NOT NULL,
  DataID INT UNIQUE,
  Year INT NOT NULL DEFAULT 2024
);

CREATE TABLE HostelStudents (
  ID SERIAL PRIMARY KEY,
  StudentID INT UNIQUE NOT NULL,
  Hostel INT NOT NULL,
  Room INT NOT NULL,
  Comment VARCHAR(255)
);

CREATE TABLE StudentAdditionalStatuses (
  StudentID INT NOT NULL,
  StatusID INT NOT NULL,
  PRIMARY KEY (StudentID, StatusID)
);

CREATE TABLE Contributions (
  ID SERIAL PRIMARY KEY,
  StudentID INT NOT NULL,
  Semester INT NOT NULL,
  Amount DECIMAL(10,2) NOT NULL,
  PaymentDate DATE,
  Year INT NOT NULL DEFAULT 2024
);

CREATE UNIQUE INDEX ON Contributions (StudentID, Year);

COMMENT ON TABLE Subdivisions IS 'Подразделения университета';

COMMENT ON TABLE Roles IS 'Роли пользователей системы';

COMMENT ON TABLE AdditionalStatuses IS 'Дополнительные статусы студентов';

COMMENT ON TABLE Groups IS 'Учебные группы с привязкой к учебному году';

COMMENT ON TABLE Users IS 'Пользователи системы с привязкой к подразделениям';

COMMENT ON TABLE StudentData IS 'Информация о студенте';

COMMENT ON TABLE Students IS 'Основные данные студентов с привязкой к учебному году';

COMMENT ON TABLE HostelStudents IS 'Статус проживания в общежитии';

COMMENT ON TABLE Contributions IS 'Взносы студентов за семестры с привязкой к учебному году';

ALTER TABLE Groups ADD FOREIGN KEY (SubdivisionID) REFERENCES Subdivisions (ID) ON DELETE CASCADE;

ALTER TABLE Users ADD FOREIGN KEY (SubdivisionID) REFERENCES Subdivisions (ID) ON DELETE SET NULL;

ALTER TABLE UserRoles ADD FOREIGN KEY (UserID) REFERENCES Users (ID) ON DELETE CASCADE;

ALTER TABLE UserRoles ADD FOREIGN KEY (RoleID) REFERENCES Roles (ID) ON DELETE CASCADE;

ALTER TABLE Students ADD FOREIGN KEY (GroupID) REFERENCES Groups (ID) ON DELETE CASCADE;

ALTER TABLE Students ADD FOREIGN KEY (DataID) REFERENCES StudentData (ID) ON DELETE SET NULL;

ALTER TABLE HostelStudents ADD FOREIGN KEY (StudentID) REFERENCES Students (ID) ON DELETE CASCADE;

ALTER TABLE StudentAdditionalStatuses ADD FOREIGN KEY (StudentID) REFERENCES Students (ID) ON DELETE CASCADE;

ALTER TABLE StudentAdditionalStatuses ADD FOREIGN KEY (StatusID) REFERENCES AdditionalStatuses (ID) ON DELETE CASCADE;

ALTER TABLE Contributions ADD FOREIGN KEY (StudentID) REFERENCES Students (ID) ON DELETE CASCADE;
