import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  IconButton,
  Chip,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import EditIcon from '@mui/icons-material/Edit';
import { groupsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import StudentDetailModal from './StudentDetailModal';

const GroupStudentsModal = ({ open, group, onClose, onStudentSave }) => {
  const { hasPermission } = useAuth();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [studentDialog, setStudentDialog] = useState({ open: false, student: null });

  useEffect(() => {
    if (open && group) {
      fetchStudents();
    }
  }, [open, group]);

  const fetchStudents = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await groupsAPI.getStudents(group.id);
      setStudents(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error('Failed to load group students:', err);
      setError('Не удалось загрузить список студентов группы');
      setStudents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStudentClick = (student) => {
    setStudentDialog({ open: true, student });
  };

  const handleStudentSave = async (studentData) => {
    try {
      await onStudentSave(studentData);
      await fetchStudents(); // Обновляем список
    } catch (err) {
      throw err; // Пробрасываем ошибку в StudentDetailModal
    }
  };

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
        <DialogTitle>
          <Box>
            <Typography variant="h6">
              Студенты группы: {group?.name}
            </Typography>
            <Typography variant="subtitle2" color="text.secondary">
              Подразделение: {group?.subdivision_name} | Год: {group?.year}
            </Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent sx={{ minHeight: 400 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {loading ? (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>ФИО</TableCell>
                    <TableCell>Статус</TableCell>
                    <TableCell>Обучение</TableCell>
                    <TableCell>Год поступления</TableCell>
                    <TableCell align="right">Действия</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {students.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        В группе нет студентов
                      </TableCell>
                    </TableRow>
                  ) : (
                    students.map((student) => (
                      <TableRow 
                        key={student.id}
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => handleStudentClick(student)}
                      >
                        <TableCell>{student.full_name || student.fullname}</TableCell>
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
                              handleStudentClick(student);
                            }}
                            title="Подробнее"
                            size="small"
                          >
                            <VisibilityIcon />
                          </IconButton>
                          {hasPermission('canManageStudents') && (
                            <IconButton
                              color="primary"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleStudentClick(student);
                              }}
                              title="Редактировать"
                              size="small"
                            >
                              <EditIcon />
                            </IconButton>
                          )}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DialogContent>
        
        <DialogActions>
          <Typography variant="body2" color="text.secondary" sx={{ flexGrow: 1, ml: 2 }}>
            Всего студентов: {students.length}
          </Typography>
          <Button onClick={onClose}>Закрыть</Button>
        </DialogActions>
      </Dialog>

      {/* Модальное окно студента */}
      <StudentDetailModal
        open={studentDialog.open}
        student={studentDialog.student}
        onClose={() => setStudentDialog({ open: false, student: null })}
        onSave={handleStudentSave}
      />
    </>
  );
};

export default GroupStudentsModal;