-- Создание таблицы для логирования изменений
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INT,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id INT,
    old_data JSONB,
    new_data JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_audit_logs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Индексы для оптимизации поиска
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_table_record ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Комментарий к таблице
COMMENT ON TABLE audit_logs IS 'Журнал аудита изменений в системе';
COMMENT ON COLUMN audit_logs.action IS 'Тип действия: CREATE, UPDATE, DELETE, VIEW';
COMMENT ON COLUMN audit_logs.table_name IS 'Название таблицы, в которой произошло изменение';
COMMENT ON COLUMN audit_logs.old_data IS 'Старые данные записи (для UPDATE и DELETE)';
COMMENT ON COLUMN audit_logs.new_data IS 'Новые данные записи (для CREATE и UPDATE)';