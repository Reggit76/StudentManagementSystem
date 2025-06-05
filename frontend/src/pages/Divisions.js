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
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { subdivisionsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Divisions = () => {
  const { hasPermission } = useAuth();
  const [subdivisions, setSubdivisions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });

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
      } else if (Array.isArray(subdivisionsData)) {
        setSubdivisions(subdivisionsData);
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

  const handleAddSubdivision = () => {
    setDialog({
      open: true,
      type: 'add',
      data: { name: '' },
    });
  };

  const handleEditSubdivision = (subdivision) => {
    setDialog({
      open: true,
      type: 'edit',
      data: subdivision,
    });
  };

  const handleDeleteSubdivision = async (id) => {
    if (window.confirm('Вы уверены, что хотите удалить это подразделение?')) {
      try {
        await subdivisionsAPI.delete(id);
        fetchSubdivisions();
      } catch (err) {
        console.error('Failed to delete subdivision:', err);
        setError('Не удалось удалить подразделение');
      }
    }
  };

  const handleDialogClose = () => {
    setDialog({ open: false, type: null, data: null });
  };

  const handleDialogSave = async () => {
    try {
      if (dialog.type === 'add') {
        await subdivisionsAPI.create(dialog.data);
      } else {
        await subdivisionsAPI.update(dialog.data.id, dialog.data);
      }
      handleDialogClose();
      fetchSubdivisions();
    } catch (err) {
      console.error('Failed to save subdivision:', err);
      setError('Не удалось сохранить подразделение');
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
                <TableRow key={subdivision.id}>
                  <TableCell>{subdivision.name}</TableCell>
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
                    {hasPermission('canManageSubdivision') && (
                      <>
                        <IconButton
                          color="primary"
                          onClick={() => handleEditSubdivision(subdivision)}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          color="error"
                          onClick={() => handleDeleteSubdivision(subdivision.id)}
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

export default Divisions;