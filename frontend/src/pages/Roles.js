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
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

const Roles = () => {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });

  // Моковые данные
  const mockRoles = [
    { id: 1, name: 'CHAIRMAN', created_at: new Date().toISOString() },
    { id: 2, name: 'DEPUTY_CHAIRMAN', created_at: new Date().toISOString() },
    { id: 3, name: 'DIVISION_HEAD', created_at: new Date().toISOString() },
    { id: 4, name: 'DORMITORY_HEAD', created_at: new Date().toISOString() },
  ];

  useEffect(() => {
    fetchRoles();
  }, []);

  const fetchRoles = async () => {
    setLoading(true);
    try {
      // TODO: Заменить на реальный API вызов
      setTimeout(() => {
        setRoles(mockRoles);
        setLoading(false);
      }, 500);
    } catch (err) {
      console.error('Failed to load roles:', err);
      setError('Не удалось загрузить роли');
      setRoles(mockRoles);
      setLoading(false);
    }
  };

  const getRoleDisplayName = (roleName) => {
    const roleNames = {
      'CHAIRMAN': 'Председатель профкома',
      'DEPUTY_CHAIRMAN': 'Заместитель председателя',
      'DIVISION_HEAD': 'Председатель подразделения',
      'DORMITORY_HEAD': 'Председатель общежития'
    };
    return roleNames[roleName] || roleName;
  };

  const isSystemRole = (roleName) => {
    return ['CHAIRMAN', 'DEPUTY_CHAIRMAN', 'DIVISION_HEAD', 'DORMITORY_HEAD'].includes(roleName);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Управление ролями
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => {/* TODO: Добавить создание ролей */}}
        >
          Добавить роль
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
              <TableCell>Название роли</TableCell>
              <TableCell>Системное название</TableCell>
              <TableCell>Тип</TableCell>
              <TableCell align="right">Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : roles.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  Роли не найдены
                </TableCell>
              </TableRow>
            ) : (
              roles.map((role) => (
                <TableRow key={role.id}>
                  <TableCell>{getRoleDisplayName(role.name)}</TableCell>
                  <TableCell>{role.name}</TableCell>
                  <TableCell>
                    {isSystemRole(role.name) ? 'Системная' : 'Пользовательская'}
                  </TableCell>
                  <TableCell align="right">
                    {!isSystemRole(role.name) && (
                      <>
                        <IconButton color="primary">
                          <EditIcon />
                        </IconButton>
                        <IconButton color="error">
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
    </Container>
  );
};

export default Roles;