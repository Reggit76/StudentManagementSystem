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
  Chip,
  Grid,
  FormHelperText,
  OutlinedInput,
  Checkbox,
  ListItemText,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import InputAdornment from '@mui/material/InputAdornment';
import { usersAPI, rolesAPI, subdivisionsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Users = () => {
  const { hasPermission } = useAuth();
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [subdivisions, setSubdivisions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });

  useEffect(() => {
    if (hasPermission('canManageUsers')) {
      fetchUsers();
      fetchRoles();
      fetchSubdivisions();
    }
  }, [hasPermission]);

  const fetchUsers = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await usersAPI.getAll();
      const usersData = response.data;
      
      if (usersData && usersData.items) {
        setUsers(usersData.items);
      } else if (Array.isArray(usersData)) {
        setUsers(usersData);
      } else {
        console.error('Unexpected users data format:', usersData);
        setUsers([]);
        setError('Некорректный формат данных пользователей');
      }
    } catch (err) {
      console.error('Failed to load users:', err);
      setError('Не удалось загрузить пользователей');
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await rolesAPI.getAll();
      setRoles(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error('Failed to load roles:', err);
      setRoles([]);
    }
  };

  const fetchSubdivisions = async () => {
    try {
      const response = await subdivisionsAPI.getAll();
      const subdivisionsData = response.data;
      
      if (subdivisionsData && subdivisionsData.items) {
        setSubdivisions(subdivisionsData.items);
      } else if (Array.isArray(subdivisionsData)) {
        setSubdivisions(subdivisionsData);
      } else {
        setSubdivisions([]);
      }
    } catch (err) {
      console.error('Failed to load subdivisions:', err);
      setSubdivisions([]);
    }
  };

  const handleAddUser = () => {
    setDialog({
      open: true,
      type: 'add',
      data: {
        login: '',
        password: '',
        subdivisionid: '',
        role_ids: [],
      },
    });
  };

  const handleEditUser = (user) => {
    setDialog({
      open: true,
      type: 'edit',
      data: {
        ...user,
        password: '',
        role_ids: user.roles ? user.roles.map(role => role.id) : [],
      },
    });
  };

  const handleDeleteUser = async (id, login) => {
    if (login === 'admin') {
      setError('Нельзя удалить главного администратора');
      return;
    }

    if (window.confirm('Вы уверены, что хотите удалить этого пользователя?')) {
      try {
        await usersAPI.delete(id);
        fetchUsers();
      } catch (err) {
        console.error('Failed to delete user:', err);
        setError('Не удалось удалить пользователя');
      }
    }
  };

  const handleDialogClose = () => {
    setDialog({ open: false, type: null, data: null });
    setError('');
  };

  const handleDialogSave = async () => {
    try {
      // Валидация
      if (!dialog.data.login.trim()) {
        setError('Логин обязателен');
        return;
      }

      if (dialog.type === 'add' && !dialog.data.password.trim()) {
        setError('Пароль обязателен');
        return;
      }

      if (dialog.data.role_ids.length === 0) {
        setError('Необходимо выбрать хотя бы одну роль');
        return;
      }

      if (dialog.type === 'add') {
        await usersAPI.create(dialog.data);
      } else {
        const updateData = { ...dialog.data };
        if (!updateData.password) {
          delete updateData.password; // Не обновляем пароль, если он пустой
        }
        await usersAPI.update(dialog.data.id, updateData);
      }

      handleDialogClose();
      fetchUsers();
    } catch (err) {
      console.error('Failed to save user:', err);
      setError('Не удалось сохранить пользователя: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setDialog(prev => ({
      ...prev,
      data: { ...prev.data, [name]: value },
    }));
  };

  const handleRoleChange = (event) => {
    const { value } = event.target;
    setDialog(prev => ({
      ...prev,
      data: { ...prev.data, role_ids: typeof value === 'string' ? value.split(',') : value },
    }));
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

  const filteredUsers = users.filter(user =>
    user.login.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!hasPermission('canManageUsers')) {
    return (
      <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
        <Alert severity="error">
          У вас нет прав для просмотра этой страницы
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Управление пользователями
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            size="small"
            placeholder="Поиск пользователей..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleAddUser}
          >
            Добавить пользователя
          </Button>
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
              <TableCell>Логин</TableCell>
              <TableCell>Подразделение</TableCell>
              <TableCell>Роли</TableCell>
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
            ) : filteredUsers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  Пользователи не найдены
                </TableCell>
              </TableRow>
            ) : (
              filteredUsers.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.login}</TableCell>
                  <TableCell>{user.subdivision_name || 'Все подразделения'}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {user.roles && user.roles.map((role) => (
                        <Chip
                          key={role.id}
                          label={getRoleDisplayName(role.name)}
                          size="small"
                          color="primary"
                        />
                      ))}
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      color="primary"
                      onClick={() => handleEditUser(user)}
                    >
                      <EditIcon />
                    </IconButton>
                    {user.login !== 'admin' && (
                      <IconButton
                        color="error"
                        onClick={() => handleDeleteUser(user.id, user.login)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Диалог создания/редактирования пользователя */}
      <Dialog open={dialog.open} onClose={handleDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialog.type === 'add' ? 'Добавить пользователя' : 'Редактировать пользователя'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Логин"
                  name="login"
                  value={dialog.data?.login || ''}
                  onChange={handleInputChange}
                  required
                  disabled={dialog.type === 'edit'}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label={dialog.type === 'add' ? 'Пароль' : 'Новый пароль (оставьте пустым, чтобы не менять)'}
                  name="password"
                  type="password"
                  value={dialog.data?.password || ''}
                  onChange={handleInputChange}
                  required={dialog.type === 'add'}
                />
              </Grid>

              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Подразделение</InputLabel>
                  <Select
                    name="subdivisionid"
                    value={dialog.data?.subdivisionid || ''}
                    onChange={handleInputChange}
                    label="Подразделение"
                  >
                    <MenuItem value="">Все подразделения</MenuItem>
                    {subdivisions.map((subdivision) => (
                      <MenuItem key={subdivision.id} value={subdivision.id}>
                        {subdivision.name}
                      </MenuItem>
                    ))}
                  </Select>
                  <FormHelperText>
                    Оставьте пустым для доступа ко всем подразделениям
                  </FormHelperText>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <FormControl fullWidth required>
                  <InputLabel>Роли</InputLabel>
                  <Select
                    multiple
                    name="role_ids"
                    value={dialog.data?.role_ids || []}
                    onChange={handleRoleChange}
                    input={<OutlinedInput label="Роли" />}
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => {
                          const role = roles.find(r => r.id === value);
                          return (
                            <Chip
                              key={value}
                              label={getRoleDisplayName(role?.name || '')}
                              size="small"
                            />
                          );
                        })}
                      </Box>
                    )}
                  >
                    {roles.map((role) => (
                      <MenuItem key={role.id} value={role.id}>
                        <Checkbox checked={(dialog.data?.role_ids || []).indexOf(role.id) > -1} />
                        <ListItemText primary={getRoleDisplayName(role.name)} />
                      </MenuItem>
                    ))}
                  </Select>
                  <FormHelperText>
                    Выберите одну или несколько ролей для пользователя
                  </FormHelperText>
                </FormControl>
              </Grid>
            </Grid>
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

export default Users;