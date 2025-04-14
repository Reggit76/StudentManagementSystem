package models

type StudentData struct {
    ID       int    `json:"id"`
    Phone    string `json:"phone,omitempty"`
    Email    string `json:"email,omitempty"`
    Birthday string `json:"birthday,omitempty"` // Или time.Time, если нужно
}
