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
  Autocomplete,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import api from '../services/api';

const Contributions = () => {
  const [contributions, setContributions] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);

  useEffect(() => {
    fetchContributions();
  }, []);

  const fetchContributions = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/contributions');
      if (response.data && Array.isArray(response.data.items)) {
        setContributions(response.data.items);
      } else {
        setContributions([]);
      }
    } catch (err) {
      console.error('Failed to load contributions:', err);
      setError(err.response?.data?.detail || 'Не удалось загрузить данные о взносах');
      setContributions([]);
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

  const handleAddContribution = () => {
    setDialog({
      open: true,
      type: 'add',
      data: {
        studentid: '',
        semester: 1,
        amount: '',
        paymentdate: '',
        year: new Date().getFullYear(),
      },
    });
    setSelectedStudent(null);
  };

  const handleEditContribution = (contribution) => {
    setDialog({
      open: true,
      type: 'edit',
      data: {
        ...contribution,
        paymentdate: contribution.paymentdate || '',
      },
    });
  };

  const handleDeleteContribution = async (id) => {
    if (window.confirm('Вы уверены, что хотите удалить этот взнос?')) {
      try {
        await api.delete(`/contributions/${id}`);
        await fetchContributions();
      } catch (err) {
        setError('Не удалось удалить взнос');
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
        await api.post('/contributions', data);
      } else {
        await api.put(`/contributions/${dialog.data.id}`, data);
      }

      handleDialogClose();
      await fetchContributions();
    } catch (err) {
      console.error('Failed to save contribution:', err);
      const errorMessage = err.response?.data?.detail || 'Не удалось сохранить взнос';
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

  const formatDate = (dateString) => {
    if (!dateString) return 'Не указана';
    try {
      return new Date(dateString).toLocaleDateString('ru-RU');
    } catch {
      return 'Некорректная дата';
    }
  };

  const formatAmount = (amount) => {
    if (!amount) return '0';
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB'
    }).format(amount);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Взносы студентов
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleAddContribution}
        >
          Добавить взнос
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
              <TableCell>Сумма</TableCell>
              <TableCell>Дата оплаты</TableCell>
              <TableCell>Семестр</TableCell>
              <TableCell>Год</TableCell>
              <TableCell>Статус</TableCell>
              <TableCell align="right">Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : contributions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  Нет данных о взносах
                </TableCell>
              </TableRow>
            ) : (
              contributions.map((contribution) => (
                <TableRow key={contribution.id}>
                  <TableCell>{contribution.student_name}</TableCell>
                  <TableCell>{contribution.group_name}</TableCell>
                  <TableCell>{formatAmount(contribution.amount)}</TableCell>
                  <TableCell>{formatDate(contribution.payment_date)}</TableCell>
                  <TableCell>{contribution.semester}</TableCell>
                  <TableCell>{contribution.year}</TableCell>
                  <TableCell>
                    <Chip
                      label={contribution.payment_date ? 'Оплачен' : 'Не оплачен'}
                      color={contribution.payment_date ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      color="primary"
                      onClick={() => handleEditContribution(contribution)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      color="error"
                      onClick={() => handleDeleteContribution(contribution.id)}
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
          {dialog.type === 'add' ? 'Добавить взнос' : 'Редактировать взнос'}
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
              <InputLabel>Семестр</InputLabel>
              <Select
                value={dialog.data?.semester || 1}
                onChange={(e) => setDialog(prev => ({
                  ...prev,
                  data: { ...prev.data, semester: e.target.value }
                }))}
                label="Семестр"
                required
              >
                <MenuItem value={1}>1 семестр</MenuItem>
                <MenuItem value={2}>2 семестр</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Сумма взноса"
              type="number"
              value={dialog.data?.amount || ''}
              onChange={(e) => setDialog(prev => ({
                ...prev,
                data: { ...prev.data, amount: e.target.value }
              }))}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Дата оплаты"
              type="date"
              value={dialog.data?.paymentdate || ''}
              onChange={(e) => setDialog(prev => ({
                ...prev,
                data: { ...prev.data, paymentdate: e.target.value }
              }))}
              InputLabelProps={{
                shrink: true,
              }}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Год"
              type="number"
              value={dialog.data?.year || new Date().getFullYear()}
              onChange={(e) => setDialog(prev => ({
                ...prev,
                data: { ...prev.data, year: e.target.value }
              }))}
              required
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

export default Contributions;