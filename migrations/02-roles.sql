-- Добавление предопределенных ролей
INSERT INTO Roles (Name) VALUES
    ('CHAIRMAN'),
    ('DEPUTY_CHAIRMAN'),
    ('DIVISION_HEAD'),
    ('DORMITORY_HEAD')
ON CONFLICT (Name) DO NOTHING;

-- Добавляем индекс для оптимизации поиска по имени роли
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);

-- Добавляем комментарии к ролям
COMMENT ON COLUMN roles.name IS 'Название роли (CHAIRMAN - председатель профкома, DEPUTY_CHAIRMAN - зам председателя, DIVISION_HEAD - председатель подразделения, DORMITORY_HEAD - председатель общежития)'; 

-- Добавляем некоторые базовые дополнительные статусы
INSERT INTO additionalstatuses (name) VALUES
    ('Староста'),
    ('Тьютор'),
    ('Профорг'),
    ('Культорг'),
    ('Спорторг')
ON CONFLICT (name) DO NOTHING;