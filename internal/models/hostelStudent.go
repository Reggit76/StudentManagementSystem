package models

type HostelStudent struct {
	ID        int    `json:"id"`
	StudentID int    `json:"student_id"`
	Hostel    int    `json:"hostel"`
	Room      int    `json:"room"`
	Comment   string `json:"comment,omitempty"`
}
