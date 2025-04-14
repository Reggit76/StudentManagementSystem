package repository

import (
	"database/sql"
	"log"

	"Student-management-system/internal/models"
)

type StudentRepository struct {
	db *sql.DB
}

func NewStudentRepository(db *sql.DB) *StudentRepository {
	return &StudentRepository{db: db}
}

func (r *StudentRepository) GetByID(id int) (*models.Student, error) {
	query := `
    SELECT id, full_name, is_active, is_budget, group_id, data_id, year 
    FROM students 
    WHERE id = $1`

	row := r.db.QueryRow(query, id)

	var s models.Student
	err := row.Scan(
		&s.ID,
		&s.FullName,
		&s.IsActive,
		&s.IsBudget,
		&s.GroupID,
		&s.DataID,
		&s.Year,
	)
	if err != nil {
		log.Printf("Ошибка при получении студента: %v", err)
		return nil, err
	}

	return &s, nil
}

func (r *StudentRepository) Create(student *models.Student) error {
	query := `
    INSERT INTO students (full_name, is_active, is_budget, group_id, data_id, year)
    VALUES ($1, $2, $3, $4, $5, $6) RETURNING id`

	err := r.db.QueryRow(query,
		student.FullName,
		student.IsActive,
		student.IsBudget,
		student.GroupID,
		student.DataID,
		student.Year,
	).Scan(&student.ID)
	if err != nil {
		log.Printf("Ошибка создания студента: %v", err)
		return err
	}

	return nil
}
