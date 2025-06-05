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
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

const Contributions = () => {
  const [contributions, setContributions] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });

  useEffect(() => {
    fetchContributions();
    fetchStudents();
  }, []);

  const fetchContributions = async () => {
    setLoading(true);
    setError('');
    try {
      // Пока используем моковые данные, так как в БД пусто
      const mockContributions = [];
      setContributions(mockContributions);
    } catch (err) {
      console.error('Failed to load contributions:', err);
      setError('Не удалось загрузить данные о взносах');
      setContributions([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStudents = async () => {
    try {
      // TODO: Загрузить список студентов
      const mockStudents = [];
      setStudents(mockStudents);
    } catch (err) {
      console.error('Failed to load students:', err);
      setStudents([]);
    }
  };

  const handleAddContribution = () => {
    setDialog({
      open: true,
      type: 'add',
      data: {
        student_id: '',
        semester: 1,
        amount: '',
        payment_date: new Date().toISOString().split('T')[0],
        year: new Date().getFullYear(),
      },
    });
  };

  const handleEditContribution = (contribution) => {
    setDialog({
      open: true,
      type: 'edit',
      data: {
        ...contribution,
        payment_date: contribution.payment_date ? new Date(contribution.payment_date).toISOString().split('T')[0] : '',
      },
    });
  };

  const handleDeleteContribution = async (id) => {
    if (window.confirm('Вы уверены, что хотите удалить этот взнос?')) {
      try {
        // TODO: Реальное удаление
        setContributions(contributions.filter(c => c.id !== id));
      } catch (err) {
        setError('Не удалось удалить взнос');
      }
    }
  };

  const handleDialogClose = () => {
    setDialog({ open: false, type: null, data: null });
  };

  const handleDialogSave = async () => {
    try {
      // TODO: Реальное сохранение
      handleDialogClose();
      fetchContributions();
    } catch (err) {
      setError('Не удалось сохранить взнос');
    }
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setDialog(prev => ({
      ...prev,
      data: { ...prev.data, [name]: value },
    }));
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
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Студент</InputLabel>
                <Select
                  name="student_id"
                  value={dialog.data?.student_id || ''}
                  onChange={handleInputChange}
                  label="Студент"
                  required
                >
                  {students.map((student) => (
                    <MenuItem key={student.id} value={student.id}>
                      {student.full_name} ({student.group_name})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
            <TextField
              fullWidth
              label="Сумма взноса"
              name="amount"
              type="number"
              value={dialog.data?.amount || ''}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Семестр</InputLabel>
              <Select
                name="semester"
                value={dialog.data?.semester || 1}
                onChange={handleInputChange}
                label="Семестр"
                required
              >
                <MenuItem value={1}>1 семестр</MenuItem>
                <MenuItem value={2}>2 семестр</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Год"
              name="year"
              type="number"
              value={dialog.data?.year || new Date().getFullYear()}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Дата оплаты"
              name="payment_date"
              type="date"
              value={dialog.data?.payment_date || ''}
              onChange={handleInputChange}
              sx={{ mb: 2 }}
              InputLabelProps={{ shrink: true }}
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