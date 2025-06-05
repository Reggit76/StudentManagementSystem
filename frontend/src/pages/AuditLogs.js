import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  TablePagination,
  Card,
  CardContent,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import ClearIcon from '@mui/icons-material/Clear';
import { auditLogsAPI, usersAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const AuditLogs = () => {
  const { hasPermission } = useAuth();
  const [logs, setLogs] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  
  const [filters, setFilters] = useState({
    user_id: '',
    action: '',
    table_name: '',
    date_from: '',
    date_to: '',
  });

  const actions = ['CREATE', 'UPDATE', 'DELETE', 'VIEW'];
  const tables = [
    'users', 'roles', 'subdivisions', 'groups', 
    'students', 'studentdata', 'contributions', 
    'hostelstudents', 'additionalstatuses'
  ];

  useEffect(() => {
    if (hasPermission('canViewAll')) {
      fetchLogs();
      fetchUsers();
    }
  }, [hasPermission, page, rowsPerPage]);

  const fetchLogs = async () => {
    setLoading(true);
    setError('');
    try {
      const params = {
        page: page + 1,
        size: rowsPerPage,
        ...Object.fromEntries(
          Object.entries(filters).filter(([_, value]) => value !== '')
        )
      };

      const response = await auditLogsAPI.getAll(params);
      const logsData = response.data;
      
      if (logsData && logsData.items) {
        setLogs(logsData.items);
        setTotal(logsData.total);
      } else {
        setLogs([]);
        setTotal(0);
      }
    } catch (err) {
      console.error('Failed to load audit logs:', err);
      setError('Не удалось загрузить логи аудита');
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await usersAPI.getAll();
      const usersData = response.data;
      
      if (usersData && usersData.items) {
        setUsers(usersData.items);
      } else if (Array.isArray(usersData)) {
        setUsers(usersData);
      }
    } catch (err) {
      console.error('Failed to load users:', err);
      setUsers([]);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSearch = () => {
    setPage(0);
    fetchLogs();
  };

  const handleClearFilters = () => {
    setFilters({
      user_id: '',
      action: '',
      table_name: '',
      date_from: '',
      date_to: '',
    });
    setPage(0);
  };

  const getActionColor = (action) => {
    switch (action) {
      case 'CREATE': return 'success';
      case 'UPDATE': return 'warning';
      case 'DELETE': return 'error';
      case 'VIEW': return 'info';
      default: return 'default';
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return '';
    try {
      return new Date(dateString).toLocaleString('ru-RU');
    } catch {
      return dateString;
    }
  };

  const getTableDisplayName = (tableName) => {
    const tableNames = {
      'users': 'Пользователи',
      'roles': 'Роли',
      'subdivisions': 'Подразделения',
      'groups': 'Группы',
      'students': 'Студенты',
      'studentdata': 'Данные студентов',
      'contributions': 'Взносы',
      'hostelstudents': 'Общежития',
      'additionalstatuses': 'Доп. статусы'
    };
    return tableNames[tableName] || tableName;
  };

  if (!hasPermission('canViewAll')) {
    return (
      <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
        <Alert severity="error">
          У вас нет прав для просмотра логов аудита
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Логи аудита
      </Typography>

      {/* Фильтры */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Пользователь</InputLabel>
                <Select
                  value={filters.user_id}
                  label="Пользователь"
                  onChange={(e) => handleFilterChange('user_id', e.target.value)}
                >
                  <MenuItem value="">Все пользователи</MenuItem>
                  {users.map((user) => (
                    <MenuItem key={user.id} value={user.id}>
                      {user.login}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Действие</InputLabel>
                <Select
                  value={filters.action}
                  label="Действие"
                  onChange={(e) => handleFilterChange('action', e.target.value)}
                >
                  <MenuItem value="">Все действия</MenuItem>
                  {actions.map((action) => (
                    <MenuItem key={action} value={action}>
                      {action}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Таблица</InputLabel>
                <Select
                  value={filters.table_name}
                  label="Таблица"
                  onChange={(e) => handleFilterChange('table_name', e.target.value)}
                >
                  <MenuItem value="">Все таблицы</MenuItem>
                  {tables.map((table) => (
                    <MenuItem key={table} value={table}>
                      {getTableDisplayName(table)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                size="small"
                label="Дата от"
                type="datetime-local"
                value={filters.date_from}
                onChange={(e) => handleFilterChange('date_from', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                size="small"
                label="Дата до"
                type="datetime-local"
                value={filters.date_to}
                onChange={(e) => handleFilterChange('date_to', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  onClick={handleSearch}
                  startIcon={<RefreshIcon />}
                  size="small"
                >
                  Поиск
                </Button>
                <Button
                  variant="outlined"
                  onClick={handleClearFilters}
                  startIcon={<ClearIcon />}
                  size="small"
                >
                  Очистить
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Таблица логов */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Дата и время</TableCell>
                <TableCell>Пользователь</TableCell>
                <TableCell>Действие</TableCell>
                <TableCell>Таблица</TableCell>
                <TableCell>ID записи</TableCell>
                <TableCell>IP адрес</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : logs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    Логи не найдены
                  </TableCell>
                </TableRow>
              ) : (
                logs.map((log) => (
                  <TableRow key={log.id} hover>
                    <TableCell>{formatDateTime(log.created_at)}</TableCell>
                    <TableCell>{log.user_login || 'Система'}</TableCell>
                    <TableCell>
                      <Chip
                        label={log.action}
                        color={getActionColor(log.action)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{getTableDisplayName(log.table_name)}</TableCell>
                    <TableCell>{log.record_id}</TableCell>
                    <TableCell>{log.ip_address || '-'}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={total}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(event, newPage) => setPage(newPage)}
          onRowsPerPageChange={(event) => {
            setRowsPerPage(parseInt(event.target.value, 10));
            setPage(0);
          }}
        />
      </Paper>
    </Container>
  );
};

export default AuditLogs;