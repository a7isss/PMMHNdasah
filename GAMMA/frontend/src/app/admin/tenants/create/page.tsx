'use client';

import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  TextField,
  Paper,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  ArrowBack,
  Save,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useAppSelector } from '@/lib/hooks';
import { useCreateTenantMutation } from '@/lib/api/adminApi';

export default function CreateTenant() {
  const router = useRouter();
  const user = useAppSelector((state) => state.auth.user);
  const [createTenant, { isLoading }] = useCreateTenantMutation();

  const [formData, setFormData] = useState({
    name: '',
    domain: '',
    subscription_plan: 'starter',
    contact_email: '',
    contact_phone: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Check if user is super admin
  if (user?.role !== 'super_admin') {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">
          Access denied. Super Admin privileges required.
        </Alert>
      </Container>
    );
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Tenant name is required';
    }

    if (!formData.subscription_plan) {
      newErrors.subscription_plan = 'Subscription plan is required';
    }

    if (formData.domain && !/^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$/.test(formData.domain)) {
      newErrors.domain = 'Domain must be a valid subdomain (letters, numbers, and hyphens only)';
    }

    if (formData.contact_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.contact_email)) {
      newErrors.contact_email = 'Please enter a valid email address';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      await createTenant({
        name: formData.name.trim(),
        domain: formData.domain.trim() || undefined,
        subscription_plan: formData.subscription_plan,
        contact_email: formData.contact_email.trim() || undefined,
        contact_phone: formData.contact_phone.trim() || undefined,
      }).unwrap();

      // Redirect to tenants list on success
      router.push('/admin/tenants');
    } catch (error: any) {
      console.error('Failed to create tenant:', error);
      // Handle specific error messages from the API
      if (error.data?.detail) {
        if (error.data.detail.includes('Domain already in use')) {
          setErrors({ domain: 'This domain is already in use' });
        } else {
          setErrors({ general: error.data.detail });
        }
      } else {
        setErrors({ general: 'Failed to create tenant. Please try again.' });
      }
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => router.push('/admin/tenants')}
            sx={{ mr: 2 }}
          >
            Back to Tenants
          </Button>
        </Box>
        <Typography variant="h4" component="h1" gutterBottom>
          Create New Tenant
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Set up a new company/organization in the system
        </Typography>
      </Box>

      {/* Form */}
      <Paper sx={{ p: 4 }}>
        <form onSubmit={handleSubmit}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* General Error */}
            {errors.general && (
              <Alert severity="error">{errors.general}</Alert>
            )}

            {/* Tenant Name */}
            <TextField
              label="Tenant Name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              error={!!errors.name}
              helperText={errors.name}
              fullWidth
              required
              placeholder="Enter company or organization name"
            />

            {/* Domain */}
            <TextField
              label="Custom Domain (Optional)"
              value={formData.domain}
              onChange={(e) => handleInputChange('domain', e.target.value)}
              error={!!errors.domain}
              helperText={errors.domain || 'Custom subdomain for tenant (e.g., company-name)'}
              fullWidth
              placeholder="company-name"
            />

            {/* Subscription Plan */}
            <TextField
              select
              label="Subscription Plan"
              value={formData.subscription_plan}
              onChange={(e) => handleInputChange('subscription_plan', e.target.value)}
              error={!!errors.subscription_plan}
              helperText={errors.subscription_plan}
              fullWidth
              required
              SelectProps={{ native: true }}
            >
              <option value="free">Free</option>
              <option value="starter">Starter</option>
              <option value="professional">Professional</option>
              <option value="enterprise">Enterprise</option>
            </TextField>

            {/* Contact Information */}
            <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
              Contact Information (Optional)
            </Typography>

            <TextField
              label="Contact Email"
              type="email"
              value={formData.contact_email}
              onChange={(e) => handleInputChange('contact_email', e.target.value)}
              error={!!errors.contact_email}
              helperText={errors.contact_email}
              fullWidth
              placeholder="contact@company.com"
            />

            <TextField
              label="Contact Phone"
              value={formData.contact_phone}
              onChange={(e) => handleInputChange('contact_phone', e.target.value)}
              fullWidth
              placeholder="+1 (555) 123-4567"
            />

            {/* Actions */}
            <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
              <Button
                type="button"
                variant="outlined"
                onClick={() => router.push('/admin/tenants')}
                fullWidth
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                startIcon={isLoading ? <CircularProgress size={20} /> : <Save />}
                disabled={isLoading}
                fullWidth
              >
                {isLoading ? 'Creating...' : 'Create Tenant'}
              </Button>
            </Box>
          </Box>
        </form>
      </Paper>

      {/* Information */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>Note:</strong> After creating the tenant, you can add users to it from the tenant management page.
          The tenant will be created as active by default.
        </Typography>
      </Alert>
    </Container>
  );
}
