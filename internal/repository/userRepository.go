package repository

import (
	"database/sql"
	"log"

	"Student-management-system/internal/models"
)

type UserRepository struct {
	db *sql.DB
}

func NewUserRepository(db *sql.DB) *UserRepository {
	return &UserRepository{db: db}
}

func (r *UserRepository) GetByID(id int) (*models.User, error) {
	query := "SELECT id, login, password_hash, subdivision_id FROM users WHERE id = $1"
	row := r.db.QueryRow(query, id)

	var u models.User
	err := row.Scan(&u.ID, &u.Login, &u.PasswordHash, &u.SubdivisionID)
	if err != nil {
		log.Printf("Ошибка при получении пользователя: %v", err)
		return nil, err
	}

	return &u, nil
}

func (r *UserRepository) Create(user *models.User) error {
	query := "INSERT INTO users (login, password_hash, subdivision_id) VALUES ($1, $2, $3) RETURNING id"
	err := r.db.QueryRow(query, user.Login, user.PasswordHash, user.SubdivisionID).Scan(&user.ID)
	if err != nil {
		log.Printf("Ошибка создания пользователя: %v", err)
		return err
	}

	return nil
}
