package models

type Contribution struct {
	ID          int     `json:"id"`
	StudentID   int     `json:"student_id"`
	Semester    int     `json:"semester"`
	Amount      float64 `json:"amount,string"`
	PaymentDate string  `json:"payment_date"`
	Year        int     `json:"year"`
}
