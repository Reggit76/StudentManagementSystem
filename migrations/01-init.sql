-- Создание основных таблиц системы управления профсоюзом

-- Подразделения
CREATE TABLE subdivisions (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Роли пользователей
CREATE TABLE roles (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Дополнительные статусы студентов
CREATE TABLE additionalstatuses (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Группы
CREATE TABLE groups (
  id SERIAL PRIMARY KEY,
  subdivisionid INT NOT NULL,
  name VARCHAR(255) UNIQUE NOT NULL,
  year INT NOT NULL DEFAULT EXTRACT(YEAR FROM CURRENT_DATE),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_groups_subdivision FOREIGN KEY (subdivisionid) REFERENCES subdivisions(id) ON DELETE CASCADE
);

-- Пользователи системы
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  login VARCHAR(50) UNIQUE NOT NULL,
  passwordhash VARCHAR(255) NOT NULL,
  subdivisionid INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_users_subdivision FOREIGN KEY (subdivisionid) REFERENCES subdivisions(id) ON DELETE SET NULL
);

-- Связь пользователей и ролей
CREATE TABLE userroles (
  userid INT NOT NULL,
  roleid INT NOT NULL,
  PRIMARY KEY (userid, roleid),
  CONSTRAINT fk_userroles_user FOREIGN KEY (userid) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_userroles_role FOREIGN KEY (roleid) REFERENCES roles(id) ON DELETE CASCADE
);

-- Дополнительные данные студентов
CREATE TABLE studentdata (
  id SERIAL PRIMARY KEY,
  phone VARCHAR(20),
  email VARCHAR(255),
  birthday DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Студенты
CREATE TABLE students (
  id SERIAL PRIMARY KEY,
  groupid INT NOT NULL,
  fullname VARCHAR(255) NOT NULL,
  isactive BOOLEAN NOT NULL DEFAULT false,
  isbudget BOOLEAN NOT NULL DEFAULT true,
  dataid INT UNIQUE,
  year INT NOT NULL DEFAULT EXTRACT(YEAR FROM CURRENT_DATE),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_students_group FOREIGN KEY (groupid) REFERENCES groups(id) ON DELETE CASCADE,
  CONSTRAINT fk_students_data FOREIGN KEY (dataid) REFERENCES studentdata(id) ON DELETE SET NULL
);

-- Проживающие в общежитии
CREATE TABLE hostelstudents (
  id SERIAL PRIMARY KEY,
  studentid INT UNIQUE NOT NULL,
  hostel INT NOT NULL CHECK (hostel BETWEEN 1 AND 20),
  room INT NOT NULL CHECK (room > 0),
  comment TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_hostelstudents_student FOREIGN KEY (studentid) REFERENCES students(id) ON DELETE CASCADE
);

-- Связь студентов и дополнительных статусов
CREATE TABLE studentadditionalstatuses (
  studentid INT NOT NULL,
  statusid INT NOT NULL,
  PRIMARY KEY (studentid, statusid),
  CONSTRAINT fk_studentstatuses_student FOREIGN KEY (studentid) REFERENCES students(id) ON DELETE CASCADE,
  CONSTRAINT fk_studentstatuses_status FOREIGN KEY (statusid) REFERENCES additionalstatuses(id) ON DELETE CASCADE
);

-- Взносы студентов
CREATE TABLE contributions (
  id SERIAL PRIMARY KEY,
  studentid INT NOT NULL,
  semester INT NOT NULL CHECK (semester IN (1, 2)),
  amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
  paymentdate DATE,
  year INT NOT NULL DEFAULT EXTRACT(YEAR FROM CURRENT_DATE),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_contributions_student FOREIGN KEY (studentid) REFERENCES students(id) ON DELETE CASCADE,
  CONSTRAINT uk_contributions_student_year UNIQUE (studentid, year)
);

-- Создание индексов для оптимизации
CREATE INDEX idx_groups_subdivision ON groups(subdivisionid);
CREATE INDEX idx_groups_year ON groups(year);
CREATE INDEX idx_students_group ON students(groupid);
CREATE INDEX idx_students_active ON students(isactive);
CREATE INDEX idx_students_year ON students(year);
CREATE INDEX idx_students_fullname ON students(fullname);
CREATE INDEX idx_hostelstudents_hostel ON hostelstudents(hostel);
CREATE INDEX idx_hostelstudents_room ON hostelstudents(hostel, room);
CREATE INDEX idx_contributions_student ON contributions(studentid);
CREATE INDEX idx_contributions_year ON contributions(year);
CREATE INDEX idx_contributions_payment ON contributions(paymentdate);

-- Функция обновления timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггеры для автоматического обновления updated_at
CREATE TRIGGER update_subdivisions_updated_at BEFORE UPDATE ON subdivisions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_additionalstatuses_updated_at BEFORE UPDATE ON additionalstatuses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_groups_updated_at BEFORE UPDATE ON groups FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_studentdata_updated_at BEFORE UPDATE ON studentdata FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_hostelstudents_updated_at BEFORE UPDATE ON hostelstudents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_contributions_updated_at BEFORE UPDATE ON contributions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Комментарии к таблицам
COMMENT ON TABLE subdivisions IS 'Подразделения университета';
COMMENT ON TABLE roles IS 'Роли пользователей системы';
COMMENT ON TABLE additionalstatuses IS 'Дополнительные статусы студентов';
COMMENT ON TABLE groups IS 'Учебные группы';
COMMENT ON TABLE users IS 'Пользователи системы';
COMMENT ON TABLE studentdata IS 'Дополнительная информация о студентах';
COMMENT ON TABLE students IS 'Основные данные студентов';
COMMENT ON TABLE hostelstudents IS 'Данные о проживании в общежитии';
COMMENT ON TABLE contributions IS 'Взносы студентов';