package models

type Student struct {
    ID          int    `json:"id"`
    FullName    string `json:"full_name"`
    IsActive    bool   `json:"is_active"`
    IsBudget    bool   `json:"is_budget"`
    GroupID     int    `json:"group_id"`
    DataID      *int   `json:"data_id,omitempty"`
    Year        int    `json:"year"`
}
