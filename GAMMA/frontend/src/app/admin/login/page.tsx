'use client';

import { useState, useEffect } from 'react';
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
  Chip,
} from '@mui/material';
import {
  AdminPanelSettings,
  Security,
  Login,
} from '@mui/icons-material';
import { useLoginMutation } from '@/lib/api/authApi';
import { useAppDispatch } from '@/lib/hooks';
import { setCredentials } from '@/features/auth/authSlice';

export default function AdminLoginPage() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const [login, { isLoading, error }] = useLoginMutation();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [envCredentials, setEnvCredentials] = useState({
    email: '',
    password: '',
  });

  const [useEnvLogin, setUseEnvLogin] = useState(false);

  useEffect(() => {
    // Check for environment variables on client side
    const superadminEmail = process.env.NEXT_PUBLIC_SUPERADMIN_EMAIL;
    const superadminPassword = process.env.NEXT_PUBLIC_SUPERADMIN_PASSWORD;

    if (superadminEmail && superadminPassword) {
      setEnvCredentials({
        email: superadminEmail,
        password: superadminPassword,
      });
      setUseEnvLogin(true);
      setFormData({
        email: superadminEmail,
        password: superadminPassword,
      });
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
        throw new Error('Login failed');
      }

      const result = await response.json();

      dispatch(setCredentials({
        user: result.user,
        token: result.access_token,
      }));

      router.push('/admin');
    } catch (err) {
      // Error is handled by the API response
      console.error('Superadmin login failed:', err);
    }
  };

  const handleEnvLogin = async () => {
    if (!envCredentials.email || !envCredentials.password) {
      return;
    }

    try {
      const response = await fetch('/api/v1/auth/superadmin/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: envCredentials.email,
          password: envCredentials.password,
        }),
      });

      if (!response.ok) {
        throw new Error('Environment login failed');
      }

      const result = await response.json();

      dispatch(setCredentials({
        user: result.user,
        token: result.access_token,
      }));

      router.push('/admin');
    } catch (err) {
      console.error('Environment superadmin login failed:', err);
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

        {/* Environment Variables Status */}
        {useEnvLogin && (
          <Card sx={{ width: '100%', mb: 3, border: '2px solid', borderColor: 'success.main' }}>
            <CardContent sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Security sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6" color="success.main">
                  Environment Credentials Detected
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Superadmin credentials found in environment variables. You can login automatically or manually.
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={`Email: ${envCredentials.email}`}
                  variant="outlined"
                  color="success"
                  size="small"
                />
                <Chip
                  label="Password: [SECURE]"
                  variant="outlined"
                  color="success"
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        )}

        {/* Login Form */}
        <Card sx={{ width: '100%', maxWidth: 400 }}>
          <CardContent sx={{ p: 4 }}>
            <Typography component="h2" variant="h5" gutterBottom textAlign="center">
              Super Admin Login
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {'data' in error && error.data && typeof error.data === 'object' && 'detail' in error.data
                  ? (error.data as any).detail
                  : 'Superadmin login failed. Please try again.'}
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

              <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  color="error"
                  startIcon={<Login />}
                  sx={{ py: 1.5 }}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <CircularProgress size={24} color="inherit" />
                  ) : (
                    'Login as Super Admin'
                  )}
                </Button>

                {useEnvLogin && (
                  <Button
                    type="button"
                    fullWidth
                    variant="outlined"
                    color="success"
                    startIcon={<Security />}
                    onClick={handleEnvLogin}
                    sx={{ py: 1.5 }}
                    disabled={isLoading}
                  >
                    Auto Login (Environment)
                  </Button>
                )}
              </Box>
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
