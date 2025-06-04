-- Добавление предопределенных ролей
INSERT INTO Roles (Name) VALUES
    ('CHAIRMAN'),
    ('DEPUTY_CHAIRMAN'),
    ('DIVISION_HEAD'),
    ('DORMITORY_HEAD')
ON CONFLICT (Name) DO NOTHING;

-- Добавляем индекс для оптимизации поиска по имени роли
CREATE INDEX idx_roles_name ON Roles(Name);

-- Добавляем комментарии к ролям
COMMENT ON COLUMN Roles.Name IS 'Название роли (CHAIRMAN - председатель профкома, DEPUTY_CHAIRMAN - зам председателя, DIVISION_HEAD - председатель подразделения, DORMITORY_HEAD - председатель общежития)'; 