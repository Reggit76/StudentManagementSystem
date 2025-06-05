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
  Autocomplete,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import api from '../services/api';  // Import the configured API instance

const Hostels = () => {
  const [hostelStudents, setHostelStudents] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);

  useEffect(() => {
    fetchHostelStudents();
  }, []);

  const fetchHostelStudents = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/hostels');
      if (response.data && Array.isArray(response.data.items)) {
        setHostelStudents(response.data.items);
      } else {
        setHostelStudents([]);
      }
    } catch (err) {
      console.error('Failed to load hostel students:', err);
      setError(err.response?.data?.detail || 'Не удалось загрузить данные об общежитии');
      setHostelStudents([]);
    } finally {
      setLoading(false);
    }
  };

  const searchStudents = async (searchText) => {
    if (!searchText) {
      setStudents([]);
      return;
    }
    try {
      const response = await api.get('/students/list', { params: { search: searchText } });
      const data = response.data;
      setStudents(Array.isArray(data) ? data : (data.items || []));
    } catch (err) {
      console.error('Failed to search students:', err);
      setStudents([]);
    }
  };

  const handleAddHostelStudent = () => {
    setDialog({
      open: true,
      type: 'add',
      data: {
        studentid: '',
        hostel: 1,
        room: '',
        comment: '',
      },
    });
    setSelectedStudent(null);
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
        await api.delete(`/hostels/${id}`);
        await fetchHostelStudents();
      } catch (err) {
        console.error('Failed to delete hostel record:', err);
        setError(err.response?.data?.detail || 'Не удалось удалить запись');
      }
    }
  };

  const handleDialogClose = () => {
    setDialog({ open: false, type: null, data: null });
    setSelectedStudent(null);
    setError('');
  };

  const handleDialogSave = async () => {
    if (!selectedStudent && dialog.type === 'add') {
      setError('Необходимо выбрать студента');
      return;
    }

    try {
      const data = {
        ...dialog.data,
        studentid: dialog.type === 'add' ? selectedStudent.id : dialog.data.studentid,
      };

      if (dialog.type === 'add') {
        await api.post('/hostels', data);
      } else {
        await api.put(`/hostels/${dialog.data.id}`, data);
      }

      handleDialogClose();
      await fetchHostelStudents();
    } catch (err) {
      console.error('Failed to save hostel record:', err);
      const errorMessage = err.response?.data?.detail || 'Не удалось сохранить данные';
      setError(errorMessage);
    }
  };

  const handleStudentSearch = (event, value) => {
    setSearchTerm(value);
    if (value) {
      searchStudents(value);
    }
  };

  const handleStudentSelect = (event, value) => {
    setSelectedStudent(value);
    if (value) {
      setDialog(prev => ({
        ...prev,
        data: {
          ...prev.data,
          studentid: value.id,
        },
      }));
    }
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
              <TableCell>Общежитие</TableCell>
              <TableCell>Комната</TableCell>
              <TableCell>Комментарий</TableCell>
              <TableCell align="right">Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : hostelStudents.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  Нет данных о проживающих в общежитии
                </TableCell>
              </TableRow>
            ) : (
              hostelStudents.map((student) => (
                <TableRow key={student.id}>
                  <TableCell>{student.student_name}</TableCell>
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
              <Autocomplete
                fullWidth
                options={students}
                getOptionLabel={(option) => option.fullname || ''}
                inputValue={searchTerm}
                onInputChange={handleStudentSearch}
                onChange={handleStudentSelect}
                value={selectedStudent}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Поиск студента"
                    required
                    sx={{ mb: 2 }}
                  />
                )}
                isOptionEqualToValue={(option, value) => option.id === value?.id}
                loading={loading}
                loadingText="Поиск..."
                noOptionsText="Нет подходящих студентов"
              />
            )}
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Общежитие</InputLabel>
              <Select
                name="hostel"
                value={dialog.data?.hostel || 1}
                onChange={(e) => setDialog(prev => ({
                  ...prev,
                  data: { ...prev.data, hostel: e.target.value }
                }))}
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
              onChange={(e) => setDialog(prev => ({
                ...prev,
                data: { ...prev.data, room: e.target.value }
              }))}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Комментарий"
              name="comment"
              value={dialog.data?.comment || ''}
              onChange={(e) => setDialog(prev => ({
                ...prev,
                data: { ...prev.data, comment: e.target.value }
              }))}
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