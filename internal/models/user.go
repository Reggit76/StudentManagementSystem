package models

type User struct {
    ID           int    `json:"id"`
    Login        string `json:"login"`
    PasswordHash string `json:"password_hash"`
    SubdivisionID *int  `json:"subdivision_id,omitempty"` // Может быть NULL
}

