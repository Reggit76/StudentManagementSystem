package repository

import (
	"database/sql"
	"log"

	"Student-management-system/internal/models"
)

type AdditionalStatusRepository struct {
	db *sql.DB
}

func NewAdditionalStatusRepository(db *sql.DB) *AdditionalStatusRepository {
	return &AdditionalStatusRepository{db: db}
}

func (r *AdditionalStatusRepository) GetByID(id int) (*models.AdditionalStatus, error) {
	query := "SELECT id, name FROM additional_statuses WHERE id = $1"
	row := r.db.QueryRow(query, id)

	var status models.AdditionalStatus
	err := row.Scan(&status.ID, &status.Name)
	if err != nil {
		log.Printf("Ошибка при получении статуса: %v", err)
		return nil, err
	}

	return &status, nil
}

func (r *AdditionalStatusRepository) Create(status *models.AdditionalStatus) error {
	query := "INSERT INTO additional_statuses (name) VALUES ($1) RETURNING id"
	err := r.db.QueryRow(query, status.Name).Scan(&status.ID)
	if err != nil {
		log.Printf("Ошибка создания статуса: %v", err)
		return err
	}

	return nil
}

func (r *AdditionalStatusRepository) Delete(id int) error {
	query := "DELETE FROM additional_statuses WHERE id = $1"
	_, err := r.db.Exec(query, id)
	return err
}
