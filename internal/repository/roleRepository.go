package repository

import (
	"database/sql"
	"log"

	"Student-management-system/internal/models"
)

type RoleRepository struct {
	db *sql.DB
}

func NewRoleRepository(db *sql.DB) *RoleRepository {
	return &RoleRepository{db: db}
}

func (r *RoleRepository) GetByID(id int) (*models.Role, error) {
	query := "SELECT id, name FROM roles WHERE id = $1"
	row := r.db.QueryRow(query, id)

	var role models.Role
	err := row.Scan(&role.ID, &role.Name)
	if err != nil {
		log.Printf("Ошибка при получении роли: %v", err)
		return nil, err
	}

	return &role, nil
}

func (r *RoleRepository) Create(role *models.Role) error {
	query := "INSERT INTO roles (name) VALUES ($1) RETURNING id"
	err := r.db.QueryRow(query, role.Name).Scan(&role.ID)
	if err != nil {
		log.Printf("Ошибка создания роли: %v", err)
		return err
	}

	return nil
}

func (r *RoleRepository) Update(role *models.Role) error {
	query := "UPDATE roles SET name = $1 WHERE id = $2"
	_, err := r.db.Exec(query, role.Name, role.ID)
	return err
}

func (r *RoleRepository) Delete(id int) error {
	query := "DELETE FROM roles WHERE id = $1"
	_, err := r.db.Exec(query, id)
	return err
}
