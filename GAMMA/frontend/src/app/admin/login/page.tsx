'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Container,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  AdminPanelSettings,
  Login,
} from '@mui/icons-material';
import { useAppDispatch } from '@/lib/hooks';
import { setCredentials } from '@/features/auth/authSlice';

export default function AdminLoginPage() {
  const router = useRouter();
  const dispatch = useAppDispatch();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Use superadmin login endpoint
      const response = await fetch('/api/v1/auth/superadmin/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: formData.email,
          password: formData.password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const result = await response.json();

      dispatch(setCredentials({
        user: result.user,
        token: result.access_token,
      }));

      router.push('/admin');
    } catch (err: any) {
      setError(err.message || 'Superadmin login failed. Please try again.');
      console.error('Superadmin login failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="sm" sx={{ py: 8 }}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        {/* Logo/Brand */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <AdminPanelSettings sx={{ fontSize: 48, color: 'error.main', mb: 2 }} />
          <Typography component="h1" variant="h4" fontWeight="bold">
            Super Admin Access
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Secure administrative login for system management
          </Typography>
        </Box>

        {/* Login Form */}
        <Card sx={{ width: '100%', maxWidth: 400 }}>
          <CardContent sx={{ p: 4 }}>
            <Typography component="h2" variant="h5" gutterBottom textAlign="center">
              Super Admin Login
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="Superadmin Email"
                name="email"
                autoComplete="email"
                autoFocus
                value={formData.email}
                onChange={handleChange}
                disabled={isLoading}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Superadmin Password"
                type="password"
                id="password"
                autoComplete="current-password"
                value={formData.password}
                onChange={handleChange}
                disabled={isLoading}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                color="error"
                startIcon={<Login />}
                sx={{ mt: 3, mb: 2, py: 1.5 }}
                disabled={isLoading}
              >
                {isLoading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'Login as Super Admin'
                )}
              </Button>
            </Box>

            {/* Security Notice */}
            <Box sx={{ mt: 3, p: 2, bgcolor: 'error.50', borderRadius: 1 }}>
              <Typography variant="body2" color="error.main" sx={{ fontWeight: 'bold' }}>
                🔒 Security Notice:
              </Typography>
              <Typography variant="body2" color="error.main">
                This login provides unrestricted system access. Ensure you're authorized to use superadmin privileges.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
}
