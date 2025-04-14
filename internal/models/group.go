package models

type Group struct {
    ID        int    `json:"id"`
    SubdivisionID int `json:"subdivision_id"`
    Name      string `json:"name"`
    Year      int    `json:"year"`
}
