import React, { useState, useEffect } from 'react';
import {
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Box,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import { groupsAPI } from '../services/api';

const StudentForm = ({ data, onSubmit }) => {
  const [formData, setFormData] = useState({
    group_id: '',
    full_name: '',
    is_active: false,
    is_budget: true,
    year: new Date().getFullYear(),
  });

  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchGroups();
  }, []);

  useEffect(() => {
    if (data) {
      setFormData({
        group_id: data.group_id || data.groupid || '',
        full_name: data.full_name || data.fullname || '',
        is_active: data.is_active || data.isactive || false,
        is_budget: data.is_budget || data.isbudget || true,
        year: data.year || new Date().getFullYear(),
      });
    }
  }, [data]);

  const fetchGroups = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await groupsAPI.getAll();
      const groupsData = response.data;
      
      if (groupsData && groupsData.items) {
        setGroups(groupsData.items);
      } else if (Array.isArray(groupsData)) {
        setGroups(groupsData);
      } else {
        console.error('Unexpected groups data format:', groupsData);
        setGroups([]);
        setError('Не удалось загрузить группы');
      }
    } catch (err) {
      console.error('Failed to load groups:', err);
      setError('Не удалось загрузить группы');
      setGroups([]);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (event) => {
    const { name, value, checked } = event.target;
    if (name === 'is_active' || name === 'is_budget') {
      setFormData(prev => ({
        ...prev,
        [name]: checked,
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <FormControl fullWidth>
            <InputLabel>Group</InputLabel>
            <Select
              name="group_id"
              value={formData.group_id}
              onChange={handleChange}
              label="Group"
              required
              disabled={loading}
            >
              {loading ? (
                <MenuItem disabled>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Loading groups...
                </MenuItem>
              ) : groups.length === 0 ? (
                <MenuItem disabled>No groups available</MenuItem>
              ) : (
                groups.map((group) => (
                  <MenuItem key={group.id} value={group.id}>
                    {group.name} ({group.subdivision_name}) - {group.year}
                  </MenuItem>
                ))
              )}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Full Name"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            required
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControlLabel
            control={
              <Switch
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
              />
            }
            label="Active"
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControlLabel
            control={
              <Switch
                name="is_budget"
                checked={formData.is_budget}
                onChange={handleChange}
              />
            }
            label="Budget"
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Year"
            name="year"
            type="number"
            value={formData.year}
            onChange={handleChange}
            required
          />
        </Grid>

        <Grid item xs={12}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
          >
            Save
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
};

export default StudentForm;