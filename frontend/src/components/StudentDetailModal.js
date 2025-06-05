import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Typography,
  Divider,
  Chip,
  OutlinedInput,
  Checkbox,
  ListItemText,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Paper,
} from '@mui/material';
import { groupsAPI, subdivisionsAPI } from '../services/api';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`student-tabpanel-${index}`}
      aria-labelledby={`student-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const StudentDetailModal = ({ open, student, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    // Основные данные
    full_name: '',
    group_id: '',
    is_active: false,
    is_budget: true,
    year: new Date().getFullYear(),
    
    // Дополнительные данные
    phone: '',
    email: '',
    birthday: '',
    
    // Статусы
    additional_status_ids: [],
    
    // Общежитие
    hostel: '',
    room: '',
    hostel_comment: '',
  });

  const [groups, setGroups] = useState([]);
  const [subdivisions, setSubdivisions] = useState([]);
  const [additionalStatuses, setAdditionalStatuses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);

  // Моковые дополнительные статусы
  const mockStatuses = [
    { id: 1, name: 'Староста' },
    { id: 2, name: 'Профорг' },
    { id: 3, name: 'Культорг' },
    { id: 4, name: 'Спорторг' },
    { id: 5, name: 'Тьютор' },
  ];

  useEffect(() => {
    if (open) {
      fetchGroups();
      fetchSubdivisions();
      setAdditionalStatuses(mockStatuses);
      
      if (student) {
        setFormData({
          full_name: student.full_name || student.fullname || '',
          group_id: student.group_id || student.groupid || '',
          is_active: student.is_active || student.isactive || false,
          is_budget: student.is_budget || student.isbudget || true,
          year: student.year || new Date().getFullYear(),
          
          // Дополнительные данные из student_data
          phone: student.student_data?.phone || '',
          email: student.student_data?.email || '',
          birthday: student.student_data?.birthday || '',
          
          // Статусы
          additional_status_ids: student.additional_statuses?.map(s => s.id) || [],
          
          // Данные общежития
          hostel: student.hostel_info?.hostel || '',
          room: student.hostel_info?.room || '',
          hostel_comment: student.hostel_info?.comment || '',
        });
      }
    }
  }, [open, student]);

  const fetchGroups = async () => {
    try {
      const response = await groupsAPI.getAll();
      const groupsData = response.data;
      
      if (Array.isArray(groupsData)) {
        setGroups(groupsData);
      } else if (groupsData && groupsData.items) {
        setGroups(groupsData.items);
      }
    } catch (err) {
      console.error('Failed to load groups:', err);
      setGroups([]);
    }
  };

  const fetchSubdivisions = async () => {
    try {
      const response = await subdivisionsAPI.getAll();
      const subdivisionsData = response.data;
      
      if (Array.isArray(subdivisionsData)) {
        setSubdivisions(subdivisionsData);
      } else if (subdivisionsData && subdivisionsData.items) {
        setSubdivisions(subdivisionsData.items);
      }
    } catch (err) {
      console.error('Failed to load subdivisions:', err);
      setSubdivisions([]);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Валидация
      if (!formData.full_name.trim()) {
        setError('ФИО обязательно для заполнения');
        return;
      }
      
      if (!formData.group_id) {
        setError('Необходимо выбрать группу');
        return;
      }

      // Подготавливаем данные для сохранения
      const saveData = {
        full_name: formData.full_name,
        group_id: formData.group_id,
        is_active: formData.is_active,
        is_budget: formData.is_budget,
        year: formData.year,
        
        student_data: {
          phone: formData.phone,
          email: formData.email,
          birthday: formData.birthday || null,
        },
        
        additional_status_ids: formData.additional_status_ids,
        
        // Данные общежития (если заполнены)
        hostel_data: formData.hostel ? {
          hostel: formData.hostel,
          room: formData.room,
          comment: formData.hostel_comment,
        } : null,
      };

      await onSave(saveData);
      onClose();
    } catch (err) {
      console.error('Failed to save student:', err);
      setError('Не удалось сохранить данные студента');
    } finally {
      setLoading(false);
    }
  };

  const getSelectedGroup = () => {
    return groups.find(g => g.id === formData.group_id);
  };

  const getSelectedSubdivision = () => {
    const group = getSelectedGroup();
    return subdivisions.find(s => s.id === group?.subdivision_id);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {student ? 'Редактирование студента' : 'Добавление студента'}
      </DialogTitle>
      
      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label="Основные данные" />
            <Tab label="Контактная информация" />
            <Tab label="Статусы и роли" />
            <Tab label="Общежитие" />
          </Tabs>
        </Box>

        {error && (
          <Alert severity="error" sx={{ m: 2 }}>
            {error}
          </Alert>
        )}

        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="ФИО студента"
                value={formData.full_name}
                onChange={(e) => handleChange('full_name', e.target.value)}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Группа</InputLabel>
                <Select
                  value={formData.group_id}
                  onChange={(e) => handleChange('group_id', e.target.value)}
                  label="Группа"
                  required
                >
                  {groups.map((group) => (
                    <MenuItem key={group.id} value={group.id}>
                      {group.name} ({group.subdivision_name})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Год поступления"
                type="number"
                value={formData.year}
                onChange={(e) => handleChange('year', parseInt(e.target.value))}
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={(e) => handleChange('is_active', e.target.checked)}
                  />
                }
                label="Активный член профсоюза"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_budget}
                    onChange={(e) => handleChange('is_budget', e.target.checked)}
                  />
                }
                label="Бюджетное обучение"
              />
            </Grid>

            {getSelectedGroup() && (
              <Grid item xs={12}>
                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Информация о группе:
                  </Typography>
                  <Typography variant="body2">
                    <strong>Группа:</strong> {getSelectedGroup().name}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Подразделение:</strong> {getSelectedSubdivision()?.name || 'Не указано'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Год:</strong> {getSelectedGroup().year}
                  </Typography>
                </Paper>
              </Grid>
            )}
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Номер телефона"
                value={formData.phone}
                onChange={(e) => handleChange('phone', e.target.value)}
                placeholder="+7 (___) ___-__-__"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                placeholder="student@example.com"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Дата рождения"
                type="date"
                value={formData.birthday}
                onChange={(e) => handleChange('birthday', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Дополнительные статусы</InputLabel>
                <Select
                  multiple
                  value={formData.additional_status_ids}
                  onChange={(e) => handleChange('additional_status_ids', e.target.value)}
                  input={<OutlinedInput label="Дополнительные статусы" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => {
                        const status = additionalStatuses.find(s => s.id === value);
                        return (
                          <Chip
                            key={value}
                            label={status?.name || ''}
                            size="small"
                          />
                        );
                      })}
                    </Box>
                  )}
                >
                  {additionalStatuses.map((status) => (
                    <MenuItem key={status.id} value={status.id}>
                      <Checkbox checked={formData.additional_status_ids.indexOf(status.id) > -1} />
                      <ListItemText primary={status.name} />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Общежитие</InputLabel>
                <Select
                  value={formData.hostel}
                  onChange={(e) => handleChange('hostel', e.target.value)}
                  label="Общежитие"
                >
                  <MenuItem value="">Не проживает</MenuItem>
                  {Array.from({ length: 20 }, (_, i) => i + 1).map((num) => (
                    <MenuItem key={num} value={num}>
                      Общежитие №{num}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            {formData.hostel && (
              <>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Номер комнаты"
                    type="number"
                    value={formData.room}
                    onChange={(e) => handleChange('room', e.target.value)}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Комментарий"
                    multiline
                    rows={3}
                    value={formData.hostel_comment}
                    onChange={(e) => handleChange('hostel_comment', e.target.value)}
                    placeholder="Дополнительная информация о проживании"
                  />
                </Grid>
              </>
            )}
          </Grid>
        </TabPanel>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Отмена
        </Button>
        <Button 
          onClick={handleSave} 
          color="primary" 
          variant="contained"
          disabled={loading}
        >
          {loading ? <CircularProgress size={20} /> : 'Сохранить'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default StudentDetailModal;