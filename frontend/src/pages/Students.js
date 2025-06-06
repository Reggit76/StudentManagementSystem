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
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  TextField,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import VisibilityIcon from '@mui/icons-material/Visibility';
import InputAdornment from '@mui/material/InputAdornment';
import { studentsAPI, groupsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import StudentForm from '../components/StudentForm';
import StudentDetailModal from '../components/StudentDetailModal';

const Students = () => {
  const { user, hasPermission } = useAuth();
  const [students, setStudents] = useState([]);
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });
  const [detailDialog, setDetailDialog] = useState({ open: false, student: null });

  useEffect(() => {
    fetchGroups();
    fetchStudents();
  }, []);

  useEffect(() => {
    // Debounce search
    const timeoutId = setTimeout(() => {
      fetchStudents();
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, selectedGroup]);

  const fetchGroups = async () => {
    try {
      const response = await groupsAPI.getAll();
      setGroups(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error('Failed to load groups:', err);
      setGroups([]);
    }
  };

  const fetchStudents = async (params = {}) => {
    setLoading(true);
    setError('');
    try {
      const queryParams = {
        group_id: selectedGroup || undefined,
        search: searchTerm || undefined,
        ...params,
      };
      
      Object.keys(queryParams).forEach(key => {
        if (queryParams[key] === undefined || queryParams[key] === '') {
          delete queryParams[key];
        }
      });

      const response = await studentsAPI.getAll(queryParams);
      const studentsData = response.data;
      
      if (Array.isArray(studentsData)) {
        setStudents(studentsData);
      } else {
        console.error('Expected array, got:', studentsData);
        setStudents([]);
        setError('Некорректный формат данных от сервера');
      }
    } catch (err) {
      console.error('Failed to load students:', err);
      setError('Не удалось загрузить список студентов');
      setStudents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddStudent = () => {
    setDialog({
      open: true,
      type: 'add',
      data: {
        group_id: selectedGroup || '',
        full_name: '',
        is_active: false,
        is_budget: true,
        year: new Date().getFullYear(),
      },
    });
  };

  const handleEditStudent = (student, event) => {
    event.stopPropagation(); // Предотвращаем открытие детальной модалки
    setDialog({
      open: true,
      type: 'edit',
      data: student,
    });
  };

  const handleDeleteStudent = async (id, event) => {
    event.stopPropagation(); // Предотвращаем открытие детальной модалки
    if (window.confirm('Вы уверены, что хотите удалить этого студента?')) {
      try {
        await studentsAPI.delete(id);
        fetchStudents();
      } catch (err) {
        setError('Не удалось удалить студента');
      }
    }
  };

  const handleRowClick = (student) => {
    setDetailDialog({ open: true, student });
  };

  const handleGroupChange = (event) => {
    setSelectedGroup(event.target.value);
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleDialogClose = () => {
    setDialog({ open: false, type: null, data: null });
  };

  const handleDialogSave = async (formData) => {
    try {
      if (dialog.type === 'add') {
        await studentsAPI.create(formData);
      } else {
        await studentsAPI.update(dialog.data.id, formData);
      }
      handleDialogClose();
      fetchStudents();
    } catch (err) {
      console.error('Failed to save student:', err);
      setError('Не удалось сохранить студента: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDetailSave = async (studentData) => {
    try {
      if (detailDialog.student) {
        await studentsAPI.update(detailDialog.student.id, studentData);
      } else {
        await studentsAPI.create(studentData);
      }
      fetchStudents();
    } catch (err) {
      console.error('Failed to save student:', err);
      throw err;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Студенты
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            size="small"
            placeholder="Поиск студентов..."
            value={searchTerm}
            onChange={handleSearch}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel id="group-select-label">Группа</InputLabel>
            <Select
              labelId="group-select-label"
              value={selectedGroup}
              label="Группа"
              onChange={handleGroupChange}
              size="small"
            >
              <MenuItem value="">Все группы</MenuItem>
              {groups.map((group) => (
                <MenuItem key={group.id} value={group.id}>
                  {group.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          {hasPermission('canManageStudents') && (
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleAddStudent}
            >
              Добавить студента
            </Button>
          )}
        </Box>
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
              <TableCell>ФИО</TableCell>
              <TableCell>Группа</TableCell>
              <TableCell>Статус</TableCell>
              <TableCell>Обучение</TableCell>
              <TableCell>Год поступления</TableCell>
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
            ) : students.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  Студенты не найдены
                </TableCell>
              </TableRow>
            ) : (
              students.map((student) => (
                <TableRow 
                  key={student.id}
                  hover
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    }
                  }}
                  onClick={() => handleRowClick(student)}
                >
                  <TableCell>{student.full_name || student.fullname}</TableCell>
                  <TableCell>{student.group_name}</TableCell>
                  <TableCell>
                    <Chip
                      label={student.is_active || student.isactive ? 'Активный' : 'Неактивный'}
                      color={student.is_active || student.isactive ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={student.is_budget || student.isbudget ? 'Бюджет' : 'Контракт'}
                      color={student.is_budget || student.isbudget ? 'primary' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{student.year}</TableCell>
                  <TableCell align="right">
                    <IconButton
                      color="info"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRowClick(student);
                      }}
                      title="Подробнее"
                    >
                      <VisibilityIcon />
                    </IconButton>
                    {hasPermission('canManageStudents') && (
                      <>
                        <IconButton
                          color="primary"
                          onClick={(e) => handleEditStudent(student, e)}
                          title="Редактировать"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          color="error"
                          onClick={(e) => handleDeleteStudent(student.id, e)}
                          title="Удалить"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Простая форма для быстрого создания/редактирования */}
      <Dialog open={dialog.open} onClose={handleDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialog.type === 'add' ? 'Добавить студента' : 'Редактировать студента'}
        </DialogTitle>
        <DialogContent>
          {dialog.open && (
            <StudentForm
              data={dialog.data}
              onSubmit={handleDialogSave}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Отмена</Button>
        </DialogActions>
      </Dialog>

      {/* Детальная модалка студента */}
      <StudentDetailModal
        open={detailDialog.open}
        student={detailDialog.student}
        onClose={() => setDetailDialog({ open: false, student: null })}
        onSave={handleDetailSave}
      />
    </Container>
  );
};

export default Students;