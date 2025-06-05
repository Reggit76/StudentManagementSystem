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
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import EditIcon from '@mui/icons-material/Edit';
import { groupsAPI, studentsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import GroupStudentsModal from './GroupStudentsModal';

const SubdivisionGroupsModal = ({ open, subdivision, onClose }) => {
  const { hasPermission } = useAuth();
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [studentsDialog, setStudentsDialog] = useState({ open: false, group: null });

  useEffect(() => {
    if (open && subdivision) {
      fetchGroups();
    }
  }, [open, subdivision]);

  const fetchGroups = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await groupsAPI.getAll({ subdivision_id: subdivision.id });
      const groupsData = response.data;
      
      if (Array.isArray(groupsData)) {
        setGroups(groupsData);
      } else if (groupsData && groupsData.items) {
        setGroups(groupsData.items);
      } else {
        setGroups([]);
      }
    } catch (err) {
      console.error('Failed to load subdivision groups:', err);
      setError('Не удалось загрузить группы подразделения');
      setGroups([]);
    } finally {
      setLoading(false);
    }
  };

  const handleGroupClick = (group) => {
    setStudentsDialog({ open: true, group });
  };

  const handleStudentSave = async (studentData) => {
    try {
      if (studentData.id) {
        await studentsAPI.update(studentData.id, studentData);
      } else {
        await studentsAPI.create(studentData);
      }
      // Обновляем список групп для обновления счетчиков
      await fetchGroups();
    } catch (err) {
      throw err;
    }
  };

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box>
            <Typography variant="h6">
              Группы подразделения: {subdivision?.name}
            </Typography>
            <Typography variant="subtitle2" color="text.secondary">
              Всего студентов: {subdivision?.students_count || 0} | 
              В профсоюзе: {subdivision?.active_students_count || 0} |
              Процент: {subdivision?.union_percentage || 0}%
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
                    <TableCell>Название</TableCell>
                    <TableCell>Год</TableCell>
                    <TableCell>Студентов</TableCell>
                    <TableCell>В профсоюзе</TableCell>
                    <TableCell align="right">Действия</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {groups.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        В подразделении нет групп
                      </TableCell>
                    </TableRow>
                  ) : (
                    groups.map((group) => (
                      <TableRow 
                        key={group.id}
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => handleGroupClick(group)}
                      >
                        <TableCell>{group.name}</TableCell>
                        <TableCell>{group.year}</TableCell>
                        <TableCell>{group.students_count || 0}</TableCell>
                        <TableCell>{group.active_students_count || 0}</TableCell>
                        <TableCell align="right">
                          <IconButton
                            color="info"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleGroupClick(group);
                            }}
                            title="Посмотреть студентов"
                            size="small"
                          >
                            <VisibilityIcon />
                          </IconButton>
                          {hasPermission('canManageGroups') && (
                            <IconButton
                              color="primary"
                              title="Редактировать группу"
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
            Всего групп: {groups.length}
          </Typography>
          <Button onClick={onClose}>Закрыть</Button>
        </DialogActions>
      </Dialog>

      {/* Модальное окно студентов группы */}
      <GroupStudentsModal
        open={studentsDialog.open}
        group={studentsDialog.group}
        onClose={() => setStudentsDialog({ open: false, group: null })}
        onStudentSave={handleStudentSave}
      />
    </>
  );
};

export default SubdivisionGroupsModal;