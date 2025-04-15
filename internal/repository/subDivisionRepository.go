package repository

import (
	"database/sql"
	"log"

	"Student-management-system/internal/models"
)

type SubdivisionRepository struct {
	db *sql.DB
}

func NewSubdivisionRepository(db *sql.DB) *SubdivisionRepository {
	return &SubdivisionRepository{db: db}
}

func (r *SubdivisionRepository) GetByID(id int) (*models.Subdivision, error) {
	query := "SELECT id, name FROM subdivisions WHERE id = $1"
	row := r.db.QueryRow(query, id)

	var s models.Subdivision
	err := row.Scan(&s.ID, &s.Name)
	if err != nil {
		log.Printf("Ошибка при получении подразделения: %v", err)
		return nil, err
	}

	return &s, nil
}

func (r *SubdivisionRepository) Create(subdiv *models.Subdivision) error {
	query := "INSERT INTO subdivisions (name) VALUES ($1) RETURNING id"
	err := r.db.QueryRow(query, subdiv.Name).Scan(&subdiv.ID)
	if err != nil {
		log.Printf("Ошибка создания подразделения: %v", err)
		return err
	}

	return nil
}

func (r *SubdivisionRepository) Update(subdiv *models.Subdivision) error {
	query := "UPDATE subdivisions SET name = $1 WHERE id = $2"
	_, err := r.db.Exec(query, subdiv.Name, subdiv.ID)
	if err != nil {
		log.Printf("Ошибка обновления подразделения: %v", err)
		return err
	}

	return nil
}

// Delete
func (r *SubdivisionRepository) Delete(id int) error {
	query := "DELETE FROM subdivisions WHERE id = $1"
	_, err := r.db.Exec(query, id)
	return err
}
