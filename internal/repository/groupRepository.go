package repository

import (
	"database/sql"
	"log"

	"Student-management-system/internal/models"
)

type GroupRepository struct {
	db *sql.DB
}

func NewGroupRepository(db *sql.DB) *GroupRepository {
	return &GroupRepository{db: db}
}

func (r *GroupRepository) GetByID(id int) (*models.Group, error) {
	query := "SELECT id, subdivision_id, name, year FROM groups WHERE id = $1"
	row := r.db.QueryRow(query, id)

	var group models.Group
	err := row.Scan(&group.ID, &group.SubdivisionID, &group.Name, &group.Year)
	if err != nil {
		log.Printf("Ошибка при получении группы: %v", err)
		return nil, err
	}

	return &group, nil
}

func (r *GroupRepository) Create(group *models.Group) error {
	query := "INSERT INTO groups (subdivision_id, name, year) VALUES ($1, $2, $3) RETURNING id"
	err := r.db.QueryRow(query, group.SubdivisionID, group.Name, group.Year).Scan(&group.ID)
	if err != nil {
		log.Printf("Ошибка создания группы: %v", err)
		return err
	}

	return nil
}

func (r *GroupRepository) Update(group *models.Group) error {
	query := "UPDATE groups SET subdivision_id = $1, name = $2, year = $3 WHERE id = $4"
	_, err := r.db.Exec(query, group.SubdivisionID, group.Name, group.Year, group.ID)
	return err
}

func (r *GroupRepository) Delete(id int) error {
	query := "DELETE FROM groups WHERE id = $1"
	_, err := r.db.Exec(query, id)
	return err
}
