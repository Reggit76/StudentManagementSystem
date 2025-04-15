package repository

import (
	"database/sql"
	"log"

	"Student-management-system/internal/models"
)

type StudentDataRepository struct {
	db *sql.DB
}

func NewStudentDataRepository(db *sql.DB) *StudentDataRepository {
	return &StudentDataRepository{db: db}
}

func (r *StudentDataRepository) GetByID(id int) (*models.StudentData, error) {
	query := "SELECT id, phone, email, birthday FROM student_data WHERE id = $1"
	row := r.db.QueryRow(query, id)

	var data models.StudentData
	err := row.Scan(&data.ID, &data.Phone, &data.Email, &data.Birthday)
	if err != nil {
		log.Printf("Ошибка при получении данных студента: %v", err)
		return nil, err
	}

	return &data, nil
}

func (r *StudentDataRepository) Create(data *models.StudentData) error {
	query := "INSERT INTO student_data (phone, email, birthday) VALUES ($1, $2, $3) RETURNING id"
	err := r.db.QueryRow(query, data.Phone, data.Email, data.Birthday).Scan(&data.ID)
	if err != nil {
		log.Printf("Ошибка создания данных студента: %v", err)
		return err
	}

	return nil
}

func (r *StudentDataRepository) Update(data *models.StudentData) error {
	query := "UPDATE student_data SET phone = $1, email = $2, birthday = $3 WHERE id = $4"
	_, err := r.db.Exec(query, data.Phone, data.Email, data.Birthday, data.ID)
	return err
}

func (r *StudentDataRepository) Delete(id int) error {
	query := "DELETE FROM student_data WHERE id = $1"
	_, err := r.db.Exec(query, id)
	return err
}
