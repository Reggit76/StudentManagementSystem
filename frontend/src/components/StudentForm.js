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
} from '@mui/material';

const StudentForm = ({ data, groups, onSubmit }) => {
  const [formData, setFormData] = useState({
    group_id: '',
    full_name: '',
    is_active: false,
    is_budget: true,
    year: new Date().getFullYear(),
  });

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
            >
              {groups.map((group) => (
                <MenuItem key={group.id} value={group.id}>
                  {group.name}
                </MenuItem>
              ))}
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