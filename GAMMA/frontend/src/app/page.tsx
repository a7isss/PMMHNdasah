'use client';

import { Box, Container, Typography, Card, CardContent, Button, CircularProgress, Alert } from '@mui/material';
import { Construction, TrendingUp, WhatsApp, Assessment, Login } from '@mui/icons-material';
import { useGetProjectsQuery } from '@/lib/api/projectsApi';
import { useAppSelector } from '@/lib/hooks';
import Link from 'next/link';

export default function Dashboard() {
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const { data: projects, isLoading, error } = useGetProjectsQuery({}, {
    skip: !isAuthenticated, // Only fetch if authenticated
  });

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Construction sx={{ fontSize: 64, color: 'primary.main', mb: 3 }} />
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Welcome to Hndasah PM
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
            AI-powered civil engineering project management with WhatsApp integration
          </Typography>
          <Button
            component={Link}
            href="/login"
            variant="contained"
            size="large"
            startIcon={<Login />}
            sx={{ px: 4, py: 1.5 }}
          >
            Sign In to Continue
          </Button>
        </Box>
      </Container>
    );
  }

  if (isLoading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress size={48} sx={{ my: 4 }} />
        <Typography variant="h6" color="text.secondary">
          Loading dashboard...
        </Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 4 }}>
          Failed to load dashboard data. Please try again later.
        </Alert>
      </Container>
    );
  }

  const activeProjects = projects?.filter((p: any) => p.status === 'active') || [];
  const onTimeProjects = projects?.filter((p: any) => p.progressPercentage >= 80) || [];

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Welcome back, {user?.firstName || user?.email}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          AI-powered civil engineering project management with WhatsApp integration
        </Typography>
      </Box>

      {/* Quick Stats */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Card sx={{ minWidth: 250, flex: 1 }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={1}>
              <Construction color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Active Projects</Typography>
            </Box>
            <Typography variant="h4" fontWeight="bold">{activeProjects.length}</Typography>
            <Typography variant="body2" color="text.secondary">
              Currently in progress
            </Typography>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 250, flex: 1 }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={1}>
              <TrendingUp color="secondary" sx={{ mr: 1 }} />
              <Typography variant="h6">On-Time Delivery</Typography>
            </Box>
            <Typography variant="h4" fontWeight="bold">
              {projects && projects.length > 0
                ? Math.round((onTimeProjects.length / projects.length) * 100)
                : 0}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Projects on track
            </Typography>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 250, flex: 1 }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={1}>
              <WhatsApp sx={{ mr: 1, color: '#25D366' }} />
              <Typography variant="h6">Total Projects</Typography>
            </Box>
            <Typography variant="h4" fontWeight="bold">{projects?.length || 0}</Typography>
            <Typography variant="body2" color="text.secondary">
              Across all statuses
            </Typography>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 250, flex: 1 }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={1}>
              <Assessment color="warning" sx={{ mr: 1 }} />
              <Typography variant="h6">Avg. Health Score</Typography>
            </Box>
            <Typography variant="h4" fontWeight="bold">
              {projects && projects.length > 0
                ? Math.round(projects.reduce((sum: number, p: any) => sum + (p.healthScore || 0), 0) / projects.length)
                : 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Project health rating
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Main Content */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 3 }}>
        {/* Recent Projects */}
        <Card sx={{ flex: '2 1 500px' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Recent Projects
            </Typography>
            <Box sx={{ mb: 2 }}>
              {projects && projects.length > 0 ? (
                projects.slice(0, 3).map((project: any) => (
                  <Typography key={project.id} variant="body2" color="text.secondary" gutterBottom>
                    {project.name} - {project.status} ({project.progressPercentage}% complete)
                  </Typography>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No projects found. Create your first project to get started.
                </Typography>
              )}
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button variant="outlined" size="small">
                View All Projects
              </Button>
              <Button
                variant="contained"
                size="small"
                component={Link}
                href="/projects/create"
              >
                Create New Project
              </Button>
            </Box>
          </CardContent>
        </Card>

        {/* AI Insights */}
        <Card sx={{ flex: '1 1 300px' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              AI Insights
            </Typography>
            <Box sx={{ mb: 2 }}>
              {projects && projects.some((p: any) => (p.healthScore || 0) < 70) ? (
                projects
                  .filter((p: any) => (p.healthScore || 0) < 70)
                  .slice(0, 3)
                  .map((project: any) => (
                    <Typography key={project.id} variant="body2" sx={{ mb: 1 }}>
                      ⚠️ <strong>{project.name}:</strong> Health score needs attention ({project.healthScore})
                    </Typography>
                  ))
              ) : (
                <Typography variant="body2" sx={{ mb: 1 }}>
                  ✅ <strong>All projects:</strong> Performing well with good health scores
                </Typography>
              )}
            </Box>
            <Button variant="outlined" size="small">
              View All Insights
            </Button>
          </CardContent>
        </Card>
      </Box>

      {/* WhatsApp Activity */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom fontWeight="bold">
            WhatsApp Integration Ready
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>System Status:</strong> WhatsApp API integration configured and ready
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>AI Processing:</strong> Automatic message analysis and task creation enabled
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Real-time Updates:</strong> Live project communication via WhatsApp
            </Typography>
          </Box>
          <Button
            variant="outlined"
            size="small"
            component={Link}
            href="/whatsapp"
          >
            Open WhatsApp Interface
          </Button>
        </CardContent>
      </Card>

      {/* Footer */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Hndasah PM System v3.0 (Gamma) - AI-First Construction Project Management
        </Typography>
      </Box>
    </Container>
  );
}
