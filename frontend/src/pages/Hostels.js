import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

const Hostels = () => {
  const [hostelStudents, setHostelStudents] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });

  useEffect(() => {
    fetchHostelStudents();
    fetchStudents();
  }, []);

  const fetchHostelStudents = async () => {
    setLoading(true);
    setError('');
    try {
      // Пока используем моковые данные, так как в БД пусто
      const mockHostelStudents = [];
      setHostelStudents(mockHostelStudents);
    } catch (err) {
      console.error('Failed to load hostel students:', err);
      setError('Не удалось загрузить данные об общежитии');
      setHostelStudents([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStudents = async () => {
    try {
      // TODO: Загрузить список студентов для выпадающего списка
      const mockStudents = [];
      setStudents(mockStudents);
    } catch (err) {
      console.error('Failed to load students:', err);
      setStudents([]);
    }
  };

  const handleAddHostelStudent = () => {
    setDialog({
      open: true,
      type: 'add',
      data: {
        student_id: '',
        hostel: 1,
        room: '',
        comment: '',
      },
    });
  };

  const handleEditHostelStudent = (student) => {
    setDialog({
      open: true,
      type: 'edit',
      data: student,
    });
  };

  const handleDeleteHostelStudent = async (id) => {
    if (window.confirm('Вы уверены, что хотите удалить эту запись?')) {
      try {
        // TODO: Реальное удаление
        setHostelStudents(hostelStudents.filter(h => h.id !== id));
      } catch (err) {
        setError('Не удалось удалить запись');
      }
    }
  };

  const handleDialogClose = () => {
    setDialog({ open: false, type: null, data: null });
  };

  const handleDialogSave = async () => {
    try {
      // TODO: Реальное сохранение
      handleDialogClose();
      fetchHostelStudents();
    } catch (err) {
      setError('Не удалось сохранить данные');
    }
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setDialog(prev => ({
      ...prev,
      data: { ...prev.data, [name]: value },
    }));
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Проживающие в общежитии
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleAddHostelStudent}
        >
          Добавить проживающего
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ФИО студента</TableCell>
              <TableCell>Группа</TableCell>
              <TableCell>Общежитие</TableCell>
              <TableCell>Комната</TableCell>
              <TableCell>Комментарий</TableCell>
              <TableCell align="right">Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : hostelStudents.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  Нет данных о проживающих в общежитии
                </TableCell>
              </TableRow>
            ) : (
              hostelStudents.map((student) => (
                <TableRow key={student.id}>
                  <TableCell>{student.student_name}</TableCell>
                  <TableCell>{student.group_name}</TableCell>
                  <TableCell>№{student.hostel}</TableCell>
                  <TableCell>{student.room}</TableCell>
                  <TableCell>{student.comment}</TableCell>
                  <TableCell align="right">
                    <IconButton
                      color="primary"
                      onClick={() => handleEditHostelStudent(student)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      color="error"
                      onClick={() => handleDeleteHostelStudent(student.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialog.open} onClose={handleDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialog.type === 'add' ? 'Добавить проживающего' : 'Редактировать данные'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ mt: 2 }}>
            {dialog.type === 'add' && (
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Студент</InputLabel>
                <Select
                  name="student_id"
                  value={dialog.data?.student_id || ''}
                  onChange={handleInputChange}
                  label="Студент"
                  required
                >
                  {students.map((student) => (
                    <MenuItem key={student.id} value={student.id}>
                      {student.full_name} ({student.group_name})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Общежитие</InputLabel>
              <Select
                name="hostel"
                value={dialog.data?.hostel || 1}
                onChange={handleInputChange}
                label="Общежитие"
                required
              >
                {Array.from({ length: 20 }, (_, i) => i + 1).map((num) => (
                  <MenuItem key={num} value={num}>
                    Общежитие №{num}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Номер комнаты"
              name="room"
              type="number"
              value={dialog.data?.room || ''}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Комментарий"
              name="comment"
              value={dialog.data?.comment || ''}
              onChange={handleInputChange}
              multiline
              rows={3}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Отмена</Button>
          <Button onClick={handleDialogSave} color="primary">
            Сохранить
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Hostels;