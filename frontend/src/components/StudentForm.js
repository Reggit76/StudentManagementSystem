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
} from '@mui/material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';

const StudentForm = ({ data, groups, onSubmit }) => {
  const [formData, setFormData] = useState({
    GroupID: '',
    FullName: '',
    IsActive: false,
    IsBudget: true,
    Year: new Date().getFullYear(),
    Data: {
      Phone: '',
      Email: '',
      Birthday: null,
    },
  });

  useEffect(() => {
    if (data) {
      setFormData({
        ...data,
        Data: {
          ...data.Data,
          Birthday: data.Data?.Birthday ? new Date(data.Data.Birthday) : null,
        },
      });
    }
  }, [data]);

  const handleChange = (event) => {
    const { name, value, checked } = event.target;
    if (name === 'IsActive' || name === 'IsBudget') {
      setFormData(prev => ({
        ...prev,
        [name]: checked,
      }));
    } else if (name.startsWith('Data.')) {
      const field = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        Data: {
          ...prev.Data,
          [field]: value,
        },
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
              name="GroupID"
              value={formData.GroupID}
              onChange={handleChange}
              label="Group"
              required
            >
              {groups.map((group) => (
                <MenuItem key={group.ID} value={group.ID}>
                  {group.Name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Full Name"
            name="FullName"
            value={formData.FullName}
            onChange={handleChange}
            required
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControlLabel
            control={
              <Switch
                name="IsActive"
                checked={formData.IsActive}
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
                name="IsBudget"
                checked={formData.IsBudget}
                onChange={handleChange}
              />
            }
            label="Budget"
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Phone"
            name="Data.Phone"
            value={formData.Data.Phone}
            onChange={handleChange}
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Email"
            name="Data.Email"
            type="email"
            value={formData.Data.Email}
            onChange={handleChange}
          />
        </Grid>

        <Grid item xs={12}>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DatePicker
              label="Birthday"
              value={formData.Data.Birthday}
              onChange={(newValue) => {
                setFormData(prev => ({
                  ...prev,
                  Data: {
                    ...prev.Data,
                    Birthday: newValue,
                  },
                }));
              }}
              renderInput={(params) => (
                <TextField {...params} fullWidth name="Data.Birthday" />
              )}
            />
          </LocalizationProvider>
        </Grid>
      </Grid>
    </Box>
  );
};

export default StudentForm; 