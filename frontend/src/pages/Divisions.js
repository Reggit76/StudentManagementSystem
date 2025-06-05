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
  CircularProgress,
  Chip,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import VisibilityIcon from '@mui/icons-material/Visibility';
import GroupsIcon from '@mui/icons-material/Groups';
import { subdivisionsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import SubdivisionGroupsModal from '../components/SubdivisionGroupsModal';

const Divisions = () => {
  const { hasPermission } = useAuth();
  const [subdivisions, setSubdivisions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });
  const [groupsDialog, setGroupsDialog] = useState({ open: false, subdivision: null });
  const [totalStats, setTotalStats] = useState({
    totalSubdivisions: 0,
    totalGroups: 0,
    totalStudents: 0,
    totalActiveStudents: 0,
    averageUnionPercentage: 0,
  });

  useEffect(() => {
    fetchSubdivisions();
  }, []);

  const fetchSubdivisions = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await subdivisionsAPI.getAll();
      const subdivisionsData = response.data;
      
      if (subdivisionsData && subdivisionsData.items) {
        setSubdivisions(subdivisionsData.items);
        calculateTotalStats(subdivisionsData.items);
      } else if (Array.isArray(subdivisionsData)) {
        setSubdivisions(subdivisionsData);
        calculateTotalStats(subdivisionsData);
      } else {
        console.error('Unexpected subdivisions data format:', subdivisionsData);
        setSubdivisions([]);
        setError('Некорректный формат данных подразделений');
      }
    } catch (err) {
      console.error('Failed to load subdivisions:', err);
      setError('Не удалось загрузить подразделения');
      setSubdivisions([]);
    } finally {
      setLoading(false);
    }
  };

  const calculateTotalStats = (data) => {
    const stats = data.reduce((acc, subdivision) => {
      acc.totalGroups += subdivision.groups_count || 0;
      acc.totalStudents += subdivision.students_count || 0;
      acc.totalActiveStudents += subdivision.active_students_count || 0;
      return acc;
    }, {
      totalSubdivisions: data.length,
      totalGroups: 0,
      totalStudents: 0,
      totalActiveStudents: 0,
    });

    stats.averageUnionPercentage = stats.totalStudents > 0 
      ? Math.round((stats.totalActiveStudents / stats.totalStudents) * 100)
      : 0;

    setTotalStats(stats);
  };

  const handleAddSubdivision = () => {
    setDialog({
      open: true,
      type: 'add',
      data: { name: '' },
    });
  };

  const handleEditSubdivision = (subdivision, event) => {
    event.stopPropagation(); // Предотвращаем открытие модалки групп
    setDialog({
      open: true,
      type: 'edit',
      data: subdivision,
    });
  };

  const handleDeleteSubdivision = async (id, event) => {
    event.stopPropagation(); // Предотвращаем открытие модалки групп
    if (window.confirm('Вы уверены, что хотите удалить это подразделение? Это приведет к удалению всех связанных данных!')) {
      try {
        await subdivisionsAPI.delete(id);
        fetchSubdivisions();
      } catch (err) {
        console.error('Failed to delete subdivision:', err);
        setError('Не удалось удалить подразделение: ' + (err.response?.data?.detail || err.message));
      }
    }
  };

  const handleRowClick = (subdivision) => {
    setGroupsDialog({ open: true, subdivision });
  };

  const handleDialogClose = () => {
    setDialog({ open: false, type: null, data: null });
    setError('');
  };

  const handleDialogSave = async () => {
    try {
      // Валидация
      if (!dialog.data.name.trim()) {
        setError('Название подразделения обязательно');
        return;
      }

      if (dialog.type === 'add') {
        await subdivisionsAPI.create(dialog.data);
      } else {
        await subdivisionsAPI.update(dialog.data.id, dialog.data);
      }
      handleDialogClose();
      fetchSubdivisions();
    } catch (err) {
      console.error('Failed to save subdivision:', err);
      setError('Не удалось сохранить подразделение: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setDialog(prev => ({
      ...prev,
      data: { ...prev.data, [name]: value },
    }));
  };

  const getUnionPercentageColor = (percentage) => {
    if (percentage >= 70) return 'success';
    if (percentage >= 50) return 'warning';
    return 'error';
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Подразделения
        </Typography>
        {hasPermission('canManageSubdivision') && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleAddSubdivision}
          >
            Добавить подразделение
          </Button>
        )}
      </Box>

      {/* Общая статистика */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Всего подразделений
              </Typography>
              <Typography variant="h5" component="div">
                {totalStats.totalSubdivisions}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Всего групп
              </Typography>
              <Typography variant="h5" component="div">
                {totalStats.totalGroups}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Всего студентов
              </Typography>
              <Typography variant="h5" component="div">
                {totalStats.totalStudents}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                В профсоюзе
              </Typography>
              <Typography variant="h5" component="div">
                {totalStats.totalActiveStudents}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {totalStats.averageUnionPercentage}% от общего числа
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Название</TableCell>
              <TableCell>Количество групп</TableCell>
              <TableCell>Количество студентов</TableCell>
              <TableCell>В профсоюзе</TableCell>
              <TableCell>% в профсоюзе</TableCell>
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
            ) : subdivisions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  Подразделения не найдены
                </TableCell>
              </TableRow>
            ) : (
              subdivisions.map((subdivision) => (
                <TableRow 
                  key={subdivision.id}
                  hover
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    }
                  }}
                  onClick={() => handleRowClick(subdivision)}
                >
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <GroupsIcon sx={{ mr: 1, color: 'primary.main' }} />
                      {subdivision.name}
                    </Box>
                  </TableCell>
                  <TableCell>{subdivision.groups_count || 0}</TableCell>
                  <TableCell>{subdivision.students_count || 0}</TableCell>
                  <TableCell>{subdivision.active_students_count || 0}</TableCell>
                  <TableCell>
                    <Chip
                      label={`${subdivision.union_percentage || 0}%`}
                      color={getUnionPercentageColor(subdivision.union_percentage || 0)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      color="info"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRowClick(subdivision);
                      }}
                      title="Посмотреть группы"
                    >
                      <VisibilityIcon />
                    </IconButton>
                    {hasPermission('canManageSubdivision') && (
                      <>
                        <IconButton
                          color="primary"
                          onClick={(e) => handleEditSubdivision(subdivision, e)}
                          title="Редактировать"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          color="error"
                          onClick={(e) => handleDeleteSubdivision(subdivision.id, e)}
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

      {/* Диалог создания/редактирования подразделения */}
      <Dialog open={dialog.open} onClose={handleDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialog.type === 'add' ? 'Добавить подразделение' : 'Редактировать подразделение'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Название"
              name="name"
              value={dialog.data?.name || ''}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
              helperText="Введите полное название подразделения"
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

      {/* Модальное окно групп подразделения */}
      <SubdivisionGroupsModal
        open={groupsDialog.open}
        subdivision={groupsDialog.subdivision}
        onClose={() => {
          setGroupsDialog({ open: false, subdivision: null });
          // Обновляем данные после закрытия модального окна
          fetchSubdivisions();
        }}
      />
    </Container>
  );
};

export default Divisions;